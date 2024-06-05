from shiny import *
from htmltools import HTML, div, Tag
import pandas as pd
#from translate_input import translate_description
from predict_meddra import get_sim
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
    ui.panel_title("MedDRA AutoCoder"),
    ui.navset_tab_card(
        ui.nav('Predict',
               ui.layout_sidebar(
                   ui.panel_sidebar(
                       # ui.input_radio_buttons('do_translate', 'Translate input to English (recommended)', translation_options, selected="Yes"),
                       ui.input_select('meddra_level', 'MedDRA level', meddra_levels, selected='PT', multiple=False),
                       ui.input_slider('n_terms', 'Number of predictions', min=1, max=10, value=5),
                       ui.input_radio_buttons('output_mode', 'Output Type', output_modes, selected='df'),
                       "\n",
                       ui.input_text_area('textinput', 'Description to analyse', rows=4),
                       ui.input_action_button(id="predict_term", label="Predict", class_='btn-success'),
                       "\n",
                       width=3
                   ),

                   ui.panel_main(
                       ui.panel_conditional(
                           "input.predict_term > 0 && input.output_mode === 'df' && input.textinput != ''",
                           ui.output_table("df_output"),
                       ),

                       width=8  # smaller (8 instead of 9) to smoothen right edge
                   )
               )
        ),
        selected='Predict',
    ),
    title='MedDRA AutoCoder',
)


#####################################################################
# RENDER (Server)
#####################################################################
def server(input, output, session):

    # define reactive variables: n_terms, ask_feedback, send_feedback
    val = reactive.Value(5)
    @reactive.Effect
    @reactive.event(input.n_terms)
    def _():
        val.set(input.n_terms())

    #############################
    # create output using various methods

    @output()
    @render.table
    @reactive.event(input.predict_term)
    async def df_output():
        data = {
            'Name': ['Alice', 'Bob', 'Charlie', 'David', 'Eva'],
            'Age': [24, 27, 22, 32, 29],
            'City': ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix'],
            'Salary': [70000, 80000, 60000, 90000, 75000]
        }
        results = pd.DataFrame(data)
        results = get_sim(input.textinput(),
                            n_terms=val.get(), meddra_level=input.meddra_level(), output_mode=input.output_mode())
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



