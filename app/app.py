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
dictionary_match_url = os.getenv('DICTIONARY_MATCH_URL', 'http://dict-match:8002/message')

logger.info(f'DICTIONARY_MATCH_URL: {dictionary_match_url}')

app_ui = ui.page_fluid(
    ui.input_text("api_url", "Enter API URL", value=dictionary_match_url), 
    ui.input_text("sentence", "Enter Sentence to Split"), 
    ui.input_action_button("split", "Split Sentence"),
    ui.output_text_verbatim("response"),
    ui.output_text_verbatim("processed_response")
)

def server(input, output, session):
    split_state = {'count': 0}
    split_data = reactive.Value("")

    @reactive.event(input.split)
    def handle_button_click():
        split_state['count'] += 1
        api_url = input.api_url()
        sentence = input.sentence()
        logger.info(f'Split button clicked. API URL: {api_url}, Sentence: {sentence}')
        try:
            logger.info(f'Making API request to {api_url} with sentence: {sentence}')
            res = requests.get(api_url, params={'sentence': sentence})
            logger.info(f'API response status: {res.status_code}')
            res.raise_for_status()
            data = res.json()
            logger.info(f'Data fetched successfully: {data}')
            split_data.set(data)
        except requests.exceptions.RequestException as e:
            logger.error(f'Error fetching data: {e}')
            split_data.set({'error': str(e)})
        except ValueError as e:
            logger.error(f'Error parsing JSON response: {e}')
            split_data.set({'error': 'Error parsing JSON response'})
        except Exception as e:
            logger.error(f'Unexpected error: {e}')
            split_data.set({'error': 'Unexpected error occurred'})

    @output
    @render.text
    def response():
        data = split_data.get()
        if isinstance(data, dict) and 'error' in data:
            return f"Error: {data['error']}"
        logger.info(f'Raw response data: {data}')
        return str(data)
    
    @output
    @render.text
    def processed_response():
        data = split_data.get()
        if isinstance(data, dict) and 'sentence' in data:
            sentence = data['sentence']
            if isinstance(sentence, str):
                processed = ', '.join(sentence)
                logger.info(f'Processed data: {processed}')
                return processed
            else:
                logger.error(f'Unexpected data format for sentence: {sentence}')
                return "Unexpected data format for sentence"
        logger.error('No data to process or error occurred')
        return "No data to process or error occurred"

app = App(app_ui, server)

def main():
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.add_signal_handler(signal.SIGTERM, lambda: asyncio.create_task(server.shutdown()))
    loop.add_signal_handler(signal.SIGINT, lambda: asyncio.create_task(server.shutdown()))

    logger.info('Starting server...')
    loop.run_until_complete(server.serve())
    logger.info('Server stopped.')

if __name__ == "__main__":
    main()
