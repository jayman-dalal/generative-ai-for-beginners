import os
import openai as ai
import azure.identity as identity
from dotenv import load_dotenv
from helpers.logging_config import logger  # Import the logger

class AzureOpenAIClient:
    def __init__(self, client, endpoint, deployment):
        self.client = client
        self.endpoint = endpoint
        self.deployment = deployment

def is_env_loaded():
    required_vars = ["AZURE_OPENAI_API_VERSION", "AZURE_OPENAI_TENANT_NAME"]
    return all(os.getenv(var) is not None for var in required_vars)

def get_azure_openai_client():
    if not is_env_loaded():
        load_dotenv()

    api_version = os.getenv("AZURE_OPENAI_API_VERSION")
    tenant_name = os.getenv("AZURE_OPENAI_TENANT_NAME")
    if tenant_name and tenant_name == "MSDN":
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT_MSDN")
        deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_MSDN")
        subscription_key = os.getenv("AZURE_OPENAI_API_KEY_MSDN") 
        logger.info(f"Endpoint: {endpoint}")
        logger.info(f"Deployment: {deployment}")
        client = ai.AzureOpenAI(  
            azure_endpoint=endpoint,  
            api_key=subscription_key,  
            api_version=api_version,
        )
    else:
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
        logger.info(f"Endpoint: {endpoint}")
        logger.info(f"Deployment: {deployment}")
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

    return AzureOpenAIClient(client, endpoint, deployment)