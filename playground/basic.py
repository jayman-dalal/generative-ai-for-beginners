import os
import base64
import openai as ai
import azure.identity as identity
from dotenv import load_dotenv
import logging

# Configure logging with a custom format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

logger.info("Starting the script...")
load_dotenv()

endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
api_version = os.getenv("AZURE_OPENAI_API_VERSION")
logger.info(f"Endpoint: {endpoint}")
logger.info(f"Deployment: {deployment}")


# Initialize Azure OpenAI Service client with Entra ID authentication
token_provider = identity.get_bearer_token_provider(
    identity.DefaultAzureCredential(),
    "https://cognitiveservices.azure.com/.default"
)

client = ai.AzureOpenAI(
    azure_endpoint=endpoint,
    azure_ad_token_provider=token_provider,
    api_version=api_version,
)

chat_prompt = [
    {
        "role": "system",
        "content": "You are an AI assistant that helps people find information."
    }
]

# Include speech result if speech is enabled
messages = chat_prompt

completion = client.chat.completions.create(
    model=deployment,
    messages=messages,
    max_tokens=800,
    temperature=0.7,
    top_p=0.95,
    frequency_penalty=0,
    presence_penalty=0,
    stop=None,
    stream=False
)

print(completion.to_json())
logger.info("Done with the script.")