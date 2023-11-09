import streamlit as st

import os
from PIL import Image

# Type hinting
from typing import List

# Internal UI modules
from massseer.util_ui import MassSeerGUI
from massseer.file_handling_ui import process_osw_file, get_sqmass_files, get_mzml_files, TransitionListUI
from massseer.plotting_ui import ChromatogramPlotSettings
from massseer.algo_ui import AlgorithmUISettings

# Internal server modules
from massseer.loaders.SpectralLibraryLoader import SpectralLibraryLoader
from massseer.targeted_experiment_ui import TargetedExperimentUI
from massseer.data_loader import process_many_files
from massseer.plotter import Plotter, draw_many_chrom_data, draw_many_consensus_chrom
from massseer.chromatogram_data_handling import get_chrom_data_limits, get_chrom_data_global, compute_consensus_chromatogram
from massseer.peak_picking import perform_chromatogram_peak_picking

from massseer.loaders.DiaNNLoader import DiaNNLoader

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
    massseer_gui.sqmass_file_path_input = os.path.join(dirname, '..', 'tests', 'test_data', 'xics')
    massseer_gui.osw_file_path = os.path.join(dirname, '..', 'tests', 'test_data', 'osw', 'test_data.osw')

    # Remove welcome message container if dataset is loaded
    massseer_gui.welcome_container.empty()
    # del welcome_container

if massseer_gui.osw_file_path!="*.osw" and massseer_gui.sqmass_file_path_input!="*.sqMass" and not st.session_state.clicked['load_toy_dataset']:
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

if massseer_gui.transition_list_file_path != "*.pqp / *.tsv":
    # Load data from a TSV file
    transition_list = SpectralLibraryLoader(massseer_gui.transition_list_file_path)
    transition_list.load()

    # Create a UI for targeted experiment
    targeted_experiment_ui = TargetedExperimentUI(transition_list)
    targeted_experiment_ui.show_transition_information()
    print(targeted_experiment_ui.target_transition_list)
    
    if massseer_gui.raw_file_path_input != "*.mzML":
        mzml_file_path_list, threads = get_mzml_files(massseer_gui.raw_file_path_input)

    if massseer_gui.diann_report_file_path_input != "*.tsv":
        diann_data = DiaNNLoader(massseer_gui.diann_report_file_path_input, massseer_gui.transition_list_file_path)

        # Load DIA-NN search results
        diann_data.load_report()
        print(diann_data.report.search_data.columns)
        
        # Get DIA-NN search results information for precursor
        targeted_experiment_ui.search_results = diann_data.load_report_for_precursor(targeted_experiment_ui.transition_settings.selected_peptide,  targeted_experiment_ui.transition_settings.selected_charge)

        targeted_experiment_ui.show_search_results_information()

        diann_qvalue_filtered_analytes = diann_data.filter_search_results_proteins_by_qvalue(targeted_experiment_ui.qvalue_threshold)
        targeted_experiment_ui.update_transition_information(diann_qvalue_filtered_analytes)

    if massseer_gui.raw_file_path_input != "*.mzML":

        # Create a UI for extraction parameters for targeted experiment
        targeted_experiment_ui.show_extraction_parameters()
        
        # if st.sidebar.button("Run Targeted Extraction"):
            # print(mzml_file_path_list) 
        import timeit
        from datetime import timedelta
        from massseer.util import time_block

        start_time = timeit.default_timer()
        with st.status("Performing targeted extraction...", expanded=True) as status:
            
            with time_block() as elapsed_time:
                targeted_exp = targeted_experiment_ui.load_targeted_experiment(mzml_file_path_list)
            print(f"HERE: {elapsed_time}")
            st.write(f"Loading raw file... Elapsed time: {elapsed_time()}") 
            with time_block() as elapsed_time:
                targeted_experiment_ui.targeted_data_access(targeted_exp)
            st.write(f"Setting up extraction parameters... Elapsed time: {elapsed_time()}")
            with time_block() as elapsed_time:
                peptide_coord = targeted_experiment_ui.get_peptide_dict()
                targeted_experiment_ui.targeted_extraction(targeted_exp, peptide_coord)
            st.write(f"Extracting data... Elapsed time: {elapsed_time()}")
            with time_block() as elapsed_time:
                targeted_data = targeted_experiment_ui.get_targeted_data(targeted_exp)
            st.write(f'Getting data as a pandas dataframe... Elapsed time: {elapsed_time()}')
            with time_block() as elapsed_time:
                massseer_gui.transition_group_dict = targeted_experiment_ui.load_transition_group(targeted_exp)
            st.write(f'Creating TransitionGroup... Elapsed time: {elapsed_time()}')
            status.update(label="Targeted extraction complete!", state="complete", expanded=False)
            # print(transition_group)
        elapsed = timeit.default_timer() - start_time

    from massseer.plotting.InteractivePlotter import InteractivePlotter
    from massseer.plotting.GenericPlotter import PlotConfig
    for transition_group  in massseer_gui.transition_group_dict.values():


        print("Plotting...")
        # Show Plotting Settings UI
        massseer_gui.show_chromatogram_plot_settings()
        plot_settings_dict = massseer_gui.chromatogram_plot_settings.get_settings()
        plot_settings_dict['x_axis_label'] = 'Retention Time (s)'
        plot_settings_dict['y_axis_label'] = 'Intensity'
        plot_settings_dict['title'] = os.path.basename(massseer_gui.raw_file_path_input)
        plot_settings_dict['subtitle'] = f"{targeted_experiment_ui.transition_settings.selected_protein} | {targeted_experiment_ui.transition_settings.selected_peptide}_{targeted_experiment_ui.transition_settings.selected_charge}"
        plot_config = PlotConfig()
        plot_config.update(plot_settings_dict)
        print(plot_config)

        plotter = InteractivePlotter(plot_config)
        plot_obj = plotter.plot(transition_group)

        st.bokeh_chart(plot_obj)
        st.write(f"Time elapsed: {timedelta(seconds=elapsed)}")

    for df in targeted_data.values():
        print(df.columns)
        st.dataframe(df, hide_index=True, column_order =('native_id', 'ms_level', 'precursor_mz', 'product_mz', 'mz', 'rt', 'im', 'int', 'rt_apex', 'rt_left_width', 'rt_right_width', 'im_apex', 'PrecursorCharge', 'ProductCharge', 'LibraryIntensity', 'NormalizedRetentionTime', 'PeptideSequence', 'ModifiedPeptideSequence', 'ProteinId', 'GeneName', 'Annotation', 'PrecursorIonMobility'))


# OpenMS Siderbar Bottom Logo
st.sidebar.image(OPENMS_LOGO)