from shiny import *
import shiny
from htmltools import HTML, div, Tag
import pandas as pd
from translate_input import clean_text, detect_language, translate_description
from predict_meddra import get_sim
from signal_detection_function import detect_signals
# from load_meddra import load_embeddings
# import shiny.module

#####################################################################
# UI
#####################################################################

meddra_levels = ['SOC', 'HLGT', 'HLT', 'PT', 'LLT']
output_modes = {"df": "Table"}
multiple_adrs = {"Yes": "Yes",
                 "No": "No"}

models_to_select = ['Claude-3-Haiku (Anthropic)',
                    'Claude-3-5-Sonnet (Anthropic)',  # default
                    'GPT-4o (OpenAI)',
                    'GPT-4o-mini (OpenAI)',
                    'GPT-4 (OpenAI)'
                    ]


######################################################################


app_ui = ui.page_fluid(
    # First, specify CSS for table layouts
    ui.tags.head(
        ui.tags.style(
            """
            .custom-table-width-2 {
                width: 50%;
                max-width: 50%;
            }
            .custom-table-width-3 {
                width: 75%;
                max-width: 75%;
            }
            .custom-table-width-2 table, .custom-table-width-3 table {
                width: 100%;
            }
            """
        )
    ),

    ui.panel_title("Standardized NER"),
    shiny.ui.navset_card_tab(
        shiny.ui.nav_panel('Predict',
                ui.layout_sidebar(
                   ui.panel_sidebar(
                       ui.input_select('meddra_level', 'MedDRA level', meddra_levels, selected='PT', multiple=False),
                       ui.input_slider('n_terms', 'Number of predictions per ADR', min=1, max=5, value=1),
                       ui.input_radio_buttons('extract_multiple', 'Multi-ADR extraction?',
                                              choices=multiple_adrs, selected='Yes'),

                       # ui.input_select('model_selected', 'LLM', models_to_select,
                       #                selected='Claude-3-5-Sonnet (Anthropic)', multiple=False),

                       ui.output_ui("conditional_model_select"),
                       "\n",
                       ui.input_text_area('textinput', 'Text to extract ADRs from', rows=4),
                       ui.input_action_button(id="predict_term", label="Predict", class_='btn-success'),
                       "\n",
                       ui.input_dark_mode(), 
                       width=4
                   ),

                   ui.layout_columns(
                       ui.panel_conditional(
                           "input.predict_term > 0 && input.textinput != ''",
                           ui.div(
                               ui.output_table("show_search_data"), class_="custom-table-width-2"
                           ),
                           width=1,
                       ),
                       
                       ui.panel_conditional(
                           "input.predict_term > 0 && input.textinput != ''",
                           ui.div(
                               ui.output_table("df_output"), class_="custom-table-width-3"
                           ),
                           width=2,
                       ),
                   ),
               )
        ),
        selected='Predict',
    ),
    title='LLM Task Force Standardized NER',
)


#####################################################################
# RENDER (Server)
#####################################################################
def server(input, output, session):

    #######################
    # first define reactive variables/calculations
    @reactive.Calc
    def n_terms():
        return input.n_terms()

    @reactive.Effect
    @reactive.event(input.extract_multiple)
    def update_n_terms():
        if input.extract_multiple() == "Yes":
            ui.update_slider("n_terms", value=1)
        else:
            ui.update_slider("n_terms", value=5)

    @reactive.Calc
    def selected_model():
        return input.model_selected()

    # conditional display of LLM selection
    @render.ui
    def conditional_model_select():
        if input.extract_multiple() == "Yes":
            return ui.input_select("model_selected", "LLM", models_to_select, selected='Claude-3-5-Sonnet (Anthropic)',
                                   multiple=False)
        else:
            return ui.div()

    #############################
    # create output using various methods
    @reactive.Calc
    def search_data():
        multi_adr = input.extract_multiple()
        if multi_adr.lower() == 'yes':
            return detect_signals(input.textinput(), selected_model=selected_model())
        elif multi_adr.lower() == 'no':
            return [input.textinput()]  # convert input text to list (= no LLM processing required)
        else:
            return []

    @output()
    @render.table
    @reactive.event(input.predict_term)
    def show_search_data():
        search_results = search_data()
        return pd.DataFrame(search_results, columns=['Detected ADRs']) if search_results else pd.DataFrame(
            columns=['No ADRs detected!'])

    @output()
    @render.table
    @reactive.event(input.predict_term)
    def df_output():
        multi_adr = input.extract_multiple()

        if multi_adr.lower() == 'yes':
            prompting_results = search_data()
            # prompting_results = [x for x in prompting_results if x]  # remove rows with whitespace
            if not prompting_results or prompting_results == ['No ADRs detected!']:
                return pd.DataFrame(['No ADRs detected!'])

            detected_language = detect_language(
                input.textinput())  # detect language based on cleaned input text, not just the extracted terms
            cleaned_text = [clean_text(x) for x in prompting_results]
            translations = [translate_description(input_text=x, detected_lang=detected_language) for x in cleaned_text]

            if not translations:
                return pd.DataFrame(columns=['No ADRs detected!'])

            results = []
            for text in translations:
                result = get_sim(text, n_terms=n_terms(), meddra_level=input.meddra_level())
                if not result.empty:
                    results.append(result)

            if not results:
                return pd.DataFrame(columns=['No ADRs detected!'])

            try:
                return pd.concat(results, ignore_index=True)  # list of df's to df
            except ValueError:
                return pd.DataFrame(columns=['No ADRs detected!'])

        elif multi_adr.lower() == 'no':  # faster processing for single ADR
            detected_language = detect_language(input.textinput())
            cleaned_text = clean_text(input.textinput())
            translated_text = translate_description(cleaned_text, detected_lang=detected_language)

            if not translated_text:
                return pd.DataFrame(columns=['No ADRs detected!'])

            results = get_sim(translated_text, n_terms=n_terms(), meddra_level=input.meddra_level())
            return results

    # general return function -> can be used for (local) logging
    return {
        # 'search_data': show_search_data,
        'df_output': df_output
    }


#####################################################################
# App
#####################################################################
app = App(app_ui, server, debug=True)

##################
# RUN APP - run the lines below within the terminal/python console, after loading the app into memory (= all code above)
##################
# run_app(host='127.0.0.1', port=8000, autoreload_port=0, reload=False,  # ws_max_size=16777216,
#         log_level=None,
#         app_dir='.', #app='mac',
#         factory=False, launch_browser=True)


