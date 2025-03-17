import os
import openai as ai
from helpers.logging_config import logger  # Import the logger
from helpers import helpers
import numpy as np
import pandas as pd

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

logger.info("Starting the script...")
client = helpers.get_azure_openai_client()
# Check if environment variables are loaded correctly
if not helpers.is_env_loaded():
    logger.error("Environment variables are not loaded correctly.")
    raise EnvironmentError("Environment variables are not loaded correctly.")

SIMILARITIES_RESULTS_THRESHOLD = 0.75
DATASET_NAME = "embedding_index_3m.json"
import os

# Get the directory of the current module
current_module_directory = os.path.dirname(os.path.abspath(__file__))
dataset_path = os.path.join(current_module_directory, "..\\", DATASET_NAME)

def load_dataset(source: str) -> pd.core.frame.DataFrame:
    # Load the video session index
    pd_vectors = pd.read_json(source)
    return pd_vectors.drop(columns=["text"], errors="ignore").fillna("")

def cosine_similarity(a, b):
    if len(a) > len(b):
        b = np.pad(b, (0, len(a) - len(b)), 'constant')
    elif len(b) > len(a):
        a = np.pad(a, (0, len(b) - len(a)), 'constant')
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def get_videos(query: str, dataset: pd.core.frame.DataFrame, rows: int) -> pd.core.frame.DataFrame:
    # create a copy of the dataset
    video_vectors = dataset.copy()

    # get the embeddings for the query    
    query_embeddings = client.client.embeddings.create(input=query, model=client.embeddings_deployment).data[0].embedding

    # create a new column with the calculated similarity for each row
    video_vectors["similarity"] = video_vectors["ada_v2"].apply(
        lambda x: cosine_similarity(np.array(query_embeddings), np.array(x))
    )

    # filter the videos by similarity
    mask = video_vectors["similarity"] >= SIMILARITIES_RESULTS_THRESHOLD
    video_vectors = video_vectors[mask].copy()

    # sort the videos by similarity
    video_vectors = video_vectors.sort_values(by="similarity", ascending=False).head(
        rows
    )

    # return the top rows
    return video_vectors.head(rows)

def display_results(videos: pd.core.frame.DataFrame, query: str):
    def _gen_yt_url(video_id: str, seconds: int) -> str:
        """convert time in format 00:00:00 to seconds"""
        return f"https://youtu.be/{video_id}?t={seconds}"

    logger.info(f"\nVideos similar to '{query}':")
    for _, row in videos.iterrows():
        youtube_url = _gen_yt_url(row["videoId"], row["seconds"])
        logger.info(f" - {row['title']}")
        logger.info(f"   Summary: {' '.join(row['summary'].split()[:15])}...")
        logger.info(f"   YouTube: {youtube_url}")
        logger.info(f"   Similarity: {row['similarity']}")
        logger.info(f"   Speakers: {row['speaker']}")

pd_vectors = load_dataset(dataset_path)

# get user query from imput
while True:
    query = input("Enter a query: ")
    if query == "exit":
        break
    videos = get_videos(query, pd_vectors, 5)
    display_results(videos, query)

logger.info("Done with the script.")