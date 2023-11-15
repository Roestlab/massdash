import streamlit as st

import os
from PIL import Image

# Type hinting
from typing import List

# Internal UI modules
from massseer.ui.MassSeerGUI import MassSeerGUI
from massseer.sever.ExtractedIonChromatogramAnalysisServer import ExtractedIonChromatogramAnalysisServer
from massseer.file_handling_ui import process_osw_file, get_sqmass_files
from massseer.plotting_ui import ChromatogramPlotSettings
from massseer.algo_ui import AlgorithmUISettings

# Internal server modules
from massseer.data_loader import process_many_files
from massseer.plotter import Plotter, draw_many_chrom_data, draw_many_consensus_chrom
from massseer.chromatogram_data_handling import get_chrom_data_limits, get_chrom_data_global, compute_consensus_chromatogram
from massseer.peak_picking import perform_chromatogram_peak_picking

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

if massseer_gui.osw_file_path!="*.osw" and massseer_gui.sqmass_file_path_input!="*.sqMass" and not st.session_state.clicked['load_toy_dataset']:

    massseer_gui.show_file_input_settings(massseer_gui.osw_file_path, massseer_gui.sqmass_file_path_input)

    # Remove welcome message container if dataset is loaded
    massseer_gui.welcome_container.empty()
    # del welcome_container

if massseer_gui.sqmass_file_path_input!="*.sqMass":
    sqmass_file_path_list, threads = get_sqmass_files(massseer_gui.sqmass_file_path_input)

if massseer_gui.osw_file_path!="*.osw":

    selected_peptide, selected_precursor_charge, peptide_transition_list  = process_osw_file(massseer_gui.osw_file_path)
    
    if massseer_gui.sqmass_file_path_input!="*.sqMass":

        # UI plotting settings
        # plot_settings = ChromatogramPlotSettings()
        # plot_settings.create_sidebar()
        massseer_gui.show_chromatogram_plot_settings()
        # UI Algo settings
        # algo_settings = AlgorithmUISettings()
        # algo_settings.create_ui(plot_settings)
        massseer_gui.show_algorithm_settings()
    
        ### Processing / Plotting

        ## Get Precursor trace
        if massseer_gui.chromatogram_plot_settings.include_ms1:
            precursor_id = peptide_transition_list.PRECURSOR_ID[0]
        else:
            precursor_id = []

        ## Get Transition XIC data
        if massseer_gui.chromatogram_plot_settings.include_ms2:
            # TODO: For regular proteomics DETECTING is always 1, but for IPF there are theoretical transitions that are appened that are set to 0. Need to add an option later on to make a selection if user also wants identifying transitions
            transition_id_list = peptide_transition_list.TRANSITION_ID[peptide_transition_list.PRODUCT_DETECTING==1].tolist()
            trace_annotation = peptide_transition_list.PRODUCT_ANNOTATION[peptide_transition_list.PRODUCT_DETECTING==1].tolist()
        else:
            transition_id_list = []
            trace_annotation = []

        # Get chromatogram data for all sqMass files
        chrom_data = process_many_files(sqmass_file_path_list, include_ms1=massseer_gui.chromatogram_plot_settings.include_ms1, include_ms2=massseer_gui.chromatogram_plot_settings.include_ms2, precursor_id=precursor_id, transition_id_list=transition_id_list, trace_annotation=trace_annotation, thread_count=threads)

        # Get min RT start point and max RT end point
        x_range, y_range = get_chrom_data_limits(chrom_data, 'dict', massseer_gui.chromatogram_plot_settings.set_x_range, massseer_gui.chromatogram_plot_settings.set_y_range)

        if massseer_gui.alogrithm_settings.do_consensus_chrom == 'global':
            chrom_data_global = get_chrom_data_global(chrom_data, massseer_gui.chromatogram_plot_settings.include_ms1, massseer_gui.chromatogram_plot_settings.include_ms2)
        else:
            chrom_data_global = []

        chrom_plot_objs = draw_many_chrom_data(sqmass_file_path_list, massseer_gui, chrom_data, massseer_gui.chromatogram_plot_settings.include_ms1, massseer_gui.chromatogram_plot_settings.include_ms2, peptide_transition_list, selected_peptide, selected_precursor_charge, massseer_gui.chromatogram_plot_settings.smoothing_dict, x_range, y_range, massseer_gui.chromatogram_plot_settings.scale_intensity, massseer_gui.alogrithm_settings, threads )

        if massseer_gui.alogrithm_settings.do_consensus_chrom != 'none':

            consensus_chrom_plot_objs = draw_many_consensus_chrom(sqmass_file_path_list, selected_peptide, selected_precursor_charge, massseer_gui.alogrithm_settings.do_consensus_chrom, massseer_gui.alogrithm_settings.consensus_chrom_mode, chrom_plot_objs, chrom_data_global, massseer_gui.alogrithm_settings.scale_intensity, massseer_gui.alogrithm_settings.percentile_start, massseer_gui.alogrithm_settings.percentile_end, massseer_gui.alogrithm_settings.threshold, massseer_gui.alogrithm_settings.auto_threshold, massseer_gui.chromatogram_plot_settings.smoothing_dict, x_range, y_range, massseer_gui.alogrithm_settings, threads)

        plot_cols = st.columns(massseer_gui.chromatogram_plot_settings.num_plot_columns)
        col_counter = 0 
        for sqmass_file_path in sqmass_file_path_list:
                plot_obj = chrom_plot_objs[sqmass_file_path].plot_obj
                
                if massseer_gui.alogrithm_settings.do_consensus_chrom != 'none':
                    averaged_plot_obj = consensus_chrom_plot_objs[sqmass_file_path].plot_obj

                    # Create a Streamlit layout with two columns
                    col1, col2 = st.columns(2)
                    
                    # Display the Bokeh charts in the columns
                    with col1:
                        # Show plot in Streamlit
                        st.bokeh_chart(plot_obj)
                    with col2:
                        st.bokeh_chart(averaged_plot_obj)
                else:
                    with plot_cols[col_counter]:
                        st.bokeh_chart(plot_obj)
                        col_counter+=1
                        if col_counter >= len(plot_cols):
                            col_counter = 0

if massseer_gui.file_input_settings.osw_file_path is not None and massseer_gui.file_input_settings.sqmass_file_path_input is not None:
    show_xic_exp = ExtractedIonChromatogramAnalysisServer(massseer_gui)
    show_xic_exp.main()

# OpenMS Siderbar Bottom Logo
st.sidebar.image(OPENMS_LOGO)