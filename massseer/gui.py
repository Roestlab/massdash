import os
import streamlit as st
from PIL import Image

# Type hinting
from typing import List

from bokeh.layouts import gridplot

# Internal UI modules
from massseer.ui.MassSeerGUI import MassSeerGUI
from massseer.server.ExtractedIonChromatogramAnalysisServer import ExtractedIonChromatogramAnalysisServer

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

massseer_gui = MassSeerGUI()
massseer_gui.show_welcome_message()
WELCOME_PAGE_STATE = True


###########################
## Sidebar Window

# MassSeer Sidebar Top Logo
st.sidebar.image(MASSSEER_LOGO)

st.sidebar.divider()

if massseer_gui.workflow == "xic_data" and st.session_state.clicked['load_toy_dataset']:
    if massseer_gui.workflow == "xic_data:"
        sqmass_file_path_input = os.path.join(dirname, '..', 'tests', 'test_data', 'xics')
        osw_file_path = os.path.join(dirname, '..', 'tests', 'test_data', 'osw', 'test_data.osw')

        massseer_gui.show_file_input_settings(osw_file_path, sqmass_file_path_input)
    elif massseer_gui.workflow == "raw_data":
        #TODO: Create small toy example 
        transition_list_file_path = "/media/justincsing/ExtraDrive1/Documents2/Roest_Lab/Github/MassSeer/tests/test_data/josh/diann/K562-Library-Default_osw_6Frags_diann.tsv"
        raw_file_path_input = "/media/justincsing/ExtraDrive1/Documents2/Roest_Lab/Github/MassSeer/tests/test_data/josh/90min-SP-30cm-2um-K562-100nL-25ng_DIA_Slot1-5_1_550_3-7-2021.mzML"
        diann_report_file_path_input = "/media/justincsing/ExtraDrive1/Documents2/Roest_Lab/Github/MassSeer/tests/test_data/josh/diann/jsc718.5808924.0/report.tsv"
        
        massseer_gui.show_file_input_settings(osw_file_path, sqmass_file_path_input)

    # Remove welcome message container if dataset is loaded
    massseer_gui.welcome_container.empty()

    WELCOME_PAGE_STATE = False

if massseer_gui.workflow == "xic_data" and massseer_gui.osw_file_path!="*.osw" and massseer_gui.sqmass_file_path_input!="*.sqMass" and not st.session_state.clicked['load_toy_dataset']:

    massseer_gui.show_file_input_settings(massseer_gui.osw_file_path, massseer_gui.sqmass_file_path_input)

    # Remove welcome message container if dataset is loaded
    massseer_gui.welcome_container.empty()
    
    WELCOME_PAGE_STATE = False

if massseer_gui.workflow == "xic_data" and not WELCOME_PAGE_STATE and  massseer_gui.file_input_settings.osw_file_path is not None and massseer_gui.file_input_settings.sqmass_file_path_input is not None:
    show_xic_exp = ExtractedIonChromatogramAnalysisServer(massseer_gui)
    show_xic_exp.main()

