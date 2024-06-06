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

meddra_levels = ['SOC', 'HLGT', 'HLT', 'PT', 'LLT', 'Synonym']
output_modes = {"df": "Table"}
translation_options = {"Yes": "Yes", "No": "No"}

app_ui = ui.page_fluid(
    ui.panel_title("MedDRA AutoCoder"),
    ui.navset_tab_card(
        ui.nav('Predict',
               ui.layout_sidebar(
                   ui.panel_sidebar(
                       ui.input_select('meddra_level', 'MedDRA level', meddra_levels, selected='PT', multiple=False),
                       ui.input_slider('n_terms', 'Number of predictions', min=1, max=10, value=5),
                       "\n",
                       ui.input_text_area('textinput', 'Description to analyse', rows=4),
                       ui.input_action_button(id="predict_term", label="Predict", class_='btn-success'),
                       "\n",
                       ui.input_dark_mode(),
                       width=3
                   ),
                   ui.layout_columns(
                       ui.panel_conditional(
                           "input.predict_term > 0 && input.textinput != ''",
                           ui.output_table("temp_data"),
                           width=2,
                       ),
                       ui.panel_conditional(
                           "input.predict_term > 0 && input.textinput != ''",
                           ui.output_table("df_output"),
                           width=4,
                       ),
                   ),
               )
        ),
        selected='Predict',
    ),
    title='MedDRA AutoCoder',
)


def server(input, output, session):
    fetch_state = {'count': 0}
    send_state = {'count': 0}
    fetched_data = reactive.Value(None)  # Use reactive value for fetched data
    
    @output
    @render.text
    def response():
        
        if input.predict() > fetch_state['count']:
            send_state['count'] = input.predict()
            api_url = dictionary_match_url_fetch
            data = {
                "title": "static title from shiny app",
                "body": input.textinput(),
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
            


    # Define reactive variables
    val = reactive.Value(5)

    @reactive.Effect
    @reactive.event(input.n_terms)
    def _():
        val.set(input.n_terms())

    # Example data to display in the datagrid
    example_data = {"Found EDRs LLM": ["EDR1", "EDR2", "EDR3"],
                    "Found EDRs MedDra": ["EDR1", "EDR2", "EDR3"]}
    
    # Render the data grid
    @output
    @render.table
    def temp_data():
        return pd.DataFrame(example_data)

    @output()
    @render.table
    @reactive.event(input.predict_term)
    async def df_output():
        data = {
            "description": input.textinput(),
            "n_terms": val.get(),
            "meddra_level": input.meddra_level()
        }
        
        logger.info(f'Sending data to API: {data}')
        
        try:
            headers = {"Authorization": f"Bearer {azure_openai_api_key}"}
            res = requests.post(dictionary_match_url, json=data, headers=headers)
            res.raise_for_status()
            result_data = res.json()
            logger.info(f'Data received from API: {result_data}')
            
            # Ensure the result data is in a format that can be converted into a DataFrame
            if isinstance(result_data, dict) and all(isinstance(v, list) for v in result_data.values()):
                results = pd.DataFrame(result_data)
            else:
                # Handle cases where the API response is not as expected
                results = pd.DataFrame({"Response": [str(result_data)]})
                
        except requests.exceptions.RequestException as e:
            logger.error(f'Error sending data: {e}')
            results = pd.DataFrame({"Error": [str(e)]})
        
        return results

    # general return function -> can be used for (local) logging
    return {
        'df_output': df_output
    }
    


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
