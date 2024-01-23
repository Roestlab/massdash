"""
massdash/server/RawTargetedExtractionAnalysisServer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import pandas as pd
import streamlit as st
from typing import List, Dict

import timeit
from datetime import timedelta

# UI
from ..ui.RawTargetedExtractionAnalysisUI import RawTargetedExtractionAnalysisUI
from ..ui.ChromatogramPlotUISettings import ChromatogramPlotUISettings
from ..ui.PeakPickingUISettings import PeakPickingUISettings
from ..ui.ConcensusChromatogramUISettings import ConcensusChromatogramUISettings
from ..ui.util import st_mutable_write
# Server
from .OneDimensionPlotterServer import OneDimensionPlotterServer
from .TwoDimensionPlotterServer import TwoDimensionPlotterServer
from .ThreeDimensionPlotterServer import ThreeDimensionPlotterServer
from .util import check_ion_mobility
# Structs 
from ..structs.TargetedDIAConfig import TargetedDIAConfig
from ..structs.TransitionGroupFeature import TransitionGroupFeature
from ..structs.FeatureMap import FeatureMap
# Loaders
from ..loaders.SpectralLibraryLoader import SpectralLibraryLoader
from ..loaders.MzMLDataLoader import MzMLDataLoader
# Util
from ..util import LOGGER, conditional_decorator, check_streamlit, time_block, MeasureBlock

class RawTargetedExtractionAnalysisServer:
    
    def __init__(self, massdash_gui):
        self.massdash_gui = massdash_gui
        self.transition_list_file_path = None
        self.raw_file_path_input = None
        self.feature_file_path = None 
        self.threads = None
        self.feature_data = None
        self.transition_list = None
        self.mzml_loader = None

        LOGGER.name = "RawTargetedExtractionAnalysisServer"
        if massdash_gui.verbose:
            LOGGER.setLevel("DEBUG")
        else:
            LOGGER.setLevel("INFO")
            
    @conditional_decorator(lambda func: st.cache_resource(show_spinner=False)(func), check_streamlit())
    def get_transition_list(_self):
        """
        Loads the spectral library and sets the transition list attribute and append q-values to the transition list.
        """

        _self.transition_list = _self.mzml_loader.libraryFile
        _self.transition_list.has_im = _self.mzml_loader.libraryFile.has_im
        _self.transition_list.data = _self.mzml_loader.libraryFile.data

        # top_ranked_precursor_features = self.feature_data.get_top_rank_precursor_features_across_runs()
        top_ranked_precursor_features = _self.mzml_loader.rsltsFile.df[['ProteinId', 'PeptideSequence', 'ModifiedPeptideSequence',  'PrecursorCharge', 'Qvalue']]
        
        # If Decoy column not in transition list add it to top_ranked_precursor_features
        if 'Decoy' not in _self.transition_list.data.columns:
            top_ranked_precursor_features['Decoy'] = 0
        # i.e. Convert .(UniMod:1)SEGDSVGESVHGKPSVVYR to (UniMod:1)SEGDSVGESVHGKPSVVYR
        top_ranked_precursor_features['ModifiedPeptideSequence'] = top_ranked_precursor_features['ModifiedPeptideSequence'].str.replace('.', '')
        _self.transition_list.data['ModifiedPeptideSequence'] = _self.transition_list.data['ModifiedPeptideSequence'].str.replace('.', '')
        # merge transition list with top ranked precursor features
        _self.transition_list.data = pd.merge(_self.transition_list.data, top_ranked_precursor_features, on=['ProteinId', 'PeptideSequence', 'ModifiedPeptideSequence', 'PrecursorCharge'], how='left')
        # Qvalue column is NaN replace with 1
        _self.transition_list.data['Qvalue'] = _self.transition_list.data['Qvalue'].fillna(1)
        # Decoy column is NaN replace with 0
        _self.transition_list.data['Decoy'] = _self.transition_list.data['Decoy'].fillna(0)
        
        return _self.transition_list
    
    @conditional_decorator(lambda func: st.cache_resource(show_spinner="Loading data...")(func), check_streamlit())
    def initiate_mzML_interface(_self, mzml_files, resultsFile, dataFile, resultsFileType, verbose) -> MzMLDataLoader:
        """
        Initiate an mzMLLoader Object.

        Args:
            mzml_files (List[str]): List of paths to the mzML files.
            resultsFile (str): Path to the results file.
            dataFile (str): Path to the data file.
            resultsFileType (str): The type of the results file.
            verbose (bool): Whether or not to print verbose output.
        
        """
        _self.mzml_loader = MzMLDataLoader(resultsFile, mzml_files, dataFile, resultsFileType, verbose, 'gui')
        return _self.mzml_loader

    @conditional_decorator(lambda func: st.cache_resource(show_spinner="Loading into transition group...")(func), check_streamlit())
    def load_transition_group_feature(_self, _transition_list_ui: RawTargetedExtractionAnalysisUI) -> List[TransitionGroupFeature]:
        """
        Load the transition group from the targeted experiment.

        Args:
            _self (RawTargetedExtractionAnalysisServer): The instance of the server.
            _
            _targeted_exp (TargetedDIALoader): The targeted experiment loader.
            target_transition_list (pd.DataFrame): The target transition list.

        Returns:
            The loaded transition group feature.
        """

        return _self.mzml_loader.loadTopTransitionGroupFeatureDf(_transition_list_ui.transition_settings.selected_peptide, _transition_list_ui.transition_settings.selected_charge)

    @conditional_decorator(lambda func: st.cache_resource(show_spinner="Extracting data...")(func), check_streamlit())
    def targeted_extraction(_self, _transition_list_ui: RawTargetedExtractionAnalysisUI) -> List[FeatureMap]:
        """
        Perform targeted extraction on the given targeted experiment using the provided peptide coordinates and configuration.

        Args:
            _self (object): The instance of the class.
            _transition_list_ui (RawTargetedExtractionAnalysisUI): The UI for the transition list. Contains the selected peptide and charge and the targeted confif experiment extraction parameters.

        Returns:
            None
        """
        return _self.mzml_loader.loadFeatureMaps(_transition_list_ui.
                                                 transition_settings.selected_peptide, 
                                            _transition_list_ui.transition_settings.selected_charge,
                                            _transition_list_ui.targeted_exp_params)
        
    def main(self):
        if "extraction_param_button_clicked" not in st.session_state:
            st.session_state.extraction_param_button_clicked = False
    
        # Create a container for the plots
        plot_container = st.container()
        
        # Initiate the mzML Loader object
        with st.status("Performing Targeted Extraction....", expanded=True) as status:
            start_time = timeit.default_timer()
            st_log_writer = st_mutable_write("Initiating mzML files (this may take some time)...")
            with MeasureBlock(f"{self.__class__.__name__}::initiate_mzML_interface", self.massdash_gui.perf, self.massdash_gui.perf_output) as perf_metrics:
                # self.initiate_mzML_interface.clear()
                self.mzml_loader = self.initiate_mzML_interface(self.massdash_gui.file_input_settings.raw_file_path_list, 
                                            self.massdash_gui.file_input_settings.feature_file_path, 
                                            self.massdash_gui.file_input_settings.transition_list_file_path, 
                                            self.massdash_gui.file_input_settings.feature_file_type,
                                            self.massdash_gui.verbose)
            st_log_writer.write(f"Initiating mzML files complete! Elapsed time: {timedelta(seconds=perf_metrics.execution_time)}")
                            
            # Get and append q-values to the transition list
            self.transition_list = self.get_transition_list()
            
            # Create a UI for the transition list and show transition information
            transition_list_ui = RawTargetedExtractionAnalysisUI(self.transition_list, self.mzml_loader.has_im, self.massdash_gui.verbose)
            transition_list_ui.show_transition_information()
            
            current_selected_precursor = f"{transition_list_ui.transition_settings.selected_protein}_{transition_list_ui.transition_settings.selected_peptide}_{transition_list_ui.transition_settings.selected_charge}"
            
            clear_caches = False
            if current_selected_precursor != st.session_state.selected_precursor or st.session_state.extraction_param_button_clicked:
                st.info(f"Info: Selected precursor changed from {st.session_state.selected_precursor} to {current_selected_precursor}. Clearing caches...")
                st.info(f"Info: Extraction parameters changed ({st.session_state.extraction_param_button_clicked}). Clearing caches...")
                clear_caches = True
                st.session_state.selected_precursor = current_selected_precursor
            
            st_log_writer = st_mutable_write("Loading transition group feature...")
            with MeasureBlock(f"{self.__class__.__name__}::load_transition_group_feature", self.massdash_gui.perf, self.massdash_gui.perf_output) as perf_metrics:
                # Load feature data for selected peptide and charge
                if clear_caches:
                    self.load_transition_group_feature.clear()
                features = self.load_transition_group_feature(transition_list_ui)
            st_log_writer.write(f"Loading transition group feature complete! Elapsed time: {timedelta(seconds=perf_metrics.execution_time)}")
            
            # st.dataframe(features)
            transition_list_ui.show_search_results_information(features) 

            # Create UI for extraction parameters
            transition_list_ui.show_extraction_parameters()

            # Create UI settings for chromatogram plotting, peak picking, and consensus chromatogram
            chrom_plot_settings = ChromatogramPlotUISettings()
            chrom_plot_settings.create_ui(include_raw_data_settings=True, is_ion_mobility_data=self.mzml_loader.has_im)

            peak_picking_settings = PeakPickingUISettings()
            peak_picking_settings.create_ui(chrom_plot_settings)

            concensus_chromatogram_settings = ConcensusChromatogramUISettings()
            # TODO: Uncomment out once concensus chromatogram is implemented
            # concensus_chromatogram_settings.create_ui()
        
            st_log_writer = st_mutable_write("Extracting spectra...")
            with MeasureBlock(f"{self.__class__.__name__}::targeted_extraction", self.massdash_gui.perf, self.massdash_gui.perf_output) as perf_metrics:
                if clear_caches:
                    self.targeted_extraction.clear()
                featureMaps = self.targeted_extraction(transition_list_ui)
                st.write(list(featureMaps.values())[0].feature_df)
            st_log_writer.write(f"Extracting spectra complete! Elapsed time: {timedelta(seconds=perf_metrics.execution_time)}")

            transition_list_ui.validate_extraction(featureMaps, plot_container)

            st_log_writer = st_mutable_write("Generating plot...")
            with MeasureBlock(f"{self.__class__.__name__}::PlotGeneration", self.massdash_gui.perf, self.massdash_gui.perf_output) as perf_metrics:
                # Initialize plot object dictionary
                plot_obj_dict = {}
                if chrom_plot_settings.display_plot_dimension_type == "1D":
                    plot_obj_dict = OneDimensionPlotterServer(featureMaps, transition_list_ui, chrom_plot_settings, peak_picking_settings, self.massdash_gui.file_input_settings.transition_list_file_path, self.massdash_gui.verbose).generate_chromatogram_plots().plot_obj_dict
                elif chrom_plot_settings.display_plot_dimension_type == "2D":
                    plot_obj_dict = TwoDimensionPlotterServer(featureMaps, transition_list_ui, chrom_plot_settings).generate_two_dimensional_plots().plot_obj_dict
                elif chrom_plot_settings.display_plot_dimension_type == "3D":
                    plot_obj_dict = ThreeDimensionPlotterServer(featureMaps, transition_list_ui, chrom_plot_settings).generate_three_dimensional_plots().plot_obj_dict
            st_log_writer.write(f"Generating plot complete! Elapsed time: {timedelta(seconds=perf_metrics.execution_time)}")
            
            # Show extracted data
            st_log_writer = st_mutable_write("Rendering plot...")
            with MeasureBlock(f"{self.__class__.__name__}::DrawingPlots", self.massdash_gui.perf, self.massdash_gui.perf_output) as perf_metrics:
                if chrom_plot_settings.display_plot_dimension_type == "1D":
                    transition_list_ui.show_extracted_one_d_plots(plot_container, chrom_plot_settings, concensus_chromatogram_settings, plot_obj_dict)
                elif chrom_plot_settings.display_plot_dimension_type == "2D":
                    transition_list_ui.show_extracted_two_d_plots(plot_container, plot_obj_dict)
                elif chrom_plot_settings.display_plot_dimension_type == "3D":
                    transition_list_ui.show_extracted_three_d_plots(plot_container, plot_obj_dict, chrom_plot_settings.num_plot_columns)
            st_log_writer.write(f"Rendering plot complete! Elapsed time: {timedelta(seconds=perf_metrics.execution_time)}")
                    
            elapsed = timeit.default_timer() - start_time
            LOGGER.info("Targeted extraction complete! Elapsed time: %s", timedelta(seconds=elapsed))
            status.update(label=f"Info: Targeted extraction and plot rendering complete! Elapsed time: {timedelta(seconds=elapsed)}", state="complete", expanded=False)
        
        if chrom_plot_settings.display_extracted_data_as_df:
            transition_list_ui.show_extracted_dataframes(featureMaps)
            
        if st.session_state['perf_on']:
            st.rerun()