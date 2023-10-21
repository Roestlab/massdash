import streamlit as st

import os
import fnmatch
import numpy as np
import pyopenms as po

# Type hinting
from typing import List

# Internal modules
from data_loader import process_many_files
from SqlDataAccess import OSWDataAccess
from plotter import Plotter
from chromatogram_data_handling import get_chrom_data_limits, get_chrom_data_global, compute_consensus_chromatogram
from peak_picking import get_peak_boundariers_for_single_chromatogram, merge_and_calculate_consensus_peak_boundaries

@st.cache_data
def get_protein_options(protein_table):
    """
    Get a list of protein options from the provided data frame.

    Parameters:
        protein_table (pandas.DataFrame): A DataFrame containing protein data.

    Returns:
        list: A list of protein options.
    """
    return list(np.unique(protein_table.PROTEIN_ACCESSION.to_list()))

@st.cache_data
def get_peptide_options(peptide_table):
    """
    Get a list of peptide options from the provided data frame.

    Parameters:
        peptide_table (pandas.DataFrame): A DataFrame containing peptide data.

    Returns:
        list: A list of peptide options.
    """
    return list(np.unique(peptide_table.MODIFIED_SEQUENCE.to_list()))

# Confit
st.set_page_config(page_title='MassSeer', page_icon=':bar_chart:', layout='wide')

MASSSEER_LOGO = 'massseer/assets/img/MassSeer_Logo_Full.png'
OPENMS_LOGO = 'massseer/assets/img/OpenMS.png'

# MassSeer Sidebar Top Logo
st.sidebar.image(MASSSEER_LOGO)

st.sidebar.divider()

# Define the main area
st.sidebar.title("Input OSW file")
# Add a text input component
osw_file_path = st.sidebar.text_input("Enter file path", "*.osw")

# Define the main area
st.sidebar.title("Input sqMass file")
# Add a text input component
sqmass_file_path_input = st.sidebar.text_input("Enter file path", "*.sqMass")

if sqmass_file_path_input!="*.sqMass":
    if os.path.isfile(sqmass_file_path_input):
        sqmass_file_path_list = [sqmass_file_path_input]
    else:
        with st.sidebar.expander("Advanced Settings"):
            # 1. Get the list of files in the directory
            files_in_directory = os.listdir(sqmass_file_path_input)
            
            #2. Filter the files based on the *.sqMass file extension (case-insensitive)
            files_in_directory = [filename for filename in files_in_directory if fnmatch.fnmatch(filename.lower(), '*.sqmass')]

            # 3. Sort the filenames alphabetically
            sorted_filenames = sorted(files_in_directory, reverse=True)

            # Create a selection box in the sidebar
            selected_sorted_filenames = st.multiselect("sqMass files", sorted_filenames, sorted_filenames)    

            # Create a list of full file paths
            sqmass_file_path_list = [os.path.join(sqmass_file_path_input, file) for file in selected_sorted_filenames]

            if len(sqmass_file_path_list) > 1:
                    # Add Threads slider
                    st.title("Threads")
                    threads = st.slider("Number of threads", 1, os.cpu_count(), os.cpu_count())
            else:
                threads = 1

if osw_file_path!="*.osw":

    st.sidebar.title("Protein Selection")

    # Button to include decoys, default is False
    include_decoys = st.sidebar.checkbox("Include decoys", value=False)

    osw = OSWDataAccess(osw_file_path)

    protein_table = osw.getProteinTable(include_decoys)

    # Add a button to the sidebar for random protein selection
    pick_random_protein = st.sidebar.button('Random Protein Selection')
    if pick_random_protein:
        unique_protein_list = get_protein_options(protein_table)
        selected_protein = np.random.choice(unique_protein_list)
        selected_protein_index = int(np.where( [True if selected_protein==protein else False for protein in unique_protein_list] )[0][0])
        # print(f"Selected protein: {selected_protein} with index {selected_protein_index}")
        selected_protein_ = st.sidebar.selectbox("Select protein", get_protein_options(protein_table), index=selected_protein_index)
    else:
        # Add a searchable dropdown list to the sidebar
        selected_protein = st.sidebar.selectbox("Select protein", get_protein_options(protein_table))

    print(f"Selected protein: {selected_protein}")

    st.sidebar.title("Peptide Selection")

    # Get selected protein id from protein table based on selected protein
    selected_protein_id = protein_table[protein_table.PROTEIN_ACCESSION==selected_protein].PROTEIN_ID.to_list()[0]

    peptide_table = osw.getPeptideTableFromProteinID(selected_protein_id)

    # Add a button to the sidebar for random peptide selection
    pick_random_peptide = st.sidebar.button('Random Peptide Selection')
    if pick_random_peptide:
        unique_peptide_list = get_peptide_options(peptide_table)
        selected_peptide = np.random.choice(unique_peptide_list)
        selected_peptide_index = int(np.where( [True if selected_peptide==peptide else False for peptide in unique_peptide_list] )[0][0])
        # print(f"Selected peptide: {selected_peptide} with index {selected_peptide_index}")
        selected_peptide_ = st.sidebar.selectbox("Select peptide", get_peptide_options(peptide_table), index=selected_peptide_index)

        selected_precursor_charge = np.random.choice(osw.getPrecursorCharges(selected_peptide).CHARGE.to_list())
        selected_precursor_charge = st.sidebar.selectbox("Select charge", osw.getPrecursorCharges(selected_peptide).CHARGE.to_list())
    else:
        # Add a searchable dropdown list to the sidebar
        selected_peptide = st.sidebar.selectbox("Select peptide", get_peptide_options(peptide_table))

        selected_precursor_charge = st.sidebar.selectbox("Select charge", osw.getPrecursorCharges(selected_peptide).CHARGE.to_list())

    print(f"Selected peptide: {selected_peptide} with charge {selected_precursor_charge}")

    peptide_transition_list = osw.getPeptideTransitionInfo(selected_peptide, selected_precursor_charge)

    
    if sqmass_file_path_input!="*.sqMass":

        ### UI Components

        st.sidebar.title("Plotting Settings")
        # Add checkboxes in the sidebar to include MS1 and/or MS2 traces
        include_ms1 = st.sidebar.checkbox("Include MS1 Traces", value=True)
        include_ms2 = st.sidebar.checkbox("Include MS2 Traces", value=True)

        with st.sidebar.expander("Advanced Settings"):

            # Add Checkboxes for setting x-range and y-range
            set_x_range = st.checkbox("Set x-range", value=False)
            set_y_range = st.checkbox("Set y-range", value=False)

            # Perform Smoothing of the chromatograms
            do_smoothing = st.selectbox("Smoothing", ['sgolay', 'none'])
            smoothing_dict = {}
            smoothing_dict['type'] = do_smoothing
            if do_smoothing == 'sgolay':
                # Create two columns for side-by-side widgets
                col1, col2 = st.columns(2)

                # Add widget for sgolay_polynomial_order in the first column
                sgolay_polynomial_order = col1.number_input("Polynomial Order", min_value=1, max_value=10, value=3, step=1)

                # Add widget for sgolay_frame_length in the second column
                sgolay_frame_length = col2.number_input("Frame Length", min_value=1, max_value=50, value=11, step=1)

                smoothing_dict['sgolay_polynomial_order'] = sgolay_polynomial_order
                smoothing_dict['sgolay_frame_length'] = sgolay_frame_length

        # Perform Peak Picking
        do_peak_picking = st.sidebar.selectbox("Peak Picking", ['none', 'PeakPickerMRM'])

        ## Make a consensus chromatogram
        do_consensus_chrom = st.sidebar.selectbox("Generate Consensus Chromatogram", ['none', 'run-specific', 'global'])
        scale_intensity = st.sidebar.checkbox("Scale Intensity", value=False)

        if do_consensus_chrom != 'none':
            consensus_chrom_mode = st.sidebar.selectbox("Select aggregation method", ['averaged', 'median', 'percentile_average'])

            ## Average the chromatograms
            if consensus_chrom_mode == 'percentile_average':
                auto_threshold = st.sidebar.checkbox("Auto-Compute Percentile Threshold", value=True)
                
                if not auto_threshold:
                    percentile_start=st.sidebar.number_input('Percentile start', value=25.00, min_value=0.00, max_value=100.00, step=0.01)
                    percentile_end=st.sidebar.number_input('Percentile end', value=90.00, min_value=0.00, max_value=100.00, step=0.01) 
                    threshold=st.sidebar.number_input('Threshold', value=0.00, min_value=0.00, max_value=1000000.00, step=0.01)
                else: 
                    percentile_start=st.sidebar.number_input('Percentile start', value=99.9, min_value=0.00, max_value=100.00, step=0.01)
                    percentile_end = 100
            else:
                percentile_end = None
                percentile_start = None
                auto_threshold = None
                

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
                    # Create a PeakPickerMRM object and use it to pick the peaks in the chromatogram
                    rt_peak_picker = po.PeakPickerMRM()
                    peak_picker_params = rt_peak_picker.getParameters()
                    peak_picker_params.setValue(b'gauss_width', 30.0)
                    peak_picker_params.setValue(b'use_gauss', 'false')
                    peak_picker_params.setValue(b'sgolay_frame_length', sgolay_frame_length if do_smoothing == 'sgolay' else 11)
                    peak_picker_params.setValue(b'sgolay_polynomial_order', sgolay_polynomial_order if do_smoothing == 'sgolay' else 3)
                    peak_picker_params.setValue(b'remove_overlapping_peaks', 'true')
                    rt_peak_picker.setParameters(peak_picker_params)
                    peak_features = merge_and_calculate_consensus_peak_boundaries(chrom_data_all, rt_peak_picker)
                    
                    y_bottom = [0] * len(peak_features['leftWidth'])
                    plot_obj.vbar(x=peak_features['leftWidth'], bottom=y_bottom, top=peak_features['IntegratedIntensity'], width=0.1, color="red", line_color="black")
                    plot_obj.vbar(x=peak_features['rightWidth'], bottom=y_bottom, top=peak_features['IntegratedIntensity'], width=0.1, color="red", line_color="black")

                if do_consensus_chrom != 'none':

                    ## Generate consensus chromatogram
                    if do_consensus_chrom == 'run-specific':
                        averaged_chrom_data = compute_consensus_chromatogram(consensus_chrom_mode, chrom_data_all, scale_intensity, percentile_start, percentile_end, auto_threshold)
                        plot_title = os.path.basename(sqmass_file_path)
                    elif do_consensus_chrom == 'global':
                        averaged_chrom_data = compute_consensus_chromatogram(consensus_chrom_mode, chrom_data_global, scale_intensity, percentile_start, percentile_end, auto_threshold)
                        plot_title = 'Global Across-Run Consensus Chromatogram'

                    averaged_plotter = Plotter(averaged_chrom_data, peptide_transition_list=None, trace_annotation=[consensus_chrom_mode], title=plot_title, subtitle=f"{selected_peptide}_{selected_precursor_charge}", smoothing_dict=smoothing_dict,  plot_type='bokeh', x_range=x_range, y_range=y_range)
                    averaged_plot_obj  = averaged_plotter.plot()

                    if do_peak_picking == 'PeakPickerMRM':
                        # Create a PeakPickerMRM object and use it to pick the peaks in the chromatogram
                        rt_peak_picker = po.PeakPickerMRM()
                        peak_picker_params = rt_peak_picker.getParameters()
                        peak_picker_params.setValue(b'gauss_width', 30.0)
                        peak_picker_params.setValue(b'use_gauss', 'false')
                        peak_picker_params.setValue(b'sgolay_frame_length', sgolay_frame_length if do_smoothing == 'sgolay' else 11)
                        peak_picker_params.setValue(b'sgolay_polynomial_order', sgolay_polynomial_order if do_smoothing == 'sgolay' else 3)
                        peak_picker_params.setValue(b'remove_overlapping_peaks', 'true')
                        rt_peak_picker.setParameters(peak_picker_params)
                        peak_features = get_peak_boundariers_for_single_chromatogram(averaged_chrom_data[0], rt_peak_picker)
                            
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