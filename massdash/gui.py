import os
import click
import logging
import streamlit as st
from PIL import Image

# Server
from server.ExtractedIonChromatogramAnalysisServer import ExtractedIonChromatogramAnalysisServer
from server.RawTargetedExtractionAnalysisServer import RawTargetedExtractionAnalysisServer
# UI 
from ui.MassDashGUI import MassDashGUI
# Utils
from util import LOGGER

@click.command()
# @click.argument('args', default='args', type=str)
@click.option('--verbose', '-v', is_flag=True, help="Enables verbose mode.")
@click.option('--perf', '-t', is_flag=True, help="Enables measuring and tracking of performance.")
@click.option('--perf_output', '-o', default='MassSeer_Performance_Report.txt', type=str, help="Name of the performance report file to writeout to.")
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

    MASSDASH_LOGO = os.path.join(dirname, 'assets/img/MassDash_Logo.png')
    OPENMS_LOGO = os.path.join(dirname, 'assets/img/OpenMS.png')

    ###########################
    ## Main Container Window

    st.session_state.WELCOME_PAGE_STATE = True

    massdash_gui = MassDashGUI(verbose==verbose, perf==perf, perf_output=perf_output)
    if st.session_state.WELCOME_PAGE_STATE:
        massdash_gui.show_welcome_message()


    ###########################
    ## Sidebar Window

    # MassSeer Sidebar Top Logo
    st.sidebar.image(MASSDASH_LOGO)

    st.sidebar.divider()

    if st.session_state.workflow == "xic_data" and st.session_state.clicked['load_toy_dataset_xic_data']:
        sqmass_file_path_input = os.path.join(dirname, '..', 'tests', 'test_data', 'xics')
        osw_file_path = os.path.join(dirname, '..', 'tests', 'test_data', 'osw', 'test_data.osw')
        
        massdash_gui.show_file_input_settings(osw_file_path, sqmass_file_path_input)
        
        # Remove welcome message container if dataset is loaded
        massdash_gui.welcome_container.empty()

        st.session_state.WELCOME_PAGE_STATE = False
        
    elif st.session_state.workflow == "raw_data" and st.session_state.clicked['load_toy_dataset_raw_data']:
        #TODO: Create small toy example 
        transition_list_file_path = ""
        raw_file_path_input = ""
        diann_report_file_path_input = ""
        feature_file_type = ""
        st.stop("Toy dataset not available yet.")
        massdash_gui.show_file_input_settings(diann_report_file_path_input, raw_file_path_input, transition_list_file_path, feature_file_type)

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

    if st.session_state.workflow == "xic_data" and not st.session_state.WELCOME_PAGE_STATE and massdash_gui.file_input_settings is not None:
        show_xic_exp = ExtractedIonChromatogramAnalysisServer(massdash_gui)
        show_xic_exp.main()
        
    if st.session_state.workflow == "raw_data" and not st.session_state.WELCOME_PAGE_STATE:
        show_raw_exp = RawTargetedExtractionAnalysisServer(massdash_gui)
        show_raw_exp.main()


    # OpenMS Siderbar Bottom Logo
    st.sidebar.image(OPENMS_LOGO)
    
if __name__ == "__main__":
    main()