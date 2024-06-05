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


    with open(f'data/embed/{level.upper()}_embeddings_' + model_name.replace('/', '-') + '.pkl', 'rb') as pkl:
        meddra_embeddings = pickle.load(pkl)

        # for the shiny app, only allow loading the embedding files locally.
    # except FileNotFoundError:
    #     return f'Failed loading the embedding file from: data/embed/{level.upper()}_embeddings_{subset}' + model_name.replace(
    #         '/', '-') + '.pkl'

    ########### OPTIONAL - VECTORIZE ALL MEDDRA TERMS FOR ALL LEVELS 
    # ---------------------------------------------------------------------------------------
    return meddra_embeddings


###################
def load_meddra_df(kind='Synonym'):
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


###################
# small pipeline to create new embeddings for a given model & meddra dataset
#
# model_names = ['FremyCompany/BioLORD-2023-C']
# meddra_levels = ['SOC', 'HLGT', 'HLT', 'PT', 'LLT']
#
#
# for new_model_name in model_names:
#     print(f'Started processing for {new_model_name}')
#     for meddra_level in meddra_levels:
#         create_new_embeddings(model_name=new_model_name, level=meddra_level)
#
# #