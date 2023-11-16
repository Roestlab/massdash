import os
import streamlit as st
from PIL import Image

# Type hinting
from typing import List

# Internal UI modules
from massseer.ui.MassSeerGUI import MassSeerGUI
from massseer.sever.ExtractedIonChromatogramAnalysisServer import ExtractedIonChromatogramAnalysisServer

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

# welcome_container, load_toy_dataset, osw_file_path, sqmass_file_path_input = show_welcome_message()

massseer_gui = MassSeerGUI()
massseer_gui.show_welcome_message()
WELCOME_PAGE_STATE = True

# initialize load_toy_dataset key in clicked session state
# This is needed because streamlit buttons return True when clicked and then default back to False.
# See: https://discuss.streamlit.io/t/how-to-make-st-button-content-stick-persist-in-its-own-section/45694/2
if 'clicked' not in st.session_state:
    st.session_state.clicked  = {'load_toy_dataset':False}

###########################
## Sidebar Window

# MassSeer Sidebar Top Logo
st.sidebar.image(MASSSEER_LOGO)

st.sidebar.divider()

if st.session_state.clicked['load_toy_dataset']:
    sqmass_file_path_input = os.path.join(dirname, '..', 'tests', 'test_data', 'xics')
    osw_file_path = os.path.join(dirname, '..', 'tests', 'test_data', 'osw', 'test_data.osw')

    massseer_gui.show_file_input_settings(osw_file_path, sqmass_file_path_input)

    # Remove welcome message container if dataset is loaded
    massseer_gui.welcome_container.empty()

    WELCOME_PAGE_STATE = False

if massseer_gui.osw_file_path!="*.osw" and massseer_gui.sqmass_file_path_input!="*.sqMass" and not st.session_state.clicked['load_toy_dataset']:

    massseer_gui.show_file_input_settings(massseer_gui.osw_file_path, massseer_gui.sqmass_file_path_input)

    # Remove welcome message container if dataset is loaded
    massseer_gui.welcome_container.empty()
    
    WELCOME_PAGE_STATE = False

if not WELCOME_PAGE_STATE and  massseer_gui.file_input_settings.osw_file_path is not None and massseer_gui.file_input_settings.sqmass_file_path_input is not None:
    show_xic_exp = ExtractedIonChromatogramAnalysisServer(massseer_gui)
    show_xic_exp.main()

# OpenMS Siderbar Bottom Logo
st.sidebar.image(OPENMS_LOGO)