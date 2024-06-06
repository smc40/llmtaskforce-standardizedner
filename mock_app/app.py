import asyncio
import signal
from shiny import App, ui, render
from flask import Flask, request, jsonify
import uvicorn
import logging
from threading import Thread

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define Shiny UI
app_ui = ui.page_fluid(
    ui.h2("API Endpoint App")
)

# Define Flask app
flask_app = Flask(__name__)

@flask_app.route('/message', methods=['POST'])
def message():
    data = request.get_json()
    logger.info(f'Received message: {data}')
    if data:
        return jsonify({"response": f"Nice to meet you. You sent data {data}"})
    return jsonify({"error": "No message sent"}), 400

@flask_app.route('/data', methods=['GET'])
def data():
    logger.info('Data fetch requested')
    sample_data = {
        "data": [
            {"id": 1, "name": "Alice", "age": 30},
            {"id": 2, "name": "Bob", "age": 25},
            {"id": 3, "name": "Charlie", "age": 35}
        ]
    }
    return jsonify(sample_data)

# Define Shiny server function
def server(input, output, session):
    pass

app = App(app_ui, server)

# Function to run the Flask app
def run_flask():
    flask_app.run(host='0.0.0.0', port=8002)

# Function to run the Shiny app with Uvicorn
def run_shiny():
    config = uvicorn.Config(app, host="0.0.0.0", port=8003, log_level="info")
    server = uvicorn.Server(config)

    loop = asyncio.get_event_loop()
    loop.add_signal_handler(signal.SIGTERM, lambda: asyncio.create_task(server.shutdown()))
    loop.add_signal_handler(signal.SIGINT, lambda: asyncio.create_task(server.shutdown()))

    logger.info('Starting Shiny server...')
    loop.run_until_complete(server.serve())
    logger.info('Shiny server stopped.')

if __name__ == "__main__":
    # Run Flask app in a separate thread
    flask_thread = Thread(target=run_flask)
    flask_thread.start()

    # Run Shiny app
    run_shiny()
