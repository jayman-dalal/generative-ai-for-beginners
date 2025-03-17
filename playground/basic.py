
import openai as ai
import logging
from helpers import helpers
import logging
import helpers.logging_config
import traceback

logger = logging.getLogger(__name__)
logger.info("Starting the script...")
client = None

def main():
    try:
        global client
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

        logger.info(completion.to_json())
        logger.info("Script completed successfully.")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        logger.error(traceback.format_exc())
    finally:
        logger.info("DONE.")
if __name__ == "__main__":
    main()