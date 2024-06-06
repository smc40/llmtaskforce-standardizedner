'''Description: This script connects to the Azure OpenAI service and utilizes a pre-defined prompt to extract specific entities related to healthcare, specifically "adverse reactions" or "side effects" (collectively referred to as "Medical Problems") from user-provided text.
The extracted entities are returned as a list'''

#Load packages
import os
from openai import AzureOpenAI
from dotenv import load_dotenv
import pandas as pd
import ast

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
role = "You are having a role of the healthcare professional who is flagging adverse reactions and side effects included in the input text given by the user."


#Establishing connection with Azure
client = AzureOpenAI(
azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"), 
api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
api_version="2024-02-01")


def detect_signals(user_input: str, model = "gpt-4") -> list:

    response = client.chat.completions.create(
    model=model , # model = "gpt-35-turbo" or "gpt-4".
    messages=[
        {"role": "system", "content": f"{role}"},
        {"role": "user", "content": f"{selected_prompt}" + user_input}
      ]
    )
    try:
        out_list = ast.literal_eval(response.choices[0].message.content)
        if not out_list:
            out_list = ['No ADRs detected!']
    except Exception as e:
        out_list = ['No ADRs detected!']
    return out_list

#Test
# signals = detect_signals("I had a headache and a fever after taking the medicine")

