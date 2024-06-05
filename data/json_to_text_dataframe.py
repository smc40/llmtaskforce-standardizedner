import json
import pandas as pd

# Function to load JSON data from a file
def load_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

# Function to extract text and signals from JSON data
def extract_text_and_signals(data):
    text_entities = []
    for doc in data:
        # for each entity
        if '_textEntities' in doc:
            for entity in doc['_textEntities']:
                # get text of entity
                text_value = entity['text']
                # get text value from all signals and medicinalProducts values for the entity
                signals = [signal['text'] for signal in entity.get('signals', [])]
                products = [signal['text'] for signal in entity.get('medicinalProducts', [])]

                # save to dict to turn into dataframe
                text_entities.append({'text': text_value, 'products': products, 'signals': signals})
    return text_entities

# Load JSON data from a file
file_path = 'groundtruth.json'  # Replace with your JSON file path
data = load_json(file_path)

# Extract text and signals
text_entities = extract_text_and_signals(data)

# Create DataFrame
df = pd.DataFrame(text_entities)