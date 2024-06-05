import signal
import asyncio
from shiny import App, ui, render
import requests
import pandas as pd
import uvicorn

app_ui = ui.page_fluid(
    ui.input_text("api_url", "Enter API URL", value="https://jsonplaceholder.typicode.com/posts"),
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
            try:
                res = requests.get(api_url)
                res.raise_for_status()
                data = res.json()
                # If you need to convert to a DataFrame
                df = pd.DataFrame(data)
                return df.to_string()
            except requests.exceptions.RequestException as e:
                return str(e)
        
        if input.send() > 0:
            api_url = input.api_url()
            data = {
                "title": input.data_title(),
                "body": input.data_body(),
                "userId": 1  # JSONPlaceholder API requires a userId for POST requests
            }
            try:
                res = requests.post(api_url, json=data)
                res.raise_for_status()
                return res.json()
            except requests.exceptions.RequestException as e:
                return str(e)

app = App(app_ui, server)

def main():
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)

    loop = asyncio.get_event_loop()
    loop.add_signal_handler(signal.SIGTERM, lambda: asyncio.create_task(server.shutdown()))
    loop.add_signal_handler(signal.SIGINT, lambda: asyncio.create_task(server.shutdown()))

    loop.run_until_complete(server.serve())

if __name__ == "__main__":
    main()
