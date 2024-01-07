"""
massdash/ui/RawTargetedExtractionAnalysisUI
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

from os.path import basename
import streamlit as st
import numpy as np
from typing import Literal, Dict

# Loaders
from loaders.SpectralLibraryLoader import SpectralLibraryLoader
from structs.TargetedDIAConfig import TargetedDIAConfig
# Structs
from structs.FeatureMap import FeatureMap
# UI
from .TransitionListUISettings import TransitionListUISettings
from .ChromatogramPlotUISettings import ChromatogramPlotUISettings
from .ConcensusChromatogramUISettings import ConcensusChromatogramUISettings

class RawTargetedExtractionAnalysisUI(TransitionListUISettings):
    
    def __init__(self, transition_list: SpectralLibraryLoader, is_ion_mobility_data: bool=False, verbose: bool=False) -> None:
        """
        Initializes the ExtractedIonChromatogramAnalysisServer object.

        Attributes:
            transition_list : object
                An object representing the transition list.
            transition_settings : object
                An object representing the transition list UI settings.
            target_transition_list : object
                An object representing the target transition list.
            targeted_exp_params : TargetedDIAConfig
                An object representing the targeted extraction parameters.
            is_ion_mobility_data : bool
                A boolean indicating whether or not the data is ion mobility data.
            include_ms1 : bool
                A boolean indicating whether or not to include MS1 data.
            include_ms2 : bool
                A boolean indicating whether or not to include MS2 data.
                
        Methods:
            show_transition_information()
                Displays the transition list UI and filters the transition list based on user input.
            show_search_results_information(search_results)
                Display the search results information in the sidebar.
            get_mslevel_list()
                Returns a list of MS levels based on the include_ms1 and include_ms2 attributes.
            get_peptide_dict(search_results)
                Returns a dictionary containing peptide information extracted from search results.
            show_extraction_parameters()
                Displays the extraction parameters in the sidebar UI.
            get_targeted_extraction_params_dict()
                Returns a dictionary containing the targeted extraction parameters.
            show_extracted_one_d_plots(plot_container, chrom_plot_settings, concensus_chromatogram_settings, plot_dict)
                Displays the extracted ion chromatograms based on user input.
            show_extracted_two_d_plots(plot_container, plot_dict)
                Displays the extracted ion chromatograms based on user input.
            show_extracted_three_d_plots(plot_container, plot_dict, num_cols)
                Displays the extracted ion chromatograms based on user input.
            show_extracted_dataframes(targeted_df_dict)
                Displays the extracted dataframes based on user input.            
        """
        super().__init__()
        self.transition_list = transition_list
        self.transition_settings = None
        self.target_transition_list = None
        self.targeted_exp_params = TargetedDIAConfig()
        self.is_ion_mobility_data = is_ion_mobility_data
        self.include_ms1 = True
        self.include_ms2 = True
        self.submit_extraction_params = False
        self.verbose = verbose
        
    def show_transition_information(self) -> None:
        """
        Displays the transition list UI and filters the transition list based on user input.
        """
        # Create a UI for the transition list
        self.transition_settings = TransitionListUISettings()
        st.sidebar.subheader("Transition list")
        # Checkbox to include decoys (default is False)
        self.transition_settings.include_decoys = st.sidebar.checkbox("Include decoys", value=False)
        if not self.transition_settings.include_decoys:
            self.transition_list.data = self.transition_list.data[self.transition_list.data["Decoy"] == 0]
        # Slider to filter transition list by q-value
        self.transition_settings.q_value_threshold = st.sidebar.number_input(
            "Q-value threshold",
            min_value=0.0000,
            max_value=1.0000,
            value=0.0100,
            step=0.0100,
            format="%0.10f",  # Fix the format string here
            help="Filter the transition list by q-value"
        )
        self.transition_list.data = self.transition_list.data[self.transition_list.data["Qvalue"] <= self.transition_settings.q_value_threshold]
        if self.transition_list.data.empty:
            st.error("Error: No transitions passed the q-value threshold! Increase the threshold.")
            st.stop()
        # Show proteins
        self.transition_settings.show_protein_selection(self.transition_list.get_unique_proteins())
        # Show peptides for selected protein
        self.transition_settings.show_peptide_selection(self.transition_list.get_unique_peptides_per_protein(self.transition_settings.selected_protein))
        # Show charge states for selected peptide
        self.transition_settings.show_charge_selection(self.transition_list.get_unique_charge_states_per_peptide(self.transition_settings.selected_peptide), self.transition_list)
        # Show library features
        self.transition_settings.show_library_features(self.transition_list)

        # Filter the transition list based on the selected protein, peptide and charge state
        self.target_transition_list =  self.transition_list.filter_for_target_transition_list(self.transition_settings.selected_protein, self.transition_settings.selected_peptide, self.transition_settings.selected_charge)
        
        if "selected_precursor" not in st.session_state:
            st.session_state.selected_precursor = f"{self.transition_settings.selected_protein}_{self.transition_settings.selected_peptide}_{self.transition_settings.selected_charge}"
        
    def show_search_results_information(self, search_results: Literal['DiaNNLoader', 'OSWLoader']) -> None:
        """
        Display the search results information in the sidebar.

        Args:
            search_results (Literal['DiaNNLoader', 'OSWLoader']) :
                An object representing the search results.

        Returns:
        None
        """

        st.sidebar.divider()
        st.sidebar.subheader("Search results")
        
        # Check to see if chromatogram peak feature apex is not none and mobilogram peak feature apex is not none to enable the use search results checkbox otherwise disable it
        if len(search_results.shape) > 0:
            enable_use_search_results_checkbox = search_results['consensusApex'] is not np.nan
            
            # Checkbox to use search results RT apex and IM apex for extraction parameters
            self.use_search_results_in_extraction = st.sidebar.checkbox("Use search result coordinates for extraction", value=True, disabled=not enable_use_search_results_checkbox)
            # Create tabs to display search results per file in search_results
            search_results_tabs = st.sidebar.tabs([f"Run{i}" for i in range(1, search_results.shape[0] + 1)])
            grouped_df = search_results.groupby('filename')
            for search_results_tab, (file, search_result) in zip(search_results_tabs, grouped_df):
                with search_results_tab:
                    with st.expander("Expand for search results", expanded=False):
                        # Get chromatogram peak feature RT and boundaries from search results
                        chrom_rt_apex = search_result['consensusApex'].values[0]
                        chrom_rt_start = search_result['leftBoundary'].values[0]
                        chrom_rt_end = search_result['rightBoundary'].values[0]
                        # Get chromatogram intensity and qvalue from search results
                        chrom_intensity = search_result['areaIntensity'].values[0]
                        chrom_qvalue = search_result['qvalue'].values[0]
                        
                        if self.is_ion_mobility_data:
                            # Get mobilogram peak feature Im apex from search results
                            mobilogram_im_apex = search_result['consensusApexIM'].values[0]

                        # Display in sidebar
                        st.markdown(f"**{basename(file)}**")
                        st.markdown("**Chromatogram peak feature**")
                        st.code(f"RT: {chrom_rt_apex}\nRT start: {chrom_rt_start}\nRT end: {chrom_rt_end}\nIntensity: {chrom_intensity}\nQvalue: {chrom_qvalue}", language="markdown")
                        if self.is_ion_mobility_data:
                            st.markdown("**Mobilogram peak feature**")
                            st.code(f"IM: {mobilogram_im_apex}", language="markdown")
        else:
            enable_use_search_results_checkbox = False
            self.use_search_results_in_extraction = False
            st.sidebar.info("No search results found. Load a search results file if you want to use search results for extraction parameters.")

    def get_mslevel_list(self) -> list:
        """
        Returns a list of MS levels based on the include_ms1 and include_ms2 attributes.

        Returns:
            list: A list of MS levels.
        """
        mslevel_list = []
        if self.include_ms1:
            mslevel_list.append(1)
        if self.include_ms2:
            mslevel_list.append(2)
        return mslevel_list

    def get_peptide_dict(self, search_results: Literal['DiaNNLoader', 'OSWLoader']) -> Dict:
        """
        Returns a dictionary containing peptide information extracted from search results.

        Args:
            search_results (Literal['DiaNNLoader', 'OSWLoader']): The type of search results.

        Returns:
            dict: A dictionary containing peptide information.

        Example:
            peptides = { 
                'T(UniMod:21)ELISVSEVHPSR_2': {
                    'peptide': 'T(UniMod:21)ELISVSEVHPSR', 
                    'precursor_mz': 767.3691, 
                    'charge': 2, 
                    'rt_apex': 1730.08, 
                    'im_apex': 1.026132868499893, 
                    'qvalue': 0.0, 
                    'product_mz': [496.2627, 811.4057, 910.4741, 997.5061, 1110.5902, 1223.6743], 
                    'product_charge': [1, 1, 1, 1, 1, 1], 
                    'product_annotation': ['y4^1', 'y7^1', 'y8^1', 'y9^1', 'y10^1', 'y11^1'], 
                    'product_detecting': [1, 1, 1, 1, 1, 1], 
                    'rt_boundaries': [1718.036865234375, 1751.983642578125]}}
        """
        file_peptide_dict = {}
        for file, file_search_results in search_results.items():
            # Use search results RT and IM apexs if available
            if file_search_results['chromatogram_peak_feature'].consensusApex is not None:
                use_rt_apex = file_search_results['chromatogram_peak_feature'].consensusApex
            else:
                use_rt_apex = self.transition_list.get_peptide_retention_time(self.transition_settings.selected_peptide, self.transition_settings.selected_charge)

            if file_search_results['mobilogram_peak_feature'].consensusApex is not None:
                use_im_apex = file_search_results['mobilogram_peak_feature'].consensusApex
            else:
                use_im_apex = self.transition_list.get_peptide_ion_mobility(self.transition_settings.selected_peptide, self.transition_settings.selected_charge)

            # Use search results RT boundaries if available and search results qvalue and intensity
            if file_search_results['chromatogram_peak_feature'].leftBoundary is not None and file_search_results['chromatogram_peak_feature'].rightBoundary is not None:
                use_rt_boundaries = [file_search_results['chromatogram_peak_feature'].leftBoundary, file_search_results['chromatogram_peak_feature'].rightBoundary]
            else:
                # TODO: Need to figure a better way of dealing with this. Downstream code expects a list of two values
                use_rt_boundaries = [0, 8000]

            if file_search_results['chromatogram_peak_feature'].qvalue is not None:
                use_qvalue = file_search_results['chromatogram_peak_feature'].qvalue
            else:
                use_qvalue = None

            if file_search_results['chromatogram_peak_feature'].areaIntensity is not None:
                use_area_intensity = file_search_results['chromatogram_peak_feature'].areaIntensity
            else:
                use_area_intensity = None

            peptide_dict = {}
            peptide_dict[self.transition_settings.selected_peptide + "_" + str(self.transition_settings.selected_charge)] = {
                'peptide': self.transition_settings.selected_peptide, 'precursor_mz': self.transition_list.get_peptide_precursor_mz(self.transition_settings.selected_peptide, self.transition_settings.selected_charge), 
                'charge': self.transition_settings.selected_charge, 
                'rt_apex': use_rt_apex,
                'im_apex': use_im_apex,
                'qvalue': use_qvalue, 
                'product_mz': self.transition_list.get_peptide_product_mz_list(self.transition_settings.selected_peptide, self.transition_settings.selected_charge),
                'product_charge': self.transition_list.get_peptide_product_charge_list(self.transition_settings.selected_peptide, self.transition_settings.selected_charge),
                'product_annotation': self.transition_list.get_peptide_fragment_annotation_list(self.transition_settings.selected_peptide, self.transition_settings.selected_charge),
                'product_detecting': [], 
                'rt_boundaries': use_rt_boundaries,
                'area_intensity': use_area_intensity}
            file_peptide_dict[file.filename] = peptide_dict
        return file_peptide_dict

    def show_extraction_parameters(self) -> None:
        """
        Displays the extraction parameters in the sidebar UI.

        Returns:
            None
        """
        st.sidebar.divider()
        st.sidebar.subheader("Extraction parameters")
        # UI for two column checkbox to include MS1 and/or MS2
        col1, col2 = st.sidebar.columns(2)
        with col1:
            self.include_ms1 = st.checkbox("Include MS1", value=True)
        with col2:
            self.include_ms2 = st.checkbox("Include MS2", value=True)

        self.targeted_exp_params.mslevel = self.get_mslevel_list()

        # Advanced UI paramaters
        with st.sidebar.expander("Advanced parameters", expanded=True):
            extraction_param_form = st.form(key="extraction_param_form")
            # UI for MS1 MZ tolerance in ppm
            self.targeted_exp_params.ms1_mz_tol = extraction_param_form.number_input("MS1 m/z tolerance (ppm)", value=20, help="MS1 m/z tolerance in ppm")
            # UI for MS2 MZ tolerance in ppm
            self.targeted_exp_params.mz_tol = extraction_param_form.number_input("MS2 m/z tolerance (ppm)", value=20, help="MS2 m/z tolerance in ppm")
            # UI for RT extraction window in seconds
            self.targeted_exp_params.rt_window = extraction_param_form.number_input("RT window (seconds)", value=35, help="RT extraction window in seconds")
            if self.is_ion_mobility_data:
                # UI for IM extraction window in 1/K0
                self.targeted_exp_params.im_window = extraction_param_form.number_input("IM window (1/K0)", value=0.0600, format="%.8f", help="IM extraction window in 1/K0")
            else:
                self.targeted_exp_params.im_window = 0.0
                
            self.submit_extraction_params = extraction_param_form.form_submit_button("Extract Data")
            
            if self.submit_extraction_params:
                st.session_state.extraction_param_button_clicked = True
            else:
                st.session_state.extraction_param_button_clicked = False
            
    def get_targeted_extraction_params_dict(self) -> Dict:
        """
        Returns a dictionary containing the targeted extraction parameters.

        Returns:
            dict: A dictionary containing the following parameters:
                - 'mslevel': The list of MS levels to consider.
                - 'ms1_mz_tol': The m/z tolerance for MS1 scans.
                - 'mz_tol': The m/z tolerance for MS2 scans.
                - 'rt_window': The retention time window for targeted extraction.
                - 'im_window': The ion mobility window for targeted extraction.
        """
        extraction_params_dict = {
            'mslevel': self.get_mslevel_list(),
            'ms1_mz_tol': self.targeted_exp_params.ms1_mz_tol,
            'mz_tol': self.targeted_exp_params.mz_tol,
            'rt_window': self.targeted_exp_params.rt_window,
            'im_window': self.targeted_exp_params.im_window
        }
        return extraction_params_dict
   
    def validate_extraction(self, featureMap: FeatureMap, plot_container: st.container):
        fm_states = [fm.empty() for fm in featureMap.values()]
        if any(fm_states):
            plot_container.error("No spectra found/extracted for the selected precursor. Try adjusting the extraction parameters.")
       
    def show_extracted_one_d_plots(self, plot_container: st.container, chrom_plot_settings: ChromatogramPlotUISettings, concensus_chromatogram_settings: ConcensusChromatogramUISettings, plot_dict: Dict) -> None:
        """
        Displays the extracted ion chromatograms based on user input.

        Args:
        plot_container : st.container
            A container for the plots.
        chrom_plot_settings : ChromatogramPlotSettings
            An instance of the ChromatogramPlotSettings class.
        concensus_chromatogram_settings : ConsensusChromatogramSettings
            An instance of the ConsensusChromatogramSettings class.
        plot_dict : dict
            A dictionary containing the plot objects for each file.
        """
        with plot_container:
            if len(plot_dict[list(plot_dict.keys())[0]]) == 1:
                cols = st.columns(chrom_plot_settings.num_plot_columns)
                for col, (file, run_plots_list) in zip(cols, plot_dict.items()):
                    with col:
                        st.bokeh_chart(run_plots_list[0])
            else:
                for file, run_plots_list in plot_dict.items():
                    super_plot_title = run_plots_list[0].title
                    st.subheader(super_plot_title.text)
                    cols = st.columns(len(run_plots_list))
                    for i, col in enumerate(cols):
                        with col:
                            run_plots_list[i].title = None
                            st.bokeh_chart(run_plots_list[i])
        
    def show_extracted_two_d_plots(self, plot_container: st.container, plot_dict: Dict) -> None:
        """
        Displays the extracted ion chromatograms based on user input.

        Args:
        plot_container : st.container
            A container for the plots.
        plot_dict : dict
            A dictionary containing the plot objects for each file.
        """
        with plot_container:
            for file, p in plot_dict.items():
                st.bokeh_chart(p)
                    
    def show_extracted_three_d_plots(self, plot_container: st.container, plot_dict: Dict, num_cols: int) -> None:
        """
        Displays the extracted ion chromatograms based on user input.

        Args:
        plot_container : st.container
            A container for the plots.
        plot_dict : dict
            A dictionary containing the plot objects for each file.
        num_cols : int
            The number of columns to display the plots in.
        """
        if len(plot_dict) < num_cols:
            num_cols = len(plot_dict)
        with plot_container:
            cols = st.columns(num_cols)
            for col, (file, p) in zip(cols, plot_dict.items()):
                p.update_layout(title_text = basename(file))
                with col:
                    st.plotly_chart(p, theme="streamlit", use_container_width=True)
                
    def show_extracted_dataframes(self, targeted_df_dict: Dict) -> None:
        """
        Displays the extracted dataframes based on user input.

        Args:
        targeted_df_dict : dict
            A dictionary containing the extracted dataframes for each file.
        """
        # Display the extracted dataframes in tabs per file key in targeted_df_dict
        
        # Create streamlit tabs to store the extracted dataframes
        df_tabs = st.tabs([basename(f) for f in targeted_df_dict.keys()])
        
        for df_tab, feature_map in zip(df_tabs, targeted_df_dict.values()):
            with df_tab:
                st.dataframe(feature_map.feature_df, hide_index=True, column_order =('native_id', 'ms_level', 'precursor_mz', 'product_mz', 'mz', 'rt', 'im', 'int', 'rt_apex', 'rt_left_width', 'rt_right_width', 'im_apex', 'PrecursorCharge', 'ProductCharge', 'LibraryIntensity', 'NormalizedRetentionTime', 'PeptideSequence', 'ModifiedPeptideSequence', 'ProteinId', 'GeneName', 'Annotation', 'PrecursorIonMobility'))