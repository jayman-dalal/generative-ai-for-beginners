import azure.cosmos as cosmos
import logging
import openai as ai
import os
import pandas as pd
import traceback
from sklearn.neighbors import NearestNeighbors

import helpers.logging_config
from helpers import helpers

logger = logging.getLogger(__name__)
logger.info("Starting the script...")
client = None
current_module_directory = os.path.dirname(os.path.abspath(__file__))

def init_cosmosdb() -> cosmos.CosmosClient:
    url = os.getenv("AZURE_COSMOSDB_ENDPOINT")
    key = os.getenv("AZURE_COSMOSDB_KEY")
    cosmos_client = cosmos.CosmosClient(url, credential=key)
    database = cosmos_client.get_database_client("ragtestdb")
    container = database.get_container_client("ragtestcontainer")
    return container

def load_nn_data() -> pd.DataFrame:
    # Initialize an empty DataFrame
    df = pd.DataFrame(columns=['path', 'text'])
    # splitting our data into chunks
    #data_paths= ["data/frameworks.md?WT.mc_id=academic-105485-koreyst", "data/own_framework.md?WT.mc_id=academic-105485-koreyst", "data/perceptron.md?WT.mc_id=academic-105485-koreyst"]
    data_paths= ["data/frameworks.md", "data/own_framework.md", "data/perceptron.md"]

    rows = []
    for path in data_paths:
        dataset_path = os.path.join(current_module_directory, path)
        with open(dataset_path, 'r', encoding='utf-8') as file:
            file_content = file.read()

        # Append the file path and text to the DataFrame
        rows.append({'path': path, 'text': file_content})
    df = pd.concat([df, pd.DataFrame(rows)], ignore_index=True)

    logger.info(f"Loaded {len(df)} files into DataFrame.")
    logger.info(f"DataFrame head: \n{df.head()}")
    return df

def split_text(text, max_length, min_length):
    words = text.split()
    chunks = []
    current_chunk = []

    for word in words:
        current_chunk.append(word)
        if len(' '.join(current_chunk)) < max_length and len(' '.join(current_chunk)) > min_length:
            chunks.append(' '.join(current_chunk))
            current_chunk = []

    # If the last chunk didn't reach the minimum length, add it anyway
    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks

def create_embeddings(text):
    # Create embeddings for each document chunk
    embeddings = client.client.embeddings.create(input = text, model=client.embeddings_deployment).data[0].embedding
    return embeddings

def create_nearest_neighbors():
    nn_data = load_nn_data()
    # Assuming analyzed_df is a pandas DataFrame and 'output_content' is a column in that DataFrame
    splitted_df = nn_data.copy()
    splitted_df['chunks'] = splitted_df['text'].apply(lambda x: split_text(x, 400, 300))
    logger.info(f"Splitted DataFrame:\n{splitted_df[['path', 'chunks']].head()}")
    
    # Assuming 'chunks' is a column of lists in the DataFrame splitted_df, we will split the chunks into different rows
    flattened_df = splitted_df.explode('chunks')
    logger.info(f"Flattened DataFrame:\n{flattened_df[['path', 'chunks']].head()}")

    embeddings = []
    for chunk in flattened_df['chunks']:
        embeddings.append(create_embeddings(chunk))

    # store the embeddings in the dataframe
    flattened_df['embeddings'] = embeddings
    logger.info(f"DataFrame with embeddings:\n{flattened_df[['path', 'chunks', 'embeddings']].head()}")

    embeddings = flattened_df['embeddings'].to_list()

    # Create the search index
    nbrs = NearestNeighbors(n_neighbors=5, algorithm='ball_tree').fit(embeddings)

    # To query the index, you can use the kneighbors method
    distances, indices = nbrs.kneighbors(embeddings)

    # Store the indices and distances in the DataFrame
    flattened_df['indices'] = indices.tolist()
    flattened_df['distances'] = distances.tolist()

    logger.info(f"DataFrame with indices and distances:\n{flattened_df[['path', 'chunks', 'indices', 'distances']].head()}")

    return flattened_df, nbrs

def chatbot(user_input, flattened_df, nbrs):
    # Convert the question to a query vector
    query_vector = create_embeddings(user_input)

    # Find the most similar documents
    distances, indices = nbrs.kneighbors([query_vector])

    # Retrieve the relevant document chunks
    context = []
    for index in indices[0]:
        context.append(flattened_df['chunks'].iloc[index])

    # Combine the retrieved context into a single string
    combined_context = "\n".join(context)

    logger.info(f"Retrieved context for the query:\n{combined_context}")

    # Create the messages object for the Chat Completions API
    messages = [
        {
            "role": "system",
            "content": (
                "You are an AI assistant that provides accurate and grounded answers "
                "based on the provided context. Use the context below to answer the user's question."
            )
        },
        {
            "role": "system",
            "content": f"Context:\n{combined_context}"
        },
        {
            "role": "user",
            "content": user_input
        }
    ]

    # use chat completion to generate a response
    response = client.client.chat.completions.create(
        model=client.deployment,
        temperature=0.7,
        max_tokens=800,
        messages=messages
    )

    return response.choices[0].message

def main():
    try:
        global client
        client = helpers.get_azure_openai_client()
        # Check if environment variables are loaded correctly
        if not helpers.is_env_loaded():
            logger.error("Environment variables are not loaded correctly.")
            raise EnvironmentError("Environment variables are not loaded correctly.")

        # cosmos_container = init_cosmosdb()
        flattened_df, nbrs = create_nearest_neighbors()

        # Your text question
        question = "what is a perceptron?"
        chatbot_response = chatbot(question, flattened_df, nbrs)
        logger.info(f"Chatbot response: {chatbot_response}")

        logger.info("Script completed successfully.")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        logger.error(traceback.format_exc())
    finally:
        logger.info("DONE.")
if __name__ == "__main__":
    main()