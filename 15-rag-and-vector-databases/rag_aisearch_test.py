import logging
import os
import traceback

import azure.search.documents.indexes.models as index_models
import pandas as pd

import helpers.logging_config as logging_config
from helpers import helpers

logger = logging_config.setup_logger(logger=logging.getLogger(__name__))
logger.infoh1("Starting the script...")
client = None
current_module_directory = os.path.dirname(os.path.abspath(__file__))
SEARCH_INDEX_NAME = "ragtestindex"

def create_search_index():
    """Create an Azure Cognitive Search index."""
    logger.infoh1("Creating Azure Cognitive Search index...")
    index_client = helpers.get_azure_ai_search_index_client()

    # Define the index schema
    fields = [
        index_models.SimpleField(name="id", type="Edm.String", key=True),
        index_models.SearchableField(name="path", type="Edm.String"),
        index_models.SearchableField(name="text", type="Edm.String")
    ]
    index = index_models.SearchIndex(name=SEARCH_INDEX_NAME, fields=fields)

    # Create the index
    try:
        index_client.create_index(index)
        logger.info(f"Search index '{SEARCH_INDEX_NAME}' created successfully.")
    except Exception as e:
        if e.status_code == 400 and f'{e}'.find("(CannotCreateExistingIndex)") != -1:  # Index already exists
            logger.warning(f"Search index '{SEARCH_INDEX_NAME}' already exists.")
        else:
            logger.error(f"Search index '{SEARCH_INDEX_NAME}' could not be created: {e}")
            raise

def load_nn_data() -> pd.DataFrame:
    # Initialize an empty DataFrame
    logger.infoh1("Loading data into DataFrame...")
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

def index_data(data):
    """Index data into Azure Cognitive Search."""
    logger.infoh1("Indexing data into Azure Cognitive Search...")
    search_client = helpers.get_azure_ai_search_client(index_name=SEARCH_INDEX_NAME)

    # Prepare the data for indexing
    documents = []
    for i, row in data.iterrows():
        documents.append({
            "id": str(i),
            "path": row["path"],
            "text": row["text"]
        })

    # Upload the documents
    try:
        search_client.upload_documents(documents=documents)
        logger.info(f"Indexed {len(documents)} documents into Azure Cognitive Search.")
    except Exception as e:
        logger.error(f"Failed to index documents: {e}")
        raise

def query_search_index(query: str) -> list:
    """Query the Azure Cognitive Search index."""
    logger.infoh1(f"Querying Azure Cognitive Search index with query: {query}")
    search_client = helpers.get_azure_ai_search_client(index_name=SEARCH_INDEX_NAME)

    # Perform the search
    results = search_client.search(query, top=5)
    context = []
    for result in results:
        context.append(result["text"])
    return context

def chatbot(user_input: str, use_rag: bool) -> str:
    """Generate a response using OpenAI Chat Completions with Azure Cognitive Search context."""
    logger.infoh1(f"Generating response for user input: {user_input}. RAG Enabled: {use_rag}")
    messages = [
            {
                "role": "system",
                "content": (
                    "You are an AI assistant that provides accurate and grounded answers "
                    "based on the provided context. Use the context below to answer the user's question."
                )
            },
            {
                "role": "user",
                "content": user_input
            }
        ]
    # Query the search index for relevant context
    if use_rag:
        combined_context = query_search_index(user_input)
        logger.info(f"UseRag enabled: Retrieved additional context for the query:\n{combined_context}")

        # Create the messages object for the Chat Completions API
        messages.append(
        {
            "role": "system",
            "content": f"Context:\n{combined_context}"
        })

    # Use the Chat Completions API to generate a response
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

        # Create the search index
        create_search_index()

        # Load and index data
        nn_data = load_nn_data()
        index_data(nn_data)

        # User's question
        question = "What is a perceptron?"
        chatbot_response = chatbot(question, use_rag=True)
        logger.info(f"Chatbot response (with RAG): {chatbot_response}")
        chatbot_response = chatbot(question, use_rag=False)
        logger.info(f"Chatbot response (without RAG): {chatbot_response}")

        logger.info("Script completed successfully.")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        logger.error(traceback.format_exc())
    finally:
        logger.infoh1("DONE.")

if __name__ == "__main__":
    main()