import pandas as pd
import streamlit as st
from typing import List, Dict

import timeit
from datetime import timedelta

# UI
from massseer.ui.RawTargetedExtractionAnalysisUI import RawTargetedExtractionAnalysisUI
from massseer.ui.ChromatogramPlotUISettings import ChromatogramPlotUISettings
from massseer.ui.PeakPickingUISettings import PeakPickingUISettings
from massseer.ui.ConcensusChromatogramUISettings import ConcensusChromatogramUISettings
# Server
from massseer.server.PeakPickingServer import PeakPickingServer
from massseer.server.OneDimensionPlotterServer import OneDimensionPlotterServer
from massseer.server.TwoDimensionPlotterServer import TwoDimensionPlotterServer
from massseer.server.ThreeDimensionPlotterServer import ThreeDimensionalPlotter
from massseer.server.util import check_ion_mobility
# Structs 
from massseer.structs.TargetedDIAConfig import TargetedDIAConfig
from massseer.structs.TransitionGroupFeature import TransitionGroupFeature
from massseer.structs.FeatureMap import FeatureMap
# Loaders
from massseer.loaders.SpectralLibraryLoader import SpectralLibraryLoader
from massseer.loaders.MzMLDataLoader import MzMLDataLoader
# Util
from massseer.util import LOGGER, conditional_decorator, check_streamlit, time_block, MeasureBlock