if massseer_gui.transition_list_file_path != "*.pqp / *.tsv":
    # Load data from a TSV file
    transition_list = SpectralLibraryLoader(massseer_gui.transition_list_file_path)
    transition_list.load()

    # Create a UI for targeted experiment
    targeted_experiment_ui = TargetedExperimentUI(massseer_gui, transition_list)
    
    if massseer_gui.raw_file_path_input != "*.mzML":
        mzml_file_path_list, threads = get_mzml_files(massseer_gui.raw_file_path_input)

    if massseer_gui.diann_report_file_path_input != "*.tsv":
        diann_data = DiaNNLoader(massseer_gui.diann_report_file_path_input, massseer_gui.transition_list_file_path)

        # Load DIA-NN search results
        diann_data.load_report()

        targeted_experiment_ui.show_transition_information(diann_data=diann_data)

        
        # Get DIA-NN search results information for precursor
        targeted_experiment_ui.search_results = diann_data.load_report_for_precursor(targeted_experiment_ui.transition_settings.selected_peptide,  targeted_experiment_ui.transition_settings.selected_charge)

        targeted_experiment_ui.show_search_results_information()

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
            st.write(f"Loading raw file... Elapsed time: {elapsed_time()}") 
            with time_block() as elapsed_time:
                targeted_experiment_ui.targeted_data_access(targeted_exp)
            st.write(f"Setting up extraction parameters... Elapsed time: {elapsed_time()}")
            with time_block() as elapsed_time:
                peptide_coord = targeted_experiment_ui.get_peptide_dict()
                targeted_extraction_params = targeted_experiment_ui.get_targeted_extraction_params_dict()
                print(targeted_extraction_params)
                targeted_experiment_ui.targeted_extraction(targeted_exp, peptide_coord, targeted_extraction_params)
            st.write(f"Extracting data... Elapsed time: {elapsed_time()}")
            with time_block() as elapsed_time:
                targeted_data = targeted_experiment_ui.get_targeted_data(targeted_exp)
            st.write(f'Getting data as a pandas dataframe... Elapsed time: {elapsed_time()}')
            with time_block() as elapsed_time:
                massseer_gui.transition_group_dict = targeted_experiment_ui.load_transition_group(targeted_exp)
            st.write(f'Creating TransitionGroup... Elapsed time: {elapsed_time()}')
            status.update(label="Targeted extraction complete!", state="complete", expanded=False)
        elapsed = timeit.default_timer() - start_time
    print(f"Info: Targeted extraction complete! Elapsed time: {timedelta(seconds=elapsed)}")

    from massseer.plotting.InteractivePlotter import InteractivePlotter
    from massseer.plotting.GenericPlotter import PlotConfig
    print(massseer_gui.transition_group_dict.values())
    print("Start plotting")
    for transition_group  in massseer_gui.transition_group_dict.values():


        print("Plotting...")
        # Show Plotting Settings UI
        massseer_gui.show_chromatogram_plot_settings(include_raw_data_settings=True)

        run_plots_list = []
        # Generate Spectrum Plot
        if massseer_gui.chromatogram_plot_settings.display_spectrum:
            plot_settings_dict = massseer_gui.chromatogram_plot_settings.get_settings()
            plot_settings_dict['x_axis_label'] = 'm/z'
            plot_settings_dict['y_axis_label'] = 'Intensity'
            plot_settings_dict['title'] = os.path.basename(massseer_gui.raw_file_path_input)
            plot_settings_dict['subtitle'] = f"{targeted_experiment_ui.transition_settings.selected_protein} | {targeted_experiment_ui.transition_settings.selected_peptide}_{targeted_experiment_ui.transition_settings.selected_charge}"
            plot_config = PlotConfig()
            plot_config.update(plot_settings_dict)

            if not transition_group.precursorChroms[0].empty():
                plotter = InteractivePlotter(plot_config)
                plot_spectrum_obj = plotter.plot(transition_group, plot_type='spectra')
                run_plots_list.append(plot_spectrum_obj)
            else:
                st.error("No data found for selected transition group.")

        # Generate Chromatgoram Plot
        if massseer_gui.chromatogram_plot_settings.display_chromatogram:
            plot_settings_dict = massseer_gui.chromatogram_plot_settings.get_settings()
            plot_settings_dict['x_axis_label'] = 'Retention Time (s)'
            plot_settings_dict['y_axis_label'] = 'Intensity'
            plot_settings_dict['title'] = os.path.basename(massseer_gui.raw_file_path_input)
            plot_settings_dict['subtitle'] = f"{targeted_experiment_ui.transition_settings.selected_protein} | {targeted_experiment_ui.transition_settings.selected_peptide}_{targeted_experiment_ui.transition_settings.selected_charge}"
            plot_config = PlotConfig()
            plot_config.update(plot_settings_dict)

            if not transition_group.precursorChroms[0].empty():
                plotter = InteractivePlotter(plot_config)
                plot_obj = plotter.plot(transition_group)
                run_plots_list.append(plot_obj)
            else:
                st.error("No data found for selected transition group.")

        # Generate Mobilogram Plot
        if massseer_gui.chromatogram_plot_settings.display_mobilogram:
            plot_settings_dict = massseer_gui.chromatogram_plot_settings.get_settings()
            plot_settings_dict['x_axis_label'] = 'Ion Mobility (1/K0)'
            plot_settings_dict['y_axis_label'] = 'Intensity'
            plot_settings_dict['title'] = os.path.basename(massseer_gui.raw_file_path_input)
            plot_settings_dict['subtitle'] = f"{targeted_experiment_ui.transition_settings.selected_protein} | {targeted_experiment_ui.transition_settings.selected_peptide}_{targeted_experiment_ui.transition_settings.selected_charge}"
            plot_config = PlotConfig()
            plot_config.update(plot_settings_dict)

            if not transition_group.precursorChroms[0].empty():
                plotter = InteractivePlotter(plot_config)
                plot_mobilo_obj = plotter.plot(transition_group, plot_type='mobilogram')
                run_plots_list.append(plot_mobilo_obj)
            else:
                st.error("No data found for selected transition group.")


        super_plot_title = run_plots_list[0].title
       

        st.subheader(super_plot_title.text)
        cols = st.columns(len(run_plots_list))
        for i, col in enumerate(cols):
            with col:
                run_plots_list[i].title = None
                st.bokeh_chart(run_plots_list[i])
        
        st.write(f"Total elapsed time of extraction: {timedelta(seconds=elapsed)}")
    

 

    for df in targeted_data.values():
        if not df.empty:            

            plotter = InteractiveTwoDimensionPlotter(df)
            two_d_plots = plotter.plot(False)
            p = gridplot(two_d_plots, ncols=3, sizing_mode='stretch_width')
            st.bokeh_chart(p)

            st.dataframe(df, hide_index=True, column_order =('native_id', 'ms_level', 'precursor_mz', 'product_mz', 'mz', 'rt', 'im', 'int', 'rt_apex', 'rt_left_width', 'rt_right_width', 'im_apex', 'PrecursorCharge', 'ProductCharge', 'LibraryIntensity', 'NormalizedRetentionTime', 'PeptideSequence', 'ModifiedPeptideSequence', 'ProteinId', 'GeneName', 'Annotation', 'PrecursorIonMobility'))




# OpenMS Siderbar Bottom Logo
st.sidebar.image(OPENMS_LOGO)