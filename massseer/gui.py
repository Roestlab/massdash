import os
import streamlit as st
from PIL import Image

# Internal UI modules
from massseer.ui.MassSeerGUI import MassSeerGUI
from massseer.server.ExtractedIonChromatogramAnalysisServer import ExtractedIonChromatogramAnalysisServer
from massseer.server.RawTargetedExtractionAnalysisServer import RawTargetedExtractionAnalysisServer

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
    #TODO: Create small toy example 
    transition_list_file_path = "/media/justincsing/ExtraDrive1/Documents2/Roest_Lab/Github/MassSeer/tests/test_data/josh/diann/K562-Library-Default_osw_6Frags_diann.tsv"
    raw_file_path_input = "/media/justincsing/ExtraDrive1/Documents2/Roest_Lab/Github/MassSeer/tests/test_data/josh/90min-SP-30cm-2um-K562-100nL-25ng_DIA_Slot1-5_1_550_3-7-2021.mzML"
    diann_report_file_path_input = "/media/justincsing/ExtraDrive1/Documents2/Roest_Lab/Github/MassSeer/tests/test_data/josh/diann/jsc718.5808924.0/report.tsv"
    
    massseer_gui.show_file_input_settings(diann_report_file_path_input, raw_file_path_input, transition_list_file_path)

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
    show_raw_exp = RawTargetedExtractionAnalysisServer(massseer_gui)
    show_raw_exp.main()


# OpenMS Siderbar Bottom Logo
st.sidebar.image(OPENMS_LOGO)