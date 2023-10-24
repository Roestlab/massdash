import streamlit as st

import os
from PIL import Image

# Type hinting
from typing import List

# Internal UI modules
from massseer.util_ui import show_welcome_message
from massseer.file_handling_ui import process_osw_file, get_sqmass_files
from massseer.plotting_ui import chromatogram_plotting_settings
from massseer.algo_ui import algo_ui_widgets

# Internal server modules
from massseer.data_loader import process_many_files
from massseer.plotter import Plotter
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

welcome_container, load_toy_dataset, osw_file_path, sqmass_file_path_input = show_welcome_message()

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

    # Remove welcome message container if dataset is loaded
    welcome_container.empty()
    del welcome_container

if osw_file_path!="*.osw" and sqmass_file_path_input!="*.sqMass" and not st.session_state.clicked['load_toy_dataset']:
    # Remove welcome message container if dataset is loaded
    welcome_container.empty()
    del welcome_container

if sqmass_file_path_input!="*.sqMass":
    sqmass_file_path_list, threads = get_sqmass_files(sqmass_file_path_input)

if osw_file_path!="*.osw":

    selected_peptide, selected_precursor_charge, peptide_transition_list  = process_osw_file(osw_file_path)
    
    if sqmass_file_path_input!="*.sqMass":

        # UI plotting settings
        include_ms1, include_ms2, set_x_range, set_y_range, do_smoothing, sgolay_polynomial_order, sgolay_frame_length, smoothing_dict = chromatogram_plotting_settings()

        do_peak_picking, do_consensus_chrom, scale_intensity, consensus_chrom_mode, percentile_start, percentile_end, threshold, auto_threshold = algo_ui_widgets()
                
        ### Processing / Plotting

        ## Get Precursor trace
        if include_ms1:
            precursor_id = peptide_transition_list.PRECURSOR_ID[0]
        else:
            precursor_id = []

        ## Get Transition XIC data
        if include_ms2:
            # TODO: For regular proteomics DETECTING is always 1, but for IPF there are theoretical transitions that are appened that are set to 0. Need to add an option later on to make a selection if user also wants identifying transitions
            transition_id_list = peptide_transition_list.TRANSITION_ID[peptide_transition_list.PRODUCT_DETECTING==1].tolist()
            trace_annotation = peptide_transition_list.PRODUCT_ANNOTATION[peptide_transition_list.PRODUCT_DETECTING==1].tolist()
        else:
            transition_id_list = []
            trace_annotation = []

        # Get chromatogram data for all sqMass files
        chrom_data = process_many_files(sqmass_file_path_list, include_ms1=include_ms1, include_ms2=include_ms2, precursor_id=precursor_id, transition_id_list=transition_id_list, trace_annotation=trace_annotation,  thread_count=threads)

        # Get min RT start point and max RT end point
        x_range, y_range = get_chrom_data_limits(chrom_data, 'dict', set_x_range, set_y_range)

        if do_consensus_chrom == 'global':
            chrom_data_global = get_chrom_data_global(chrom_data, include_ms1, include_ms2)

        for sqmass_file_path in sqmass_file_path_list:
            chrom_data_all, trace_annotation_all = [], []

            if include_ms1:
                chrom_data_all = chrom_data_all + chrom_data[sqmass_file_path]['ms1'][0]
                trace_annotation_all = trace_annotation_all + chrom_data[sqmass_file_path]['ms1'][1]
            
            if include_ms2:
                chrom_data_all = chrom_data_all + chrom_data[sqmass_file_path]['ms2'][0]
                trace_annotation_all = trace_annotation_all + chrom_data[sqmass_file_path]['ms2'][1]

            ## Get Bokeh plot object
            if len(chrom_data_all) != 0 and len(trace_annotation_all)!=0:
                plotter = Plotter(chrom_data_all, peptide_transition_list=peptide_transition_list[peptide_transition_list.PRODUCT_DETECTING==1], trace_annotation=trace_annotation_all, title=os.path.basename(sqmass_file_path), subtitle=f"{selected_peptide}_{selected_precursor_charge}", smoothing_dict=smoothing_dict,  plot_type='bokeh', x_range=x_range, y_range=y_range)
                
                ## Generate the plot
                plot_obj  = plotter.plot()

                if do_peak_picking == 'PeakPickerMRM':
                    peak_features = perform_chromatogram_peak_picking(chrom_data_all, do_smoothing, sgolay_frame_length, sgolay_polynomial_order, merged_peak_picking=True)
                    
                    y_bottom = [0] * len(peak_features['leftWidth'])
                    plot_obj.vbar(x=peak_features['leftWidth'], bottom=y_bottom, top=peak_features['IntegratedIntensity'], width=0.1, color="red", line_color="black")
                    plot_obj.vbar(x=peak_features['rightWidth'], bottom=y_bottom, top=peak_features['IntegratedIntensity'], width=0.1, color="red", line_color="black")

                if do_consensus_chrom != 'none':

                    ## Generate consensus chromatogram
                    if do_consensus_chrom == 'run-specific':
                        averaged_chrom_data = compute_consensus_chromatogram(consensus_chrom_mode, chrom_data_all, scale_intensity, percentile_start, percentile_end, threshold, auto_threshold)
                        plot_title = os.path.basename(sqmass_file_path)
                    elif do_consensus_chrom == 'global':
                        averaged_chrom_data = compute_consensus_chromatogram(consensus_chrom_mode, chrom_data_global, scale_intensity, percentile_start, percentile_end, threshold, auto_threshold)
                        plot_title = 'Global Across-Run Consensus Chromatogram'

                    averaged_plotter = Plotter(averaged_chrom_data, peptide_transition_list=None, trace_annotation=[consensus_chrom_mode], title=plot_title, subtitle=f"{selected_peptide}_{selected_precursor_charge}", smoothing_dict=smoothing_dict,  plot_type='bokeh', x_range=x_range, y_range=y_range)
                    averaged_plot_obj  = averaged_plotter.plot()

                    if do_peak_picking == 'PeakPickerMRM':
                        peak_features = perform_chromatogram_peak_picking(averaged_chrom_data[0], do_smoothing, sgolay_frame_length, sgolay_polynomial_order, merged_peak_picking=False)

                        if peak_features is not None:
                            y_bottom = [0] * len(peak_features['leftWidth'])
                            averaged_plot_obj.vbar(x=peak_features['leftWidth'], bottom=y_bottom, top=peak_features['IntegratedIntensity'], width=0.1, color="red", line_color="black")
                            averaged_plot_obj.vbar(x=peak_features['rightWidth'], bottom=y_bottom, top=peak_features['IntegratedIntensity'], width=0.1, color="red", line_color="black")

                    # Create a Streamlit layout with two columns
                    col1, col2 = st.columns(2)
                    
                    # Display the Bokeh charts in the columns
                    with col1:
                        # Show plot in Streamlit
                        st.bokeh_chart(plot_obj)
                    with col2:
                        st.bokeh_chart(averaged_plot_obj)
                else:
                    st.bokeh_chart(plot_obj)

# OpenMS Siderbar Bottom Logo
st.sidebar.image(OPENMS_LOGO)