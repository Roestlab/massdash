"""
massdash/gui
~~~~~~~~~~~~
"""

import os
import click
import logging
import streamlit as st
from PIL import Image

# Server
from massdash.server.ExtractedIonChromatogramAnalysisServer import ExtractedIonChromatogramAnalysisServer
from massdash.server.RawTargetedExtractionAnalysisServer import RawTargetedExtractionAnalysisServer
from massdash.server.SearchResultsAnalysisServer import SearchResultsAnalysisServer
# UI 
from massdash.ui.MassDashGUI import MassDashGUI
# Utils
from massdash.util import LOGGER, get_download_folder, download_file

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
    
    if 'perf_on' not in st.session_state:
        st.session_state['perf_on'] = perf 
    if 'perf_counter' not in st.session_state:
        st.session_state['perf_counter'] = 200

    # Confit
    MASSDASH_ICON = Image.open(os.path.join(os.path.dirname(__file__), 'assets/img/MassDash_Logo.ico'))
    st.set_page_config(page_title='MassDash', page_icon=MASSDASH_ICON, layout='wide')

    dirname = os.path.dirname(__file__)

    MASSDASH_LOGO = os.path.join(dirname, 'assets/img/MassDash_Logo_Dark.png')
    OPENMS_LOGO = os.path.join(dirname, 'assets/img/OpenMS.png')

    ###########################
    ## Main Container Window

    st.session_state.WELCOME_PAGE_STATE = True

    massdash_gui = MassDashGUI(verbose==verbose, perf==perf, perf_output=perf_output)
    if st.session_state.WELCOME_PAGE_STATE:
        massdash_gui.show_welcome_message()

    ###########################
    ## Sidebar Window

    # MassDash Sidebar Top Logo
    st.sidebar.image(MASSDASH_LOGO)

    st.sidebar.divider()

    if st.session_state.workflow == "xic_data" and st.session_state.clicked['load_toy_dataset_xic_data']:
        tmp_download_folder = get_download_folder() + "/massdash_example_dataset/"
        sqmass_file_path_input = tmp_download_folder + "/test_chrom_1.sqMass"
        url_test_sqmass = "https://github.com/Roestlab/massdash/raw/dev/test/test_data/xics/test_chrom_1.sqMass"
        download_file(url_test_sqmass, tmp_download_folder)
        osw_file_path = tmp_download_folder + "/test_data.osw"
        url_test_osw = "https://github.com/Roestlab/massdash/raw/dev/test/test_data/osw/test_data.osw"
        download_file(url_test_osw, tmp_download_folder)       
        
        massdash_gui.show_file_input_settings(osw_file_path, sqmass_file_path_input)
        
        # Remove welcome message container if dataset is loaded
        massdash_gui.welcome_container.empty()

        st.session_state.WELCOME_PAGE_STATE = False
        
    elif st.session_state.workflow == "raw_data" and st.session_state.clicked['load_toy_dataset_raw_data']:
        tmp_download_folder = get_download_folder() + "/massdash_example_dataset/"
        transition_list_file_path = tmp_download_folder + "/test.pqp"
        url_test_pqp = "https://github.com/Roestlab/massdash/raw/dev/test/test_data/example_dia/openswath/lib/test.pqp"
        download_file(url_test_pqp, tmp_download_folder)
        raw_file_path_input = tmp_download_folder +  "/test_raw_1.mzML"
        url_test_raw_mzml = "https://github.com/Roestlab/massdash/raw/dev/test/test_data/example_dia/raw/test_raw_1.mzML"
        download_file(url_test_raw_mzml, tmp_download_folder)
        diann_report_file_path_input = tmp_download_folder + "/test.osw"
        url_test_osw = "https://github.com/Roestlab/massdash/raw/dev/test/test_data/example_dia/openswath/osw/test.osw"
        download_file(url_test_osw, tmp_download_folder)
        feature_file_type = "OpenSWATH"
        # st.stop("Toy dataset not available yet.")
        massdash_gui.show_file_input_settings(diann_report_file_path_input, raw_file_path_input, transition_list_file_path, feature_file_type)
        
        # Remove welcome message container if dataset is loaded
        massdash_gui.welcome_container.empty()

        st.session_state.WELCOME_PAGE_STATE = False

    if st.session_state.workflow == "search_results_analysis" and st.session_state.clicked['load_toy_dataset_search_results_analysis']:
        tmp_download_folder = get_download_folder() + "/massdash_example_dataset/"
        feature_file_path = tmp_download_folder + "/test.osw"
        url_test_osw = "https://github.com/Roestlab/massdash/blob/dev/test/test_data/example_dia/openswath/osw/test.osw"
        download_file(url_test_osw, tmp_download_folder)
        feature_file_type = "OpenSWATH"
        
        feature_file_path_3 = tmp_download_folder + "/test_dreamdia_report.tsv"
        url_test_dreamdia_report = "https://github.com/Roestlab/massdash/blob/dev/test/test_data/example_dia/dreamdia/test_dreamdia_report.tsv"
        download_file(url_test_dreamdia_report, tmp_download_folder)
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