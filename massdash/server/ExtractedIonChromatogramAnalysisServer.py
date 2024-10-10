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
from ..ui.MassDashGUI import MassDashGUI
from ..ui.ExtractedIonChromatogramAnalysisUI import ExtractedIonChromatogramAnalysisUI
from ..ui.ChromatogramPlotUISettings import ChromatogramPlotUISettings
from ..ui.PeakPickingUISettings import PeakPickingUISettings
from ..ui.ConcensusChromatogramUISettings import ConcensusChromatogramUISettings
# Loaders
from ..loaders.access.OSWDataAccess import OSWDataAccess
from ..loaders.SpectralLibraryLoader import SpectralLibraryLoader
from ..loaders.SqMassLoader import SqMassLoader
# Peak Picking
from ..peakPickers.pyMRMTransitionGroupPicker import pyMRMTransitionGroupPicker
from ..peakPickers.MRMTransitionGroupPicker import MRMTransitionGroupPicker
from ..peakPickers.ConformerPeakPicker import ConformerPeakPicker
# Plotting
from ..plotting.GenericPlotter import PlotConfig
from ..plotting.InteractivePlotter import InteractivePlotter
# Util
from ..util import LOGGER, time_block, infer_unique_filenames
from .util import get_string_mslevels_from_bool

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

        peak_picking_settings = PeakPickingUISettings(self.massdash_gui.isStreamlitCloud)
        peak_picking_settings.create_ui(chrom_plot_settings)

        concensus_chromatogram_settings = ConcensusChromatogramUISettings()
        # TODO: Uncomment out once concensus chromatogram is implemented
        # concensus_chromatogram_settings.create_ui()

        # Load XIC data from SQMass file
        self.xic_data = SqMassLoader(dataFiles=self.massdash_gui.file_input_settings.sqmass_file_path_list, rsltsFile=self.massdash_gui.file_input_settings.osw_file_path)

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
            if peak_picking_settings.do_peak_picking == 'Feature File Boundaries':
                with time_block() as elapsed_time:
                    tr_group_feature_data = self.xic_data.loadTransitionGroupFeatures(transition_list_ui.transition_settings.selected_peptide, transition_list_ui.transition_settings.selected_charge)
                st.write(f"Loading Feature File Peak Boundaries... Elapsed time: {elapsed_time()}")
            elif peak_picking_settings.do_peak_picking == 'pyPeakPickerChromatogram':
                with time_block() as elapsed_time:
                    # Peak picking using pyMRMTransitionGroupPicker
                    if peak_picking_settings.peak_pick_on_displayed_chrom:
                        mslevel = get_string_mslevels_from_bool({'ms1':chrom_plot_settings.include_ms1, 'ms2':chrom_plot_settings.include_ms2})
                    else:
                        mslevel = peak_picking_settings.peak_picker_algo_settings.mslevels
                    peak_picker_param = peak_picking_settings.peak_picker_algo_settings.PeakPickerChromatogramParams

                    tr_group_feature_data = {}
                    for file, tr_group in tr_group_data.items():
                        peak_picker = pyMRMTransitionGroupPicker(mslevel, peak_picker=peak_picker_param.peak_picker)
                        peak_features = peak_picker.pick(tr_group)
                        tr_group_feature_data[file] = peak_features
                st.write(f"Performing pyPeakPickerChromatogram Peak Picking... Elapsed time: {elapsed_time()}")
            elif peak_picking_settings.do_peak_picking == 'MRMTransitionGroupPicker':
                with time_block() as elapsed_time:
                    # Peak picking using MRMTransitionGroupPicker
                    tr_group_feature_data = {}
                    for file, tr_group in tr_group_data.items():
                        peak_picker = MRMTransitionGroupPicker(peak_picking_settings.peak_picker_algo_settings.smoother)
                        peak_features = peak_picker.pick(tr_group)
                        tr_group_feature_data[file] = peak_features
                st.write(f"Performing MRMTransitionGroupPicker Peak Picking... Elapsed time: {elapsed_time()}")
            elif peak_picking_settings.do_peak_picking == 'Conformer':
                with time_block() as elapsed_time:
                    # Peak picking using Conformer
                    tr_group_feature_data = {}
                    for file, tr_group in tr_group_data.items():
                        tr_group.targeted_transition_list = transition_list_ui.target_transition_list
                        print(f"Pretrained model file: {peak_picking_settings.peak_picker_algo_settings.pretrained_model_file}")
                        
                        peak_picker = ConformerPeakPicker(SpectralLibraryLoader(self.massdash_gui.file_input_settings.osw_file_path),
                                                          peak_picking_settings.peak_picker_algo_settings.pretrained_model_file, 
                                                          prediction_threshold=peak_picking_settings.peak_picker_algo_settings.conformer_prediction_threshold, 
                                                          prediction_type=peak_picking_settings.peak_picker_algo_settings.conformer_prediction_type)
                        # get the trantition in tr_group with the max intensity
                        max_int_transition = np.max([transition.intensity for transition in tr_group.transitionData])
                        peak_features = peak_picker.pick(tr_group, max_int_transition)
                        tr_group_feature_data[file] = peak_features
                st.write(f"Performing Conformer Peak Picking... Elapsed time: {elapsed_time()}")
            else:
                tr_group_feature_data = {file: None for file in tr_group_data.keys()}

            with time_block() as elapsed_time:
                
                # Initialize plot object dictionary
                plot_obj_dict = {}

                # Iterate through each file and generate chromatogram plots

                noFeaturesWarning = [] # list to store files with no features found so can output warning
                for file in tr_group_data.keys():
                    tr_group_data[file].targeted_transition_list = transition_list_ui.target_transition_list

                    # Extract chromatogram data from the transitionGroup
                    precursorChroms, transitionChroms = tr_group_data[file].toPandasDf(separate=True)
                    if chrom_plot_settings.include_ms1 and chrom_plot_settings.include_ms2:
                        to_plot = pd.concat([precursorChroms, transitionChroms])
                    elif chrom_plot_settings.include_ms1:
                        to_plot = precursorChroms
                    elif chrom_plot_settings.include_ms2:
                        to_plot = transitionChroms
                    else:
                        to_plot = pd.DataFrame()

                    # Load transition group features for this file
                    if file in tr_group_feature_data.keys():
                        transitionGroupFeatures = tr_group_feature_data[file]
                        transitionGroupFeatures.rename(columns={'leftBoundary':'leftWidth', 'rightBoundary':'rightWidth', 'consensusApexIntensity':'apexIntensity'}, inplace=True)
                    else:
                        transitionGroupFeatures = None
                        noFeaturesWarning.append(file)

                    if not to_plot.empty:
                        plot_obj_dict[file] = to_plot.plot(x='rt', y='intensity', kind='chromatogram', by='annotation', backend='ms_plotly', annotation_data=transitionGroupFeatures, width=2000, scale_intensity=chrom_plot_settings.scale_intensity, show_plot=False) 

            st.write(f"Generating chromatogram plots... Elapsed time: {elapsed_time()}")

        with time_block() as elapsed_time:
            # Show extracted ion chromatograms
            for i in noFeaturesWarning:
                st.warning(f"No features found for file {i}.")
            transition_list_ui.show_extracted_ion_chromatograms(plot_container, chrom_plot_settings, concensus_chromatogram_settings, plot_obj_dict)
        status.write(f"Drawing extracted ion chromatograms... Elapsed time: {elapsed_time()}")

        # Update status indicator
        overall_elapsed_time = timeit.default_timer() - overall_start_time
        status.update(label=f"{transition_list_ui.transition_settings.selected_peptide}_{transition_list_ui.transition_settings.selected_charge} XIC extration complete! Total elapsed time: {timedelta(seconds=overall_elapsed_time)}", state="complete", expanded=False)
        

