import logging
import os

import azure.identity as identity
import azure.search.documents as search
import azure.search.documents.indexes as indexes
import openai as ai
from dotenv import load_dotenv

import helpers.logging_config as logging_config

logger = logging_config.setup_logger(logger=logging.getLogger(__name__))
class AzureOpenAIClient:
    def __init__(self, client, endpoint, deployment, embeddings_deployment):
        self.client = client
        self.endpoint = endpoint
        self.deployment = deployment
        self.embeddings_deployment = embeddings_deployment

def is_env_loaded():
    required_vars = ["AZURE_OPENAI_API_VERSION", "AZURE_OPENAI_TENANT_NAME", "AZURE_AI_SEARCH_ENDPOINT"]
    return all(os.getenv(var) is not None for var in required_vars)

def get_azure_openai_client():
    if not is_env_loaded():
        load_dotenv()

    api_version = os.getenv("AZURE_OPENAI_API_VERSION")
    tenant_name = os.getenv("AZURE_OPENAI_TENANT_NAME")
    embeddings_deployment = os.getenv("AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT")
    if tenant_name and tenant_name == "MSDN":
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT_MSDN")
        deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_MSDN")
        subscription_key = os.getenv("AZURE_OPENAI_API_KEY_MSDN") 
        logger.info(f"OpenAI Endpoint: {endpoint}")
        logger.info(f"OpenAI Deployment: {deployment}")
        client = ai.AzureOpenAI(  
            azure_endpoint=endpoint,  
            api_key=subscription_key,  
            api_version=api_version,
        )
    else:
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
        logger.info(f"OpenAI Endpoint: {endpoint}")
        logger.info(f"OpenAI Deployment: {deployment}")
        credential = identity.DefaultAzureCredential()
        token_provider = identity.get_bearer_token_provider(
            credential,
            "https://cognitiveservices.azure.com/.default"
        )
        client = ai.AzureOpenAI(
            azure_endpoint=endpoint,
            azure_ad_token_provider=token_provider,
            api_version=api_version,
        )
    logger.info(f"OpenAI Embedding Deployment: {embeddings_deployment}")

    return AzureOpenAIClient(client, endpoint, deployment, embeddings_deployment)

def get_azure_ai_search_client(index_name: str) -> search.SearchClient:
    if not is_env_loaded():
        load_dotenv()

    endpoint = os.getenv("AZURE_AI_SEARCH_ENDPOINT")
    logger.info(f"AI Search Endpoint: {endpoint}")
    credential = identity.DefaultAzureCredential()
    search_client = search.SearchClient(endpoint=endpoint, index_name=index_name, credential=credential)
    return search_client

def get_azure_ai_search_index_client() -> indexes.SearchIndexClient:
    if not is_env_loaded():
        load_dotenv()

    endpoint = os.getenv("AZURE_AI_SEARCH_ENDPOINT")
    logger.info(f"AI Search Endpoint: {endpoint}")
    credential = identity.DefaultAzureCredential()
    index_client = indexes.SearchIndexClient(endpoint=endpoint, credential=credential)
    return index_client