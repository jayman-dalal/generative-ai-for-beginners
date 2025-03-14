import openai as ai
from helpers.logging_config import logger  # Import the logger
from helpers import helpers

logger.info("Starting the script...")
client = helpers.get_azure_openai_client()
# Check if environment variables are loaded correctly
if not helpers.is_env_loaded():
    logger.error("Environment variables are not loaded correctly.")
    raise EnvironmentError("Environment variables are not loaded correctly.")

no_recipes = input("No of recipes (for example, 5: ")

ingredients = input("List of ingredients (for example, chicken, potatoes, and carrots: ")

filter = input("Filter (for example, vegetarian, vegan, or gluten-free: ")

# interpolate the number of recipes into the prompt an ingredients
prompt = f"Show me {no_recipes} recipes for a dish with the following ingredients: {ingredients}. Per recipe, list all the ingredients used, no {filter}: "
messages = [{"role": "user", "content": prompt}]

completion = client.client.chat.completions.create(model=client.deployment, messages=messages, max_tokens=600, temperature = 0.1)


# print response
logger.info("Recipes:")
logger.info(completion.choices[0].message.content)

old_prompt_result = completion.choices[0].message.content
prompt_shopping = "Produce a shopping list, and please don't include ingredients that I already have at home: "

new_prompt = f"Given ingredients at home {ingredients} and these generated recipes: {old_prompt_result}, {prompt_shopping}"
messages = [{"role": "user", "content": new_prompt}]
completion = client.client.chat.completions.create(model=client.deployment, messages=messages, max_tokens=600, temperature=0)

# print response
logger.info("\n=====Shopping list ======= \n")
logger.info(completion.choices[0].message.content)
logger.info("Done with the script.")

