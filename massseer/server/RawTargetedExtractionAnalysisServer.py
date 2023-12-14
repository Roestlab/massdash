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
# Loaders
from massseer.loaders.OSWLoader import OSWLoader
from massseer.loaders.DiaNNLoader import DiaNNLoader
from massseer.loaders.SpectralLibraryLoader import SpectralLibraryLoader
from massseer.loaders.TargetedDIALoader import TargetedDIALoader
from massseer.loaders.TargetedDIADataAccess import TargetedDIAConfig, TargetedDIADataAccess
# Util
from massseer.util import LOGGER, conditional_decorator, check_streamlit, time_block

class RawTargetedExtractionAnalysisServer:
    
    def __init__(self, massseer_gui):
        self.massseer_gui = massseer_gui
        self.transition_list_file_path = None
        self.raw_file_path_input = None
        self.feature_file_path = None 
        self.threads = None
        self.feature_data = None
        self.transition_list = None

        LOGGER.name = "RawTargetedExtractionAnalysisServer"
        if massseer_gui.verbose:
            LOGGER.setLevel("DEBUG")
        else:
            LOGGER.setLevel("INFO")
        
    def get_transition_list(self):
        """
        Loads the spectral library and sets the transition list attribute.
        """
        self.transition_list = SpectralLibraryLoader(self.massseer_gui.file_input_settings.transition_list_file_path, self.massseer_gui.verbose)
        self.transition_list.load()

    def append_qvalues_to_transition_list(self):
        """
        Appends q-values to the transition list.
        """
        # top_ranked_precursor_features = self.feature_data.get_top_rank_precursor_features_across_runs()
        top_ranked_precursor_features = self.feature_data.report.search_data[['ProteinId', 'PeptideSequence', 'ModifiedPeptideSequence',  'PrecursorCharge', 'Qvalue']]
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
    
    @conditional_decorator(lambda func: st.cache_resource(show_spinner="Loading data...")(func), check_streamlit())
    def load_targeted_experiment(_self, mzml_files: List[str], _targeted_exp_params: TargetedDIAConfig, verbose: bool):
        """
        Load a targeted experiment from the given mzML files using the specified parameters.

        Args:
            mzml_files (List[str]): List of paths to the mzML files.
            _targeted_exp_params (TargetedDIAConfig): Parameters for the targeted experiment.
            verbose (bool): Whether or not to print verbose output.

        Returns:
            TargetedDIALoader: The loaded targeted experiment.
        """
        _self.targeted_exp = TargetedDIALoader(mzml_files, None, _targeted_exp_params, verbose)
        _self.targeted_exp.load_mzml_data()
        return _self.targeted_exp
    
    @conditional_decorator(lambda func: st.cache_resource(show_spinner="Accessing data...")(func), check_streamlit())
    def targeted_data_access(_self, _targeted_exp: TargetedDIALoader) -> None:
        """
        Accesses the targeted DIA data.

        Args:
            _self: The instance of the class.
            _targeted_exp: The TargetedDIALoader object containing the targeted DIA data.

        Returns:
            None
        """
        _targeted_exp.targeted_diapasef_data_access()
    
    @conditional_decorator(lambda func: st.cache_resource(show_spinner="Extracting data...")(func), check_streamlit())
    def targeted_extraction(_self, _targeted_exp: TargetedDIALoader, _peptide_coord: Dict, config) -> None:
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
        _targeted_exp.reduce_targeted_spectra(_peptide_coord, config)
        

    def get_targeted_data(_self, _transition_list_ui, _targeted_exp: TargetedDIALoader):
        """
        Retrieves targeted data from a TargetedDIALoader object based on the provided transition list and settings.

        Args:
            _self: The instance of the RawTargetedExtractionAnalysisServer class.
            _transition_list_ui: The instance of the TransitionListUI class.
            _targeted_exp: The instance of the TargetedDIALoader class.

        Returns:
            The targeted data as a dataframe.

        """
        targeted_data = _targeted_exp.get_targeted_dataframe(_transition_list_ui.get_mslevel_list(), _self.transition_list.get_peptide_product_mz_list(_transition_list_ui.transition_settings.selected_peptide, _transition_list_ui.transition_settings.selected_charge), _transition_list_ui.target_transition_list)
        return targeted_data
    
    def load_transition_group(_self, _targeted_exp: TargetedDIALoader, target_transition_list: pd.DataFrame):
        """
        Load the transition group from the targeted experiment.

        Args:
            _self (RawTargetedExtractionAnalysisServer): The instance of the server.
            _targeted_exp (TargetedDIALoader): The targeted experiment loader.
            target_transition_list (pd.DataFrame): The target transition list.

        Returns:
            The loaded transition group.
        """
        return _targeted_exp.loadTransitionGroups(target_transition_list)
    
    def main(self):
        
        # Load feature file if available
        # Check if feature file ends with a tsv
        if self.massseer_gui.file_input_settings.feature_file_path.endswith('.tsv'):
            self.feature_data = DiaNNLoader(self.massseer_gui.file_input_settings.feature_file_path, self.massseer_gui.verbose)
            self.feature_data.load_report()
        elif self.massseer_gui.file_input_settings.feature_file_path.endswith('.osw'):
            self.feature_data = OSWLoader(self.massseer_gui.file_input_settings.feature_file_path, self.massseer_gui.file_input_settings.raw_file_path_list, self.massseer_gui.verbose)
            self.feature_data.load_report()
 
        # Get and append q-values to the transition list
        self.get_transition_list()
        self.append_qvalues_to_transition_list()
        
        # Check first mzML file for ion mobility
        is_ion_mobility_data = check_ion_mobility(self.massseer_gui.file_input_settings.raw_file_path_list[0])
        
        # Create a UI for the transition list and show transition information
        transition_list_ui = RawTargetedExtractionAnalysisUI(self.transition_list, is_ion_mobility_data, self.massseer_gui.verbose)
        transition_list_ui.show_transition_information()
        
        # Load feature data for selected peptide and charge
        self.feature_data.load_report_for_precursor(transition_list_ui.transition_settings.selected_peptide, transition_list_ui.transition_settings.selected_charge)
        
        transition_list_ui.show_search_results_information(self.feature_data.report)

        # Create UI for extraction parameters
        transition_list_ui.show_extraction_parameters()

        # Create UI settings for chromatogram plotting, peak picking, and consensus chromatogram
        chrom_plot_settings = ChromatogramPlotUISettings()
        chrom_plot_settings.create_ui(include_raw_data_settings=True, is_ion_mobility_data=is_ion_mobility_data)

        peak_picking_settings = PeakPickingUISettings()
        peak_picking_settings.create_ui(chrom_plot_settings)

        concensus_chromatogram_settings = ConcensusChromatogramUISettings()
        concensus_chromatogram_settings.create_ui()
        
        # Create a container for the plots
        plot_container = st.container()
        
        # Load data from mzML files
        start_time = timeit.default_timer()
        with st.status("Performing targeted extraction (this may take some time on the first load)...", expanded=True) as status:
            with time_block() as elapsed_time:
                targeted_exp = self.load_targeted_experiment(self.massseer_gui.file_input_settings.raw_file_path_list, transition_list_ui.targeted_exp_params, self.massseer_gui.verbose)
            st.write(f"Loading raw file... Elapsed time: {elapsed_time()}") 
            
            with time_block() as elapsed_time:
                self.targeted_data_access(targeted_exp)
            st.write(f"Setting up extraction parameters... Elapsed time: {elapsed_time()}")
            
            with time_block() as elapsed_time:
                peptide_coord = transition_list_ui.get_peptide_dict(self.feature_data.report)
                targeted_extraction_params = transition_list_ui.get_targeted_extraction_params_dict()
                LOGGER.debug(f"Targeted Extraction Paramters: {targeted_extraction_params}")
                LOGGER.debug(f"Targeted Extraction Peptide Coordiantes: {peptide_coord}")
                self.targeted_extraction(targeted_exp, peptide_coord, targeted_extraction_params)
            st.write(f"Extracting data... Elapsed time: {elapsed_time()}")
            
            with time_block() as elapsed_time:
                targeted_data = self.get_targeted_data(transition_list_ui, targeted_exp)
            st.write(f'Getting data as a pandas dataframe... Elapsed time: {elapsed_time()}')
            
            with time_block() as elapsed_time:
                transition_group_dict = self.load_transition_group(targeted_exp, transition_list_ui.target_transition_list)
            st.write(f'Creating TransitionGroup... Elapsed time: {elapsed_time()}')
            
            # Perform peak picking
            peak_picker = PeakPickingServer(peak_picking_settings, chrom_plot_settings)
            tr_group_feature_data = peak_picker.perform_peak_picking(tr_group_data=transition_group_dict, transition_list_ui=transition_list_ui)
            
            with time_block() as elapsed_time:
                # Initialize plot object dictionary
                plot_obj_dict = {}
                if chrom_plot_settings.display_plot_dimension_type == "1D":
                    plot_obj_dict = OneDimensionPlotterServer(transition_group_dict, tr_group_feature_data, transition_list_ui, chrom_plot_settings, self.massseer_gui.verbose).generate_chromatogram_plots().plot_obj_dict
                elif chrom_plot_settings.display_plot_dimension_type == "2D":
                    plot_obj_dict = TwoDimensionPlotterServer(targeted_data, transition_list_ui, chrom_plot_settings).generate_two_dimensional_plots().plot_obj_dict
                elif chrom_plot_settings.display_plot_dimension_type == "3D":
                    plot_obj_dict = ThreeDimensionalPlotter(targeted_data, transition_list_ui, chrom_plot_settings).generate_three_dimensional_plots().plot_obj_dict
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
        LOGGER.info(f"Targeted extraction complete! Elapsed time: {timedelta(seconds=elapsed)}")
        status.update(label=f"Info: Targeted extraction and plot drawing complete! Elapsed time: {timedelta(seconds=elapsed)}", state="complete", expanded=False)
    
        if chrom_plot_settings.display_extracted_data_as_df:
            transition_list_ui.show_extracted_dataframes(targeted_data)