import anthropic
import os
from openai import AzureOpenAI, OpenAI
import openai
import re
import pandas as pd
import ast
from typing import List, Any
# from dotenv import load_dotenv
# load_dotenv()
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(usecwd=True))

#################################################
#Selected prompt
selected_prompt = '''
### TASK

Your task is to extract specific entities related to healthcare and return the python list with entities extracted. These entities include "adverse reactions" or "side effects" included in the text analyzed, referred to collectively as "Medical Problems."

### Entity Definitions:

"Medical Problems" are phrases indicating observations made by patients or clinicians about abnormalities in the patient’s body or mind, thought to be caused by vaccines, drugs, or diseases.

### Generate the answer

The text where you should perform the task described is as follows: 

'''

#System role definition
# role = "You are having a role of the healthcare professional who is flagging adverse reactions and side effects included in the input text given by the user."
role = "You are a pharmacovigilance expert specializing in identifying possible adverse drug reactions. Your task is to detect and extract adverse reactions from the user's query, while also considering the context and potential causality."


def initialize_client(client_name):
    """
    Load the appropriate client for the request
    Example options: azure, openai, anthropic
    """
    if client_name.lower() == 'azure':
        client = AzureOpenAI(
            azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version="2024-02-01")
    elif client_name.lower() == 'openai':
        client = OpenAI(
            api_key=os.getenv('OPENAI_API_KEY'),
            organization=os.getenv('OPENAI_ORGANIZATION')
        )
    elif client_name.lower() == 'anthropic':
        client = anthropic.Anthropic(
            api_key=os.environ.get("ANTHROPIC_API_KEY"),
        )
    return client


def extract_list_from_response(response_text: str) -> List[Any]:
    def clean_string(s: str) -> str:
        return s.strip().replace("'", '"').replace('"', '"').replace('"', '"')

    def safe_eval(s: str) -> Any:
        try:
            return ast.literal_eval(s)
        except (ValueError, SyntaxError):
            return s

    # Method 1: Try simple ast eval
    try:
        return ast.literal_eval(clean_string(response_text))
    except Exception as e:
        print(f"List extraction - Method 1 failed: {e}")

    # Method 2: Try to find and parse a list-like structure
    list_pattern = r'\[([^\[\]]*)\]'
    match = re.search(list_pattern, response_text)
    if match:
        try:
            items = [safe_eval(clean_string(item)) for item in re.split(r',\s*', match.group(1))]
            return items
        except Exception as e:
            print(f"List extraction - Method 2 failed: {e}")

    # Method 3: Try to extract comma-separated items
    try:
        items = [safe_eval(clean_string(item)) for item in re.split(r',\s*', response_text)]
        return items
    except Exception as e:
        print(f"List extraction - Method 3 failed: {e}")

    # If all methods fail, return a default list
    return ['No ADRs detected!']


def detect_signals(user_input: str, selected_model='Claude-3-5-Sonnet (Anthropic)') -> list:
    company = re.search(r'\(([^)]+)\)', selected_model).group(1).lower().strip()
    model_name = (re.search(r'^(.*)\(.*$', selected_model).group(1)).lower().strip()
    client = initialize_client(company)

    if company.lower() == 'openai':
        response = openai.chat.completions.create(
            model=model_name,
            max_tokens=512,  # hardcoded for cost control, can increase if necessary
            temperature=0.0,
            messages=[
                {"role": "system", "content": f"{role}"},
                {"role": "user", "content": f"{selected_prompt}" + user_input}
            ]
        )
        response_text = response.choices[0].message.content
        out_list = extract_list_from_response(response_text)
        return out_list

    elif company.lower() == 'anthropic':
        # specify date/version, depending on the model.  currently included: haiku-3 or sonnet-3-5
        model_version = '20240307' if 'haiku' in model_name.lower() else '20240620'

        response = client.messages.create(
            model=f"{model_name}-{model_version}",  # specify model name & version/date
            max_tokens=512,  # hardcoded for cost control, can increase if necessary
            temperature=0.0,
            system=role,
            messages=[
                {"role": "user", "content": f"{selected_prompt}" + user_input}
            ]
        )
        response_text = response.content[0].text
        #print(response)
        #print(response_text)
        out_list = extract_list_from_response(response_text)
        return out_list

    else:
        raise ValueError("""Invalid company / model specfied! Choose company ['openai', 'anthropic'] 
                    and models from: [model selection list]""")


### Test
# signals = detect_signals("I had a headache and a fever after taking the medicine",
#                          company="anthropic", model='Claude-3-Sonnet (Anthropic)')

# signals = detect_signals("I had a headache and a fever after taking the medicine",
#                          selected_model='GPT-4o (OpenAI)')

#

