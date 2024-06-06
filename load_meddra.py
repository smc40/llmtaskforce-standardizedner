import pickle
import pandas as pd
from sentence_transformers import SentenceTransformer, util
from tqdm import tqdm
import json


def load_embeddings(model_name, level):
    """"
    Preload MedDRA embeddings at the requested level.
    If the embeddings for this model could not be found, they are calculated manually

    model_name (str): (transformer) model used to vectorize the data.
    level (str): the level in the MedDRA Hierarchy. ['SOC', 'HLGT', 'HLT', 'PT', 'LLT']
    return meddra_embeddings (list): list of numpy arrays.
    """

    with open(f'data/{level.upper()}_embeddings_' + model_name.replace('/', '-') + '.pkl', 'rb') as pkl:
        meddra_embeddings = pickle.load(pkl)

    return meddra_embeddings


###################
def load_meddra_df(kind='import'):
    # kind = either 'Synonym' or 'Import'
    if kind.lower() == 'import':
        df = pd.read_csv('data/meddra26.1-import.csv', sep=';', usecols=['SOCName', 'HLTGName', 'HLTName', 'PTName', 'LLTName'])
        df.rename(columns={'SOCName': 'SOC', 'HLTGName': 'HLGT', 'HLTName': 'HLT', 'PTName': 'PT', 'LLTName': 'LLT'},
                  inplace=True)
        return df
    elif kind.lower() == 'synonym':
        df = pd.read_csv('data/taxonomy-syno.csv', sep=';', usecols=['SOC', 'HLGT', 'HLT', 'PT', 'LLT', 'is_synonym', 'Synonym'])
        return df
    else:
        return 'Invalid taxonomy specified! Choose from "Import" or "Synonym"!'


def create_new_embeddings(model_name, level):
    model = SentenceTransformer(model_name, device='cpu')
    df = load_meddra_df()
    terms = list(df[level].unique())
    meddra_embeddings = []
    print(f'Vectorizing terms for level: {level}')
    for term in tqdm(terms):
        embed = model.encode(term)
        meddra_embeddings.append(embed)
    with open(f'data/embed/{level}_embeddings_' + model_name.replace('/', '-') + '.pkl', 'wb') as pkl:
        pickle.dump(meddra_embeddings, pkl)

    with open(f'data/embed/_embeddings_' + model_name.replace('/', '-') + '.pkl', 'wb') as pkl:
        pickle.dump(meddra_embeddings, pkl)
    print(f'Finished calculating embeddings for MedDRA level {level.upper()}!')


