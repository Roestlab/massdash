"""
massdash/gui
~~~~~~~~~~~~
"""

import os
import click
import logging
import streamlit as st
from streamlit_javascript import st_javascript
from PIL import Image

# Constants
from massdash.constants import MASSDASH_ICON, MASSDASH_LOGO_LIGHT, MASSDASH_LOGO_DARK, OPENMS_LOGO
from massdash.constants import URL_TEST_SQMASS, URL_TEST_OSW, URL_TEST_PQP, URL_TEST_RAW_MZML, URL_TEST_DREAMDIA_REPORT
# Server
from massdash.server.ExtractedIonChromatogramAnalysisServer import ExtractedIonChromatogramAnalysisServer
from massdash.server.RawTargetedExtractionAnalysisServer import RawTargetedExtractionAnalysisServer
from massdash.server.SearchResultsAnalysisServer import SearchResultsAnalysisServer
# UI 
from massdash.ui.MassDashGUI import MassDashGUI
# Utils
from massdash.util import LOGGER, get_download_folder, download_file, reset_app, open_page

@click.command()
# @click.argument('args', default='args', type=str)
@click.option('--verbose', '-v', is_flag=True, help="Enables verbose mode.")
@click.option('--perf', '-t', is_flag=True, help="Enables measuring and tracking of performance.")
@click.option('--perf_output', '-o', default='MassDash_Performance_Report.txt', type=str, help="Name of the performance report file to writeout to.")
def main(verbose, perf, perf_output):     

    ###########################
    ## Logging
    LOGGER.name = 'MassDashGUIMain'
    if verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    LOGGER.setLevel(log_level) 
    
    # Confit
    st.set_page_config(page_title='MassDash', page_icon=MASSDASH_ICON, layout='wide')

    ###########################
    ## Main Container Window

    st.session_state.WELCOME_PAGE_STATE = True

    massdash_gui = MassDashGUI(verbose=verbose, perf=perf, perf_output=perf_output)
    if st.session_state.WELCOME_PAGE_STATE:
        massdash_gui.show_welcome_message()
    
    ###########################
    ## Sidebar Window

    # MassDash Sidebar Top Logo
    st_theme = st_javascript("""window.getComputedStyle(window.parent.document.getElementsByClassName("stApp")[0]).getPropertyValue("color-scheme")""")
    st.sidebar.image(MASSDASH_LOGO_LIGHT if st_theme == "dark" else MASSDASH_LOGO_DARK)
    cols = st.sidebar.columns(3)
    home_button = cols[0].button("🏠 Home", key="home_button", help="Return to the home page.", on_click=reset_app, use_container_width=True)
    MASSDASH_DOC_URL = "https://massdash.readthedocs.io/en/latest/index.html"
    documentation_button = cols[1].button("📖 Doc", key="documentation_button", help="Open the MassDash documentation in a new tab.", use_container_width=True, on_click=open_page, args=(MASSDASH_DOC_URL,))
    MASSDASH_GITHUB_URL = "https://github.com/Roestlab/massdash"
    github_button = cols[2].button("🐙 GitHub", key="github_button", help="Open the MassDash GitHub repository in a new tab.", use_container_width=True, on_click=open_page, args=(MASSDASH_GITHUB_URL,))

    st.sidebar.divider()

    if st.session_state.workflow == "xic_data" and st.session_state.clicked['load_toy_dataset_xic_data']:
        tmp_download_folder = get_download_folder() + "/massdash_example_dataset/"
        sqmass_file_path_input = tmp_download_folder + "/test_1.sqMass"
        download_file(URL_TEST_SQMASS, tmp_download_folder)
        osw_file_path = tmp_download_folder + "/test.osw"
        download_file(URL_TEST_OSW, tmp_download_folder)       
        
        massdash_gui.show_file_input_settings(osw_file_path, sqmass_file_path_input)
        
        # Remove welcome message container if dataset is loaded
        massdash_gui.welcome_container.empty()

        st.session_state.WELCOME_PAGE_STATE = False
        
    elif st.session_state.workflow == "raw_data" and st.session_state.clicked['load_toy_dataset_raw_data']:
        tmp_download_folder = get_download_folder() + "/massdash_example_dataset/"
        transition_list_file_path = tmp_download_folder + "/test.pqp"
        download_file(URL_TEST_PQP, tmp_download_folder)
        raw_file_path_input = tmp_download_folder +  "/test_raw_1.mzML"
        download_file(URL_TEST_RAW_MZML, tmp_download_folder)
        diann_report_file_path_input = tmp_download_folder + "/test.osw"
        download_file(URL_TEST_OSW, tmp_download_folder)
        feature_file_type = "OpenSWATH"
        # st.stop("Toy dataset not available yet.")
        massdash_gui.show_file_input_settings(diann_report_file_path_input, raw_file_path_input, transition_list_file_path, feature_file_type)
        
        # Remove welcome message container if dataset is loaded
        massdash_gui.welcome_container.empty()

        st.session_state.WELCOME_PAGE_STATE = False

    if st.session_state.workflow == "search_results_analysis" and st.session_state.clicked['load_toy_dataset_search_results_analysis']:
        tmp_download_folder = get_download_folder() + "/massdash_example_dataset/"
        feature_file_path = tmp_download_folder + "/test.osw"
        download_file(URL_TEST_OSW, tmp_download_folder)
        feature_file_type = "OpenSWATH"
        
        feature_file_path_3 = tmp_download_folder + "/test_dreamdia_report.tsv"
        download_file(URL_TEST_DREAMDIA_REPORT, tmp_download_folder)
        feature_file_type_3 = "DreamDIA"
        
        search_results_entries_dict = {'entry_1': {'search_results_file_path':          feature_file_path, 'search_results_exp_name': 'OSW', 'search_results_file_type': feature_file_type}, 
                                        'entry_3': {'search_results_file_path': feature_file_path_3, 'search_results_exp_name': 'DreamDIA', 'search_results_file_type': feature_file_type_3}}
        
        massdash_gui.show_file_input_settings(feature_file_entries_dict=search_results_entries_dict)
        
        # Remove welcome message container if dataset is loaded
        massdash_gui.welcome_container.empty()

        st.session_state.WELCOME_PAGE_STATE = False

    if st.session_state.workflow == "xic_data" and massdash_gui.osw_file_path!="*.osw" and massdash_gui.sqmass_file_path_input!="*.sqMass" and not st.session_state.clicked['load_toy_dataset_xic_data']:
        massdash_gui.show_file_input_settings(massdash_gui.osw_file_path, massdash_gui.sqmass_file_path_input)
        # Remove welcome message container if dataset is loaded
        massdash_gui.welcome_container.empty()
        st.session_state.WELCOME_PAGE_STATE = False

    if st.session_state.workflow == "raw_data" and massdash_gui.transition_list_file_path!="*.pqp" and massdash_gui.raw_file_path_input!="*.mzML" and not st.session_state.clicked['load_toy_dataset_raw_data']:
        massdash_gui.show_file_input_settings(massdash_gui.feature_file_path, massdash_gui.raw_file_path_input, massdash_gui.transition_list_file_path, massdash_gui.feature_file_type)
        # Remove welcome message container if dataset is loaded
        massdash_gui.welcome_container.empty()
        st.session_state.WELCOME_PAGE_STATE = False
        
    if st.session_state.workflow == "search_results_analysis" and massdash_gui.feature_file_entries is not None and not st.session_state.clicked['load_toy_dataset_search_results_analysis']:
        massdash_gui.show_file_input_settings(feature_file_entries_dict=massdash_gui.feature_file_entries)
        # Remove welcome message container if dataset is loaded
        massdash_gui.welcome_container.empty()
        st.session_state.WELCOME_PAGE_STATE = False
        
    if st.session_state.workflow == "xic_data" and not st.session_state.WELCOME_PAGE_STATE and massdash_gui.file_input_settings is not None:
        show_xic_exp = ExtractedIonChromatogramAnalysisServer(massdash_gui)
        show_xic_exp.main()
        
    if st.session_state.workflow == "raw_data" and not st.session_state.WELCOME_PAGE_STATE:
        show_raw_exp = RawTargetedExtractionAnalysisServer(massdash_gui)
        show_raw_exp.main()
        
    if st.session_state.workflow == "search_results_analysis" and not st.session_state.WELCOME_PAGE_STATE:
        show_search_results_analysis = SearchResultsAnalysisServer(massdash_gui)
        show_search_results_analysis.main()

    # OpenMS Siderbar Bottom Logo
    st.sidebar.image(OPENMS_LOGO)
    
if __name__ == "__main__":
    main()