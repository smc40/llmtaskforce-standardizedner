import pandas as pd
import numpy as np
import json
import re
import html
from sentence_transformers import SentenceTransformer, util
from load_meddra import load_embeddings

################
# optional - download model and save it locally
################
# model_name = 'FremyCompany/BioLORD-2023-C'
# model = SentenceTransformer(model_name, device='cpu')
# model.save('data/FremyCompany-BioLORD-2023-C')

################
# load prediction model from local copy
################
model_name = 'FremyCompany/BioLORD-2023-C'
model_path = 'data/FremyCompany-BioLORD-2023-C'
model = SentenceTransformer(model_path, device='cpu')
# model = SentenceTransformer(model_name, device='cpu')


# load embeddings and meddra dict from .pkl/.json file
meddra_embeddings = load_embeddings(model_name, level='Synonym')

# load meddra 
meddra_df = pd.read_csv('data/meddra26.1-import.csv', sep=';')


# meddra dict incl synonyms (optional) 
with open('data/meddra_dict.json', 'r') as f:
    meddra_dict = json.load(f)



def get_sim(text, n_terms=10, meddra_level='PT', output_mode='df'):
    """
    Get semantic similarity score at LLT level;
    Predict and return top n matches at requested MedDRA level

    text (str): the input text that will be compared to a list of MedDRA terms
    n_terms (int): the number of predictions to return
    meddra_level (str): the requested MedDRA hierarchy level, one of ['SOC', 'HLGT', 'HLT', 'PT', 'LLT']
    output mode (str): one of ['df', 'plot']
    meddra_dict (dict): temporary solution to index the meddra terms hierarchically at LLT level --> replace with df
    meddra_embeddings (list): list of numpy arrays containing the LLT embeddings

    output is returned to the main panel in app.py - one of ['text', 'df', 'plot']
    """

    embed = model.encode(text)
    sim = util.cos_sim(embed, np.array(meddra_embeddings))[0].tolist()

 
    outdf = pd.DataFrame(list(zip(meddra_df['Synonym'], meddra_df[meddra_level], sim)),
                         columns=['Synonym', meddra_level, 'score']).sort_values(by='score', ascending=False)

    outdf.drop_duplicates(subset=meddra_level, keep='first', inplace=True)
    outdf = outdf[[meddra_level, 'score']][:n_terms]

    if output_mode == 'df':
        outdf['score'] = round(outdf['score'], 3)
        return outdf

    else:
        raise TypeError('Invalid output mode specified!')
