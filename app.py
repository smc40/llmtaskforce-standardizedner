from shiny import *
from htmltools import HTML, div, Tag
import pandas as pd
from translate_input import translate_description
from predict_meddra import get_sim
from signal_detection_function import detect_signals
# from load_meddra import load_embeddings
# import shiny.module

#####################################################################
# UI
#####################################################################

meddra_levels = ['SOC', 'HLGT', 'HLT', 'PT', 'LLT', 'Synonym']
output_modes = {"df": "Table"}
translation_options = {"Yes": "Yes",
                       "No": "No"}

app_ui = ui.page_fluid(
    ui.panel_title("Standardized NER"),
    ui.navset_tab_card(
        ui.nav('Predict',
               ui.layout_sidebar(
                   ui.panel_sidebar( 
                       ui.input_select('meddra_level', 'MedDRA level', meddra_levels, selected='PT', multiple=False),
                       ui.input_slider('n_terms', 'Number of predictions', min=1, max=5, value=1),
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

                        # smaller (8 instead of 9) to smoothen right edge
                   ),

                #    ui.panel_main(
                #        

                #        width=3  # smaller (8 instead of 9) to smoothen right edge
                #    )
               )
        ),
        selected='Predict',
    ),
    title='Standardized NER',
)


#####################################################################
# RENDER (Server)
#####################################################################
def server(input, output, session):

    # Define reactive variables
    val = reactive.Value(1)


    @reactive.Effect
    @reactive.event(input.n_terms)
    def _():
        val.set(input.n_terms())

    prompting_results = detect_signals(input.textinput())

    if not isinstance(prompting_results, list):
        prompting_results = ["Not valid list"]

    search_data = {"Found EDRs LLM": prompting_results,
                    "Found EDRs MedDra": ["EDR1", "EDR2", "EDR3"]}

    
    # Render the data grid
    @output
    @render.table
    def temp_data():
        return pd.DataFrame(search_data)

    @output()
    @render.table
    @reactive.event(input.predict_term)
    async def df_output():
        # data = {
        #     'EDR': ['Alice', 'Bob', 'Charlie', 'David', 'Eva'],
        #     'Score': [24, 27, 22, 32, 29],
        # }
        # results = pd.DataFrame(data)

        translations = [translate_description(x) for x in prompting_results]
        print(translations)
        results = [get_sim(x, n_terms=val.get(), meddra_level=input.meddra_level())
                   for x in translations]
        results = pd.concat(results)  # list of df's to df

        return results


    # general return function -> can be used for (local) logging
    return {
        'df_output': df_output
    }


#####################################################################
# App
#####################################################################
app = App(app_ui, server, debug=True)

##################
# run this in python console after defining app
# #################
# run_app(host='127.0.0.1', port=8000, autoreload_port=0, reload=False,  # ws_max_size=16777216,
#         log_level=None,
#         app_dir='.', #app='mac',
#         factory=False, launch_browser=True)


