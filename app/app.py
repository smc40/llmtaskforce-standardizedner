import signal
import asyncio
from shiny import App, ui, render, reactive
import requests
import pandas as pd
import uvicorn
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Fetch environment variables
dictionary_match_url = os.getenv('DICTIONARY_MATCH_URL')
dictionary_match_url_fetch = os.getenv('DICTIONARY_MATCH_URL_FETCH')
azure_openai_api_key = os.getenv('AZURE_OPENAI_API_KEY')
azure_openai_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')

logger.info(f'DICTIONARY_MATCH_URL: {dictionary_match_url}')
logger.info(f'AZURE_OPENAI_API_KEY: {azure_openai_api_key}')
logger.info(f'AZURE_OPENAI_ENDPOINT: {azure_openai_endpoint}')

app_ui = ui.page_fluid(
    ui.input_text("api_url", "Enter API URL", value=dictionary_match_url), 
    ui.input_text("fetch_url", "Enter Fetch URL", value=dictionary_match_url_fetch), 
    ui.input_action_button("fetch", "Fetch Data"),
    ui.input_text("data_title", "Enter Title"),
    ui.input_text("data_body", "Enter Body"),
    ui.input_action_button("send", "Send Data"),
    ui.output_text_verbatim("response"),
    ui.output_text_verbatim("split_response")  # Add output for split data
)

def server(input, output, session):
    fetch_state = {'count': 0}
    send_state = {'count': 0}
    fetched_data = reactive.Value(None)  # Use reactive value for fetched data
    
    @output
    @render.text
    def response():
        if input.fetch() > fetch_state['count']:
            fetch_state['count'] = input.fetch()
            api_url = input.fetch_url()
            logger.info(f'Fetch button clicked. API URL: {api_url}')
            try:
                res = requests.get(api_url)
                res.raise_for_status()
                data = res.json()
                fetched_data.set(data)  # Store fetched data reactively
                logger.info(f'Data fetched successfully: {data}')
                df = pd.DataFrame(data['data'])  # Assuming 'data' key contains the list
                return df.to_string()
            except requests.exceptions.RequestException as e:
                logger.error(f'Error fetching data: {e}')
                return str(e)
        
        if input.send() > send_state['count']:
            send_state['count'] = input.send()
            api_url = input.api_url()
            data = {
                "title": input.data_title(),
                "body": input.data_body(),
                "userId": 1  # JSONPlaceholder API requires a userId for POST requests
            }
            logger.info(f'Send button clicked. API URL: {api_url}, Data: {data}')
            try:
                res = requests.post(api_url, json=data)
                res.raise_for_status()
                logger.info(f'Data sent successfully: {res.json()}')
                return res.json()
            except requests.exceptions.RequestException as e:
                logger.error(f'Error sending data: {e}')
                return str(e)
    
    def split_letters(text):
        return ' '.join(text)
    
    @output
    @render.text
    def split_response():
        data = fetched_data.get()
        if data:
            try:
                first_record = data['data'][0]  # Access the 'data' key to get the list of records
                first_value = next(iter(first_record.values()))  # Get the first value
                if isinstance(first_value, str):
                    return split_letters(first_value)
                else:
                    return "First value is not a string"
            except (KeyError, IndexError) as e:
                return f"Error accessing data: {e}"
        else:
            return "No data fetched"

app = App(app_ui, server)

def main():
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)

    loop = asyncio.get_event_loop()
    loop.add_signal_handler(signal.SIGTERM, lambda: asyncio.create_task(server.shutdown()))
    loop.add_signal_handler(signal.SIGINT, lambda: asyncio.create_task(server.shutdown()))

    logger.info('Starting server...')
    loop.run_until_complete(server.serve())
    logger.info('Server stopped.')

if __name__ == "__main__":
    main()
