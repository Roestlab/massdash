import os
import streamlit as st
from PIL import Image

# Internal UI modules
from massseer.ui.MassSeerGUI import MassSeerGUI
from massseer.server.ExtractedIonChromatogramAnalysisServer import ExtractedIonChromatogramAnalysisServer
from massseer.server.SearchResultsAnalysisServer import SearchResultsAnalysisServer

# Confit
# There currently is warning with the icon size for some reason, not sure why
# /home/justincsing/anaconda3/envs/py39/lib/python3.9/site-packages/PIL/IcoImagePlugin.py:316: UserWarning: Image was not the expected size
#   warnings.warn("Image was not the expected size")
massseer_icon = Image.open(os.path.join(os.path.dirname(__file__), 'assets/img/massseer.ico'))
st.set_page_config(page_title='MassSeer', page_icon=massseer_icon, layout='wide')

dirname = os.path.dirname(__file__)
MASSSEER_LOGO = os.path.join(dirname, 'assets/img/MassSeer_Logo_Full.png')
OPENMS_LOGO = os.path.join(dirname, 'assets/img/OpenMS.png')

###########################
## Main Container Window

st.session_state.WELCOME_PAGE_STATE = True

massseer_gui = MassSeerGUI()
if st.session_state.WELCOME_PAGE_STATE:
    massseer_gui.show_welcome_message()


###########################
## Sidebar Window

# MassSeer Sidebar Top Logo
st.sidebar.image(MASSSEER_LOGO)

st.sidebar.divider()

if st.session_state.workflow == "xic_data" and st.session_state.clicked['load_toy_dataset_xic_data']:
    sqmass_file_path_input = os.path.join(dirname, '..', 'tests', 'test_data', 'xics')
    osw_file_path = os.path.join(dirname, '..', 'tests', 'test_data', 'osw', 'test_data.osw')
    
    massseer_gui.show_file_input_settings(osw_file_path, sqmass_file_path_input)
    
    # Remove welcome message container if dataset is loaded
    massseer_gui.welcome_container.empty()

    st.session_state.WELCOME_PAGE_STATE = False
    
elif st.session_state.workflow == "raw_data" and st.session_state.clicked['load_toy_dataset_raw_data']:
    st.write("In development, coming soon!")
    pass

if st.session_state.workflow == "search_results_analysis" and st.session_state.clicked['load_toy_dataset_search_results_analysis']:
    # feature_file_path = os.path.join(dirname, '..', 'tests', 'test_data', 'osw', 'test_data.osw')
    feature_file_path = "/media/justincsing/ExtraDrive1/Documents2/Roest_Lab/Github/MassSeer/tests/test_data/spyogenes/openswath/osw/merged.osw"
    feature_file_type = "OpenSwath"
    
    search_results_entries_dict = {'entry_1': {'search_results_file_path': feature_file_path, 'search_results_exp_name': 'test_data', 'search_results_file_type': feature_file_type}}
    
    massseer_gui.show_file_input_settings(feature_file_entries_dict=search_results_entries_dict)
    
    # Remove welcome message container if dataset is loaded
    massseer_gui.welcome_container.empty()

    st.session_state.WELCOME_PAGE_STATE = False

if st.session_state.workflow == "xic_data" and massseer_gui.osw_file_path!="*.osw" and massseer_gui.sqmass_file_path_input!="*.sqMass" and not st.session_state.clicked['load_toy_dataset_xic_data']:

    massseer_gui.show_file_input_settings(massseer_gui.osw_file_path, massseer_gui.sqmass_file_path_input)

    # Remove welcome message container if dataset is loaded
    massseer_gui.welcome_container.empty()
    
    st.session_state.WELCOME_PAGE_STATE = False

if st.session_state.workflow == "xic_data" and not st.session_state.WELCOME_PAGE_STATE and massseer_gui.file_input_settings is not None:
    show_xic_exp = ExtractedIonChromatogramAnalysisServer(massseer_gui)
    show_xic_exp.main()
    
if st.session_state.workflow == "raw_data" and not st.session_state.WELCOME_PAGE_STATE:
    st.write("In development, coming soon!")
    pass

if st.session_state.workflow == "search_results_analysis" and not st.session_state.WELCOME_PAGE_STATE:
    show_search_results_analysis = SearchResultsAnalysisServer(massseer_gui)
    show_search_results_analysis.main()

# OpenMS Siderbar Bottom Logo
st.sidebar.image(OPENMS_LOGO)