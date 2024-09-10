import os
import requests
import json
import re
import html
import pandas as pd
from transformers import AutoTokenizer, MarianMTModel
from langdetect import detect
# from dotenv import load_dotenv
# load_dotenv()
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(usecwd=True))

################
# autodetect and translate to english using the DeepL API
# WARNING: API key used is for the free version. There is a monthly rate limit.
deepl_auth_key = os.getenv('DEEPL_API_KEY')
deepl_api_url = 'https://api-free.deepl.com/v2/translate'  # free API v2 translate
################

################
# define pretrained translation model: specialized in biomedical translation from dutch to english
################
translation_model_path = 'data/FremyCompany-opus-mt-nl-en-healthcare'  # use for local hf model storage location
translation_model_name = 'FremyCompany/opus-mt-nl-en-healthcare'    # download
translation_model = MarianMTModel.from_pretrained(translation_model_name)  # TypedStorage warning
tokenizer = AutoTokenizer.from_pretrained(translation_model_name)


def clean_text(text):
    """Basic input text cleaning"""
    try:
        # text = str(text)
        text = html.unescape(text)  # remove HTML entities
        text = re.sub(r'<.*?>', '', text)  # remove HTML tags
        text = re.sub(r'https?://\S+|www\.\S+', '', text)  # remove URLs
        text = re.sub(r'[^\w\s]', '', text)  # remove punctuation and special characters
        text = re.sub(r'[^\x00-\x7F]+', '', text)  # remove emojis
        text = re.sub(r'\s+', ' ', text)  # trim whitespace
    except:  # skip if this gives any errors
        text = text
    return text.strip().lower()  # final trim and lowercase


def detect_language(input_text):
    """langdetect method"""
    if isinstance(input_text, str):
        return detect(input_text)
    elif isinstance(input_text, list):
        combined_input = ' '.join(input_text)
        return detect(combined_input)
    elif isinstance(input_text, pd.DataFrame):
        input_text = input_text.astype(str)
        row_strings = input_text.apply(lambda row: row.str.cat(sep=' '), axis=1)
        combined_input = row_strings.sum(axis=0, skipna=False)
        return detect(combined_input)
    else:
        raise TypeError('Invalid data type for language detection!')


def translate_description(input_text, detected_lang):
    """
    Translate the input text to English, before making the predictions
    input_text (str): the text to be translated
    return (str): user input translated to English, through DeepL API and automatic language detection
    """
    # Detect the source language, if not already specified
    if not detected_lang:
        detected_lang = detect(input_text)

    # For English, simply return the output
    if detected_lang == 'en':
        return input_text

    # For Dutch, use custom NL->EN medical translation model
    if detected_lang == 'nl':
        batch = tokenizer([input_text], return_tensors="pt")
        generated_ids = translation_model.generate(**batch, max_length=512)
        translated_text = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
        return translated_text

    # For other languages, automatically detect & translate using DeepL
    else:
        try:
            params = {
                    'auth_key': os.getenv('DEEPL_API_KEY'),
                    'text': input_text,
                    'split_sentences': 0,
                    'source_lang': detected_lang.upper(),  # optionally, specify source lang
                    'target_lang': 'EN-US'  # EN-US, EN-GB, or EN
            }
            response = requests.post(deepl_api_url, data=params)
            deepl_translation = response.json()['translations'][0]['text']

        except:  # try DeepL without source language if the initial request fails
            params = {
                    'auth_key': os.getenv('DEEPL_API_KEY'),
                    'text': input_text,
                    'split_sentences': 0,
                    'target_lang': 'EN-US'  # EN-US, EN-GB, or EN
            }
            response = requests.post(deepl_api_url, data=params)
            deepl_translation = response.json()['translations'][0]['text']

        return deepl_translation
