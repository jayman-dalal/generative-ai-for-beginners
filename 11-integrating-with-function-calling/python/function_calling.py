import openai as ai
import logging
from helpers import helpers
import logging
import helpers.logging_config
import traceback
import requests
import json

logger = logging.getLogger(__name__)
logger.info("Starting the script...")
client = None

def search_courses(role, product, level):
    url = "https://learn.microsoft.com/api/catalog/"
    params = {
        "role": role,
        "product": product,
        "level": level
    }
    response = requests.get(url, params=params)
    modules = response.json()["modules"]
    results = []
    for module in modules[:5]:
        title = module["title"]
        url = module["url"]
        results.append({"title": title, "url": url})
    return str(results)


def setup_function_calling():
    student_1_description="Emily Johnson is a sophomore majoring in computer science at Duke University. She has a 3.7 GPA. Emily is an active member of the university's Chess Club and Debate Team. She hopes to pursue a career in software engineering after graduating."
    student_2_description = "Michael Lee is a sophomore majoring in computer science at Stanford University. He has a 3.8 GPA. Michael is known for his programming skills and is an active member of the university's Robotics Club. He hopes to pursue a career in artificial intelligence after finshing his studies."

    prompt1 = f'''
    Please extract the following information from the given text and return it as a JSON object:

    name
    major
    school
    grades
    club

    This is the body of text to extract the information from:
    {student_1_description}
    '''

    prompt2 = f'''
    Please extract the following information from the given text and return it as a JSON object:

    name
    major
    school
    grades
    club

    This is the body of text to extract the information from:
    {student_2_description}
    '''

    openai_response1 = client.client.chat.completions.create(
        model=client.deployment,
        messages = [{'role': 'user', 'content': prompt1}]
    )
    logger.info(f"Response1:{openai_response1.choices[0].message.content}")

    openai_response2 = client.client.chat.completions.create(
        model=client.deployment,
        messages = [{'role': 'user', 'content': prompt2}]
    )
    logger.info(f"Response2:{openai_response2.choices[0].message.content}")

    functions = [
    {
        "name":"search_courses",
        "description":"Retrieves courses from the search index based on the parameters provided",
        "parameters":{
            "type":"object",
            "properties":{
                "role":{
                "type":"string",
                "description":"The role of the learner (i.e. developer, data scientist, student, etc.)"
                },
                "product":{
                "type":"string",
                "description":"The product that the lesson is covering (i.e. Azure, Power BI, etc.)"
                },
                "level":{
                "type":"string",
                "description":"The level of experience the learner has prior to taking the course (i.e. beginner, intermediate, advanced)"
                }
            },
            "required":[
                "role"
            ]
        }
    }]

    messages= [ {"role": "user", "content": "Find me a good course for a beginner student to learn Azure."} ]
    response = client.client.chat.completions.create(model=client.deployment, 
                                        messages=messages,
                                        functions=functions, 
                                        function_call="auto") 

    logger.info(f"Function Call Message Response: {response.choices[0].message}")
    response_message = response.choices[0].message

    # Check if the model wants to call a function
    if response_message.function_call.name:
        logger.info(f"Recommended Function call:{response_message.function_call.name}")

        # Call the function. 
        function_name = response_message.function_call.name
        available_functions = {
                "search_courses": search_courses,
        }
        function_to_call = available_functions[function_name] 

        function_args = json.loads(response_message.function_call.arguments)
        function_response = function_to_call(**function_args)

        logger.info(f"Output of function call: {function_response}")
        logger.info(f"Type: {type(function_response)}")

        # Add the assistant response and function response to the messages
        messages.append( # adding assistant response to messages
            {
                "role": response_message.role,
                "function_call": {
                    "name": function_name,
                    "arguments": response_message.function_call.arguments,
                },
                "content": None
            }
        )
        messages.append( # adding function response to messages
            {
                "role": "function",
                "name": function_name,
                "content":function_response,
            }
        )

        logger.info(f"Messages in next request: {messages}")

        second_response = client.client.chat.completions.create(
            messages=messages,
            model=client.deployment,
            function_call="auto",
            functions=functions,
            temperature=0
                )  # get a new response from GPT where it can see the function response


        logger.info(f"Second Function Response: {second_response.choices[0].message}")

def main():
    try:
        global client
        client = helpers.get_azure_openai_client()
        # Check if environment variables are loaded correctly
        if not helpers.is_env_loaded():
            logger.error("Environment variables are not loaded correctly.")
            raise EnvironmentError("Environment variables are not loaded correctly.")

        setup_function_calling()
        logger.info("Script completed successfully.")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        logger.error(traceback.format_exc())
    finally:
        logger.info("DONE.")
if __name__ == "__main__":
    main()