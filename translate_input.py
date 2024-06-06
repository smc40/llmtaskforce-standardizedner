import os
import requests
import json
# from transformers import AutoTokenizer, MarianMTModel
from dotenv import load_dotenv
load_dotenv()



################
# autodetect and translate to english using the DeepL API
# WARNING: API key used is for the free version. There is a monthly rate limit.
deepl_auth_key = os.getenv('DEEPL_API_KEY')
deepl_api_url = 'https://api-free.deepl.com/v2/translate'  # free API v2 translate
################


def translate_description(input_text):
    """
    Translate the input text to English, before making the predictions
    input_text (str): the text to be translated
    return (str): user input translated to English, through DeepL API and automatic language detection
    """

    params = {
            'auth_key': os.getenv('DEEPL_API_KEY'),
            'text': input_text,
            'split_sentences': 0,
            'target_lang': 'EN-US'  # EN-US, EN-GB, or EN
    }
    response = requests.post(deepl_api_url, data=params)
    deepl_translation = response.json()['translations'][0]['text']

    return deepl_translation
