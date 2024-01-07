"""
massdash/server/ExtractedIonChromatogramAnalysisServer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import os
import streamlit as st

# Timing modules
import timeit
from datetime import timedelta

# Data modules
import numpy as np
import pandas as pd

# UI
from ui.MassDashGUI import MassDashGUI
from ui.ExtractedIonChromatogramAnalysisUI import ExtractedIonChromatogramAnalysisUI
from ui.ChromatogramPlotUISettings import ChromatogramPlotUISettings
from ui.PeakPickingUISettings import PeakPickingUISettings
from ui.ConcensusChromatogramUISettings import ConcensusChromatogramUISettings
# Loaders
from loaders.access.OSWDataAccess import OSWDataAccess
from loaders.SpectralLibraryLoader import SpectralLibraryLoader
from loaders.SqMassLoader import SqMassLoader
# Peak Picking
from peakPickers.pyMRMTransitionGroupPicker import pyMRMTransitionGroupPicker
from peakPickers.MRMTransitionGroupPicker import MRMTransitionGroupPicker
from peakPickers.ConformerPeakPicker import ConformerPeakPicker
# Plotting
from plotting.GenericPlotter import PlotConfig
from plotting.InteractivePlotter import InteractivePlotter
# Util
from util import LOGGER, time_block
from server.util import get_string_mslevels_from_bool

class ExtractedIonChromatogramAnalysisServer:
    """
    A class representing a server for extracted ion chromatogram analysis.

    Attributes:
        massdash_gui (MassDashGUI): An object representing the MassDash GUI.
        transition_list (SpectralLibraryLoader): An object representing the transition list.
        osw_data (OSWDataAccess): An object representing the OSW data.
        xic_data (SqMassLoader): An object representing the XIC data.
        
    Methods:
        get_transition_list: Loads the spectral library and sets the transition list attribute.
        append_qvalues_to_transition_list: Appends q-values to the transition list.
        main: Runs the main post extracted ion chromatogram analysis workflow.
    """
    def __init__(self, massdash_gui: MassDashGUI):
        """
        Initializes the ExtractedIonChromatogramAnalysisServer object.

        Args:
            massdash_gui (MassDashGUI): An object representing the MassDash GUI.
        """
        self.massdash_gui = massdash_gui
        self.transition_list = None
        self.osw_data = None
        self.xic_data = None
        
        LOGGER.name = "ExtractedIonChromatogramAnalysisServer"
        if massdash_gui.verbose:
            LOGGER.setLevel("DEBUG")
        else:
            LOGGER.setLevel("INFO")

    def get_transition_list(self):
        """
        Loads the spectral library and sets the transition list attribute.
        """
        self.transition_list = SpectralLibraryLoader(self.massdash_gui.file_input_settings.osw_file_path)
        self.transition_list.load()

    def append_qvalues_to_transition_list(self):
        """
        Appends q-values to the transition list.
        """
        top_ranked_precursor_features = self.osw_data.get_top_rank_precursor_features_across_runs()
        # merge transition list with top ranked precursor features
        self.transition_list.data = pd.merge(self.transition_list.data, top_ranked_precursor_features, on=['ProteinId', 'PeptideSequence', 'ModifiedPeptideSequence', 'PrecursorMz', 'PrecursorCharge', 'Decoy'], how='left')

    def main(self):
        """
        Runs the main post extracted ion chromatogram analysis workflow.
        """
        # Load data from the OSW file
        self.osw_data = OSWDataAccess(self.massdash_gui.file_input_settings.osw_file_path)

        # Get and append q-values to the transition list
        self.get_transition_list()
        self.append_qvalues_to_transition_list()

        # Create a UI for the transition list and show transition information
        transition_list_ui = ExtractedIonChromatogramAnalysisUI(self.transition_list)
        transition_list_ui.show_transition_information()

        # Create UI settings for chromatogram plotting, peak picking, and consensus chromatogram
        chrom_plot_settings = ChromatogramPlotUISettings()
        chrom_plot_settings.create_ui()

        peak_picking_settings = PeakPickingUISettings()
        peak_picking_settings.create_ui(chrom_plot_settings)

        concensus_chromatogram_settings = ConcensusChromatogramUISettings()
        concensus_chromatogram_settings.create_ui()

        # Load XIC data from SQMass file
        self.xic_data = SqMassLoader(self.massdash_gui.file_input_settings.sqmass_file_path_list, self.massdash_gui.file_input_settings.osw_file_path)

        # Print selected peptide and charge information
        LOGGER.info(f"Selected peptide: {transition_list_ui.transition_settings.selected_peptide} Selected charge: {transition_list_ui.transition_settings.selected_charge}")

        # Create a container for the plots
        plot_container = st.container()

        # Add a status indicator and start the overall timer
        overall_start_time = timeit.default_timer()
        with st.status("Performing targeted extraction...", expanded=True) as status:
            with time_block() as elapsed_time:
                # Load transition group data
                tr_group_data = self.xic_data.loadTransitionGroups(transition_list_ui.transition_settings.selected_peptide, transition_list_ui.transition_settings.selected_charge)
            st.write(f"Loading XIC data... Elapsed time: {elapsed_time()}") 
            
            # Perform peak picking based on user settings
            if peak_picking_settings.do_peak_picking == 'OSW-PyProphet':
                with time_block() as elapsed_time:
                    tr_group_feature_data = self.xic_data.loadTransitionGroupFeatures(transition_list_ui.transition_settings.selected_peptide, transition_list_ui.transition_settings.selected_charge)
                st.write(f"Loading OSW-PyProphet Peak Boundaries... Elapsed time: {elapsed_time()}")
            elif peak_picking_settings.do_peak_picking == 'pyPeakPickerMRM':
                with time_block() as elapsed_time:
                    # Peak picking using pyMRMTransitionGroupPicker
                    if peak_picking_settings.peak_pick_on_displayed_chrom:
                        mslevel = get_string_mslevels_from_bool({'ms1':chrom_plot_settings.include_ms1, 'ms2':chrom_plot_settings.include_ms2})
                    else:
                        mslevel = peak_picking_settings.peak_picker_algo_settings.mslevels
                    peak_picker_param = peak_picking_settings.peak_picker_algo_settings.PeakPickerMRMParams

                    tr_group_feature_data = {}
                    for file, tr_group in tr_group_data.items():
                        peak_picker = pyMRMTransitionGroupPicker(mslevel, peak_picker=peak_picker_param.peak_picker)
                        peak_features = peak_picker.pick(tr_group)
                        tr_group_feature_data[file.filename] = peak_features
                st.write(f"Performing pyPeakPickerMRM Peak Picking... Elapsed time: {elapsed_time()}")
            elif peak_picking_settings.do_peak_picking == 'MRMTransitionGroupPicker':
                with time_block() as elapsed_time:
                    # Peak picking using MRMTransitionGroupPicker
                    tr_group_feature_data = {}
                    for file, tr_group in tr_group_data.items():
                        peak_picker = MRMTransitionGroupPicker(peak_picking_settings.peak_picker_algo_settings.smoother)
                        peak_features = peak_picker.pick(tr_group)
                        tr_group_feature_data[file.filename] = peak_features
                st.write(f"Performing MRMTransitionGroupPicker Peak Picking... Elapsed time: {elapsed_time()}")
            elif peak_picking_settings.do_peak_picking == 'Conformer':
                with time_block() as elapsed_time:
                    # Peak picking using Conformer
                    tr_group_feature_data = {}
                    for file, tr_group in tr_group_data.items():
                        tr_group.targeted_transition_list = transition_list_ui.target_transition_list
                        print(f"Pretrained model file: {peak_picking_settings.peak_picker_algo_settings.pretrained_model_file}")
                        
                        peak_picker = ConformerPeakPicker(tr_group, peak_picking_settings.peak_picker_algo_settings.pretrained_model_file, window_size=peak_picking_settings.peak_picker_algo_settings.conformer_window_size, prediction_threshold=peak_picking_settings.peak_picker_algo_settings.conformer_prediction_threshold, prediction_type=peak_picking_settings.peak_picker_algo_settings.conformer_prediction_type)
                        # get the trantition in tr_group with the max intensity
                        max_int_transition = np.max([transition.intensity for transition in tr_group.transitionData])
                        peak_features = peak_picker.pick(max_int_transition)
                        tr_group_feature_data[file.filename] = peak_features
                st.write(f"Performing Conformer Peak Picking... Elapsed time: {elapsed_time()}")
            else:
                tr_group_feature_data = {file.filename: None for file in tr_group_data.keys()}

            with time_block() as elapsed_time:
                
                # Initialize axis limits for plotting
                axis_limits_dict = {'x_range' : [], 'y_range' : []}
                master_rt_arr = np.concatenate([tg.flatten().data for tg in tr_group_data.values()])
                master_int_arr = np.concatenate([tg.flatten().intensity for tg in tr_group_data.values()])

                # Set axis limits based on user settings
                if chrom_plot_settings.set_x_range:
                    axis_limits_dict['x_range'] = [master_rt_arr.min(), master_rt_arr.max()]
                if chrom_plot_settings.set_y_range:
                    axis_limits_dict['y_range'] = [0, master_int_arr.max()]

                # Initialize plot object dictionary
                plot_obj_dict = {}

                # Iterate through each file and generate chromatogram plots
                for file, tr_group in tr_group_data.items():
                    tr_group.targeted_transition_list = transition_list_ui.target_transition_list

                    # Configure plot settings
                    plot_settings_dict = chrom_plot_settings.get_settings()
                    plot_settings_dict['x_axis_label'] = 'Retention Time (s)'
                    plot_settings_dict['y_axis_label'] = 'Intensity'
                    plot_settings_dict['title'] = os.path.basename(file.filename)
                    plot_settings_dict['subtitle'] = f"{transition_list_ui.transition_settings.selected_protein} | {transition_list_ui.transition_settings.selected_peptide}_{transition_list_ui.transition_settings.selected_charge}"

                    # Update plot configuration
                    plot_config = PlotConfig()
                    plot_config.update(plot_settings_dict)

                    # chromatogram plot generation
                    if not tr_group.empty():
                        plotter = InteractivePlotter(plot_config)
                        # Check if there is available feature data
                        if file.filename in tr_group_feature_data.keys():
                            feature_data =  tr_group_feature_data[file.filename]
                        else:
                            feature_data = None
                        plot_obj = plotter.plot(tr_group, feature_data)
                        plot_obj_dict[file.filename] = plot_obj

            st.write(f"Generating chromatogram plots... Elapsed time: {elapsed_time()}")

        with time_block() as elapsed_time:
            # Show extracted ion chromatograms
            transition_list_ui.show_extracted_ion_chromatograms(plot_container, chrom_plot_settings, concensus_chromatogram_settings, plot_obj_dict)
        status.write(f"Drawing extracted ion chromatograms... Elapsed time: {elapsed_time()}")

        # Update status indicator
        overall_elapsed_time = timeit.default_timer() - overall_start_time
        status.update(label=f"{transition_list_ui.transition_settings.selected_peptide}_{transition_list_ui.transition_settings.selected_charge} XIC extration complete! Total elapsed time: {timedelta(seconds=overall_elapsed_time)}", state="complete", expanded=False)
        

