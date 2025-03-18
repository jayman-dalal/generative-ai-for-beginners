
import logging
import traceback

import helpers.logging_config as logging_config
from helpers import helpers

logger = logging_config.setup_logger(logger=logging.getLogger(__name__))
logger.infoh1("Starting the script...")
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
        logger.debug("This is a debug message.")
        logger.info("This is a regular info message.")
        logger.infoh1("This is a special info message.")
        logger.warning("This is a warning message.")
        logger.error("This is an error message.")
        logger.critical("This is a critical message.")
        logger.infoh1("DONE.")

if __name__ == "__main__":
    main()