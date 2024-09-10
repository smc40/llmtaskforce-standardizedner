import pandas as pd
import numpy as np
import json
import re
import html
from sentence_transformers import SentenceTransformer, util
from load_meddra import load_meddra_df, load_embeddings

################
# load prediction model, from HF/cache or from local folder
################
model_name = 'FremyCompany/BioLORD-2023-C'
model = SentenceTransformer(model_name, device='cpu')
# model.save('data/FremyCompany-BioLORD-2023-C')
# model_path = 'data/FremyCompany-BioLORD-2023-C'
# model = SentenceTransformer(model_path, device='cpu')

# load precalculated embeddings from .pkl file
meddra_embeddings = load_embeddings(model_name, level='LLT')

# load meddra
# meddra_df = pd.read_csv('data/meddra27.0-import.csv', sep=';', dtype='str', usecols=['SOC','HLGT','HLT','PT','LLT'])
meddra_df = load_meddra_df(version='27.0')


def get_sim(text, n_terms=10, meddra_level='PT'):
    """
    Get semantic similarity score at LLT level;
    Predict and return top n matches at requested MedDRA level

    text (str): the input text that will be compared to a list of MedDRA terms. After optional translation
    n_terms (int): the number of predictions to return
    meddra_level (str): the requested MedDRA hierarchy level, one of ['SOC', 'HLGT', 'HLT', 'PT', 'LLT']
    output is returned to the main panel in app.py as a df/table
    """

    embed = model.encode(text)
    sim = util.cos_sim(embed, np.array(meddra_embeddings))[0].tolist()
 
    outdf = pd.DataFrame(list(zip(meddra_df['LLT'], meddra_df[meddra_level], sim)),
                         columns=['LLT', meddra_level, 'score']).sort_values(by='score', ascending=False)

    outdf.drop_duplicates(subset=meddra_level, keep='first', inplace=True)
    outdf = outdf[[meddra_level, 'score']][:n_terms]

    outdf['score'] = round(outdf['score'], 3)
    return outdf
