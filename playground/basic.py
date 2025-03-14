
import openai as ai
from helpers.logging_config import logger  # Import the logger
from helpers import helpers

logger.info("Starting the script...")
client = helpers.get_azure_openai_client()
# Check if environment variables are loaded correctly
if not helpers.is_env_loaded():
    logger.error("Environment variables are not loaded correctly.")
    raise EnvironmentError("Environment variables are not loaded correctly.")

chat_prompt = [
    {
        "role": "system",
        "content": "You are an AI assistant that helps people find information."
    }
]

# Include speech result if speech is enabled
messages = chat_prompt

completion = client.client.chat.completions.create(
    model=client.deployment,
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