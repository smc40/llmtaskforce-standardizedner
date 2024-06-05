import signal
import asyncio
from shiny import App, ui, render
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
azure_openai_api_key = os.getenv('AZURE_OPENAI_API_KEY')
azure_openai_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')

logger.info(f'DICTIONARY_MATCH_URL: {dictionary_match_url}')
logger.info(f'AZURE_OPENAI_API_KEY: {azure_openai_api_key}')
logger.info(f'AZURE_OPENAI_ENDPOINT: {azure_openai_endpoint}')

app_ui = ui.page_fluid(
    ui.input_text("api_url", "Enter API URL", value=dictionary_match_url),
    ui.input_action_button("fetch", "Fetch Data"),
    ui.input_text("data_title", "Enter Title"),
    ui.input_text("data_body", "Enter Body"),
    ui.input_action_button("send", "Send Data"),
    ui.output_text_verbatim("response")
)

def server(input, output, session):
    @output
    @render.text
    def response():
        if input.fetch() > 0:
            api_url = input.api_url()
            logger.info(f'Fetch button clicked. API URL: {api_url}')
            try:
                res = requests.get(api_url)
                res.raise_for_status()
                data = res.json()
                logger.info(f'Data fetched successfully: {data}')
                # If you need to convert to a DataFrame
                df = pd.DataFrame(data)
                return df.to_string()
            except requests.exceptions.RequestException as e:
                logger.error(f'Error fetching data: {e}')
                return str(e)
        
        if input.send() > 0:
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