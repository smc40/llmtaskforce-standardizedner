import pickle
import pandas as pd
from sentence_transformers import SentenceTransformer, util
from tqdm import tqdm
import json


def load_embeddings(model_name, level):
    """"
    Load precalculated MedDRA embeddings from a local .pkl file
    If the embeddings for this model could not be found, they are calculated manually

    model_name (str): (transformer) model used to vectorize the data.
    level (str): the level in the MedDRA Hierarchy. ['SOC', 'HLGT', 'HLT', 'PT', 'LLT']
    return meddra_embeddings (list or numpy array)
    """

    with open(f'data/{level.upper()}_embeddings_' + model_name.replace('/', '-') + '.pkl', 'rb') as pkl:
        meddra_embeddings = pickle.load(pkl)

    return meddra_embeddings


###################
def load_meddra_df(version='27.0'):
    """Requires a .csv file containing all MedDRA terms and levels
    The MedDRA hierarchy should only contain 1) current terms, and 2) terms from the Default SOC only"""
    try:
        df = pd.read_csv(f'data/meddra{version}-import.csv', sep=';', usecols=['SOCName', 'HLTGName', 'HLTName', 'PTName', 'LLTName'])
        df.rename(columns={'SOCName': 'SOC', 'HLTGName': 'HLGT', 'HLTName': 'HLT', 'PTName': 'PT', 'LLTName': 'LLT'},
            inplace=True)
        return df
    except Exception as e:
        return 'Could not load the MedDRA file!'


def create_new_embeddings(model_name, level):
    """Optional function to create MedDRA embeddings and store them in a .pkl file
    This process can be executed for each level in the MedDRA hierarchy (SOC, HLGT, HLT, PT, LLT)"""
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


###################
# run this to create new embeddings for a given model & MedDRA file
#
# model_names = ['FremyCompany/BioLORD-2023-C']
# meddra_levels = ['SOC', 'HLGT', 'HLT', 'PT', 'LLT']
#
# for new_model_name in model_names:
#     print(f'Started processing for {new_model_name}')
#     for meddra_level in meddra_levels:
#         create_new_embeddings(model_name=new_model_name, level=meddra_level)
#