class RawTargetedExtractionAnalysisServer:
    
    def __init__(self, massseer_gui):
        self.massseer_gui = massseer_gui
        self.transition_list_file_path = None
        self.raw_file_path_input = None
        self.feature_file_path = None 
        self.threads = None
        self.feature_data = None
        self.transition_list = None
        self.mzml_loader = None

        LOGGER.name = "RawTargetedExtractionAnalysisServer"
        if massseer_gui.verbose:
            LOGGER.setLevel("DEBUG")
        else:
            LOGGER.setLevel("INFO")
        
    def get_transition_list(self):
        """
        Loads the spectral library and sets the transition list attribute.
        """
        self.transition_list = self.mzml_loader.libraryFile
        self.transition_list.has_im = self.mzml_loader.libraryFile.data.has_im
        self.transition_list.data = self.mzml_loader.libraryFile.data.data

    def append_qvalues_to_transition_list(self):
        """
        Appends q-values to the transition list.
        """
        # top_ranked_precursor_features = self.feature_data.get_top_rank_precursor_features_across_runs()
        top_ranked_precursor_features = self.mzml_loader.rsltsFile.df[['ProteinId', 'PeptideSequence', 'ModifiedPeptideSequence',  'PrecursorCharge', 'Qvalue']]
        # If Decoy column not in transition list add it to top_ranked_precursor_features
        if 'Decoy' not in self.transition_list.data.columns:
            top_ranked_precursor_features['Decoy'] = 0
        # i.e. Convert .(UniMod:1)SEGDSVGESVHGKPSVVYR to (UniMod:1)SEGDSVGESVHGKPSVVYR
        top_ranked_precursor_features['ModifiedPeptideSequence'] = top_ranked_precursor_features['ModifiedPeptideSequence'].str.replace('.', '')
        self.transition_list.data['ModifiedPeptideSequence'] = self.transition_list.data['ModifiedPeptideSequence'].str.replace('.', '')
        # merge transition list with top ranked precursor features
        self.transition_list.data = pd.merge(self.transition_list.data, top_ranked_precursor_features, on=['ProteinId', 'PeptideSequence', 'ModifiedPeptideSequence', 'PrecursorCharge'], how='left')
        # Qvalue column is NaN replace with 1
        self.transition_list.data['Qvalue'] = self.transition_list.data['Qvalue'].fillna(1)
        # Decoy column is NaN replace with 0
        self.transition_list.data['Decoy'] = self.transition_list.data['Decoy'].fillna(0)
    
    # @conditional_decorator(lambda func: st.cache_resource(show_spinner="Loading data...")(func), check_streamlit())
    def initiate_mzML_interface(self, mzml_files, resultsFile, dataFile, resultsFileType, verbose) -> None:
        """
        Initiate an mzMLLoader Object.

        Args:
            mzml_files (List[str]): List of paths to the mzML files.
            resultsFile (str): Path to the results file.
            dataFile (str): Path to the data file.
            resultsFileType (str): The type of the results file.
            verbose (bool): Whether or not to print verbose output.
        
        """
        st.write(resultsFile)
        self.mzml_loader = MzMLDataLoader(resultsFile, mzml_files, dataFile, resultsFileType, verbose)

    @conditional_decorator(lambda func: st.cache_resource(show_spinner="Extracting data...")(func), check_streamlit())
    def targeted_extraction(_self, _transition_list_ui: RawTargetedExtractionAnalysisUI) -> List[FeatureMap]:
        """
        Perform targeted extraction on the given targeted experiment using the provided peptide coordinates and configuration.

        Args:
            _self (object): The instance of the class.
            _targeted_exp (TargetedDIALoader): The targeted experiment to perform extraction on.
            _peptide_coord (Dict): The peptide coordinates to use for extraction.
            config: The configuration for the extraction.

        Returns:
            None
        """
        return _self.mzml_loader.loadFeatureMaps(_transition_list_ui.
                                                 transition_settings.selected_peptide, 
                                            _transition_list_ui.transition_settings.selected_charge,
                                            _transition_list_ui.targeted_exp_params)
          
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
    
    def main(self):
        
        # Initiate the mzML Loader object

        with st.status("Initiating .mzML files (this may take some time)....", expanded=True) as status:
            self.initiate_mzML_interface(self.massseer_gui.file_input_settings.raw_file_path_list, 
                                        self.massseer_gui.file_input_settings.feature_file_path, 
                                        self.massseer_gui.file_input_settings.transition_list_file_path, 
                                        self.massseer_gui.file_input_settings.feature_file_type,
                                        self.massseer_gui.verbose)
                
        # Get and append q-values to the transition list
        self.get_transition_list()
        self.append_qvalues_to_transition_list()
        
        # Create a UI for the transition list and show transition information
        transition_list_ui = RawTargetedExtractionAnalysisUI(self.transition_list, self.mzml_loader.has_im, self.massseer_gui.verbose)
        transition_list_ui.show_transition_information()
        
        # Load feature data for selected peptide and charge
        self.load_transition_group_feature.clear()
        features = self.load_transition_group_feature(transition_list_ui)
        
        transition_list_ui.show_search_results_information(features) 

        # Create UI for extraction parameters
        transition_list_ui.show_extraction_parameters()

        # Create UI settings for chromatogram plotting, peak picking, and consensus chromatogram
        chrom_plot_settings = ChromatogramPlotUISettings()
        chrom_plot_settings.create_ui(include_raw_data_settings=True, is_ion_mobility_data=self.mzml_loader.has_im)

        peak_picking_settings = PeakPickingUISettings()
        peak_picking_settings.create_ui(chrom_plot_settings)

        concensus_chromatogram_settings = ConcensusChromatogramUISettings()
        concensus_chromatogram_settings.create_ui()
        
        # Create a container for the plots
        plot_container = st.container()
        
        # Load data from mzML files
        with st.status("Performing Peak Extraction....", expanded=True) as status:
            start_time = timeit.default_timer()
            self.targeted_extraction.clear()
            featureMaps = self.targeted_extraction(transition_list_ui)
            
            transitionGroupChromatograms = { f:fm.to_chromatograms() for f, fm in featureMaps.items()}
            st.write(transitionGroupChromatograms)
            st.dataframe([fm.feature_df for fm in featureMaps.values()][0])
            # Perform peak picking
            peak_picker = PeakPickingServer(peak_picking_settings, chrom_plot_settings)
            tr_group_feature_data = peak_picker.perform_peak_picking(tr_group_data=transitionGroupChromatograms, transition_list_ui=transition_list_ui)
        
            with time_block() as elapsed_time:
                # Initialize plot object dictionary
                plot_obj_dict = {}
                if chrom_plot_settings.display_plot_dimension_type == "1D":
                    plot_obj_dict = OneDimensionPlotterServer(transitionGroupChromatograms, tr_group_feature_data, transition_list_ui, chrom_plot_settings, self.massseer_gui.verbose).generate_chromatogram_plots().plot_obj_dict
                elif chrom_plot_settings.display_plot_dimension_type == "2D":
                    plot_obj_dict = TwoDimensionPlotterServer(featureMaps, transition_list_ui, chrom_plot_settings).generate_two_dimensional_plots().plot_obj_dict
                elif chrom_plot_settings.display_plot_dimension_type == "3D":
                    plot_obj_dict = ThreeDimensionalPlotter(featureMaps, transition_list_ui, chrom_plot_settings).generate_three_dimensional_plots().plot_obj_dict
            st.write(f'Generating plot... Elapsed time: {elapsed_time()}')
            
            # Show extracted data
            with time_block() as elapsed_time:
                if chrom_plot_settings.display_plot_dimension_type == "1D":
                    transition_list_ui.show_extracted_one_d_plots(plot_container, chrom_plot_settings, concensus_chromatogram_settings, plot_obj_dict)
                elif chrom_plot_settings.display_plot_dimension_type == "2D":
                    transition_list_ui.show_extracted_two_d_plots(plot_container, plot_obj_dict)
                elif chrom_plot_settings.display_plot_dimension_type == "3D":
                    transition_list_ui.show_extracted_three_d_plots(plot_container, plot_obj_dict, chrom_plot_settings.num_plot_columns)
            st.write(f'Displaying plot... Elapsed time: {elapsed_time()}')
                    
                    
            elapsed = timeit.default_timer() - start_time
            LOGGER.info("Targeted extraction complete! Elapsed time: %s", timedelta(seconds=elapsed))
            status.update(label=f"Info: Targeted extraction and plot drawing complete! Elapsed time: {timedelta(seconds=elapsed)}", state="complete", expanded=False)
        
        if chrom_plot_settings.display_extracted_data_as_df:
            transition_list_ui.show_extracted_dataframes(featureMaps)