import streamlit as st
import numpy as np
import pandas as pd
from typing import List, Dict

# UI imports
from massseer.file_handling_ui import TransitionListUI

# Server side imports
from massseer.util import get_logger
from massseer.loaders.SpectralLibraryLoader import SpectralLibraryLoader
from massseer.loaders.TargeteddiaPASEFLoader import TargeteddiaPASEFLoader
from massseer.loaders.TargeteddiaPASEFDataAccess import TargeteddiaPASEFConfig
from massseer.targeted_data_extraction import TargeteddiaPASEFExperiment

class TargetedExperimentUI(TransitionListUI):
    def __init__(self, transition_list: SpectralLibraryLoader) -> None:
        super().__init__()
        self.transition_list = transition_list
        self.target_transition_list = None
        self.search_results = None
        self.targeted_exp_params = TargeteddiaPASEFConfig()

    def show(self) -> None:
        self.show_protein_selection()
        self.show_peptide_selection()
        self.show_charge_state_selection()
        self.show_transition_list()
        self.show_chromatogram_plot()

    def show_transition_information(self) -> None:
        # Create a UI for the transition list
        self.transition_settings = TransitionListUI()
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

    def update_transition_information(self, filtered_analyte_data: pd.DataFrame) -> None:
        new_protein_data = filtered_analyte_data['Protein.Ids'].tolist()
        new_peptide_data = filtered_analyte_data['Modified.Sequence'].tolist()
        print(f"len new_protein_data: {len(new_protein_data)}")
        # Update protein selection
        self.transition_settings.update_protein_selection(new_protein_data)
        # Update peptide selection
        # self.transition_settings.update_peptide_selection(new_peptide_data)

    def show_search_results_information(self) -> None:
        st.sidebar.divider()
        st.sidebar.subheader("Search results")
        # QValue threshold numeric input to filter search results and filter transition list based on filtered search results
        self.qvalue_threshold = st.sidebar.number_input("QValue threshold", value=0.01, format="%.9f" )
        # Check to see if chromatogram peak feature apex is not none and mobilogram peak feature apex is not none to enable the use search results checkbox otherwise disable it
        enable_use_search_results_checkbox = self.search_results.chromatogram_peak_feature.apex is not None and self.search_results.mobilogram_peak_feature.apex is not None
        # Checkbox to use search results RT apex and IM apex for extraction parameters
        self.use_search_results_in_extraction = st.sidebar.checkbox("Use search result coordinates for extraction", value=True, disabled=not enable_use_search_results_checkbox)
        with st.sidebar.expander("Expand for search results", expanded=False):
            # Get chromatogram peak feature RT and boundaries from search results
            chrom_rt_apex = self.search_results.chromatogram_peak_feature.apex
            chrom_rt_start = self.search_results.chromatogram_peak_feature.leftWidth
            chrom_rt_end = self.search_results.chromatogram_peak_feature.rightWidth
            # Get chromatogram intensity and qvalue from search results
            chrom_intensity = self.search_results.chromatogram_peak_feature.area_intensity
            chrom_qvalue = self.search_results.chromatogram_peak_feature.qvalue

            # Get mobilogram peak feature Im apex from search results
            mobilogram_im_apex = self.search_results.mobilogram_peak_feature.apex

            # Display in sidebar
            st.markdown("**Chromatogram peak feature**")
            st.code(f"RT: {chrom_rt_apex}\nRT start: {chrom_rt_start}\nRT end: {chrom_rt_end}\nIntensity: {chrom_intensity}\nQvalue: {chrom_qvalue}", language="markdown")
            st.markdown("**Mobilogram peak feature**")
            st.code(f"IM: {mobilogram_im_apex}", language="markdown")

    def show_extraction_parameters(self) -> None:
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
        with st.sidebar.expander("Advanced parameters", expanded=False):
            # UI for MS1 MZ tolerance in ppm
            self.targeted_exp_params.ms1_mz_tol = st.number_input("MS1 m/z tolerance (ppm)", value=20)
            # UI for MS2 MZ tolerance in ppm
            self.targeted_exp_params.mz_tol = st.number_input("MS2 m/z tolerance (ppm)", value=20)
            # UI for RT extraction window in seconds
            self.targeted_exp_params.rt_window = st.number_input("RT window (seconds)", value=50)
            # UI for IM extraction window in 1/K0
            self.targeted_exp_params.im_window = st.number_input("IM window (1/K0)", value=0.06)

    def get_mslevel_list(self) -> list:
        mslevel_list = []
        if self.include_ms1:
            mslevel_list.append(1)
        if self.include_ms2:
            mslevel_list.append(2)
        return mslevel_list

    def get_peptide_dict(self) -> dict:
        # Expected Peptide dict structure example
        # peptides = { 
        #   'T(UniMod:21)ELISVSEVHPSR_2': {
        #         'peptide': 'T(UniMod:21)ELISVSEVHPSR', 
        #         'precursor_mz': 767.3691, 
        #         'charge': 2, 
        #         'rt_apex': 1730.08, 
        #         'im_apex': 1.026132868499893, 
        #         'qvalue': 0.0, 
        #         'product_mz': [496.2627, 811.4057, 910.4741, 997.5061, 1110.5902, 1223.6743], 
        #         'product_charge': [1, 1, 1, 1, 1, 1], 
        #         'product_annotation': ['y4^1', 'y7^1', 'y8^1', 'y9^1', 'y10^1', 'y11^1'], 
        #         'product_detecting': [1, 1, 1, 1, 1, 1], 
        #         'rt_boundaries': [1718.036865234375, 1751.983642578125]}}
        
        # Use search results RT and IM apexs if available
        if self.search_results.chromatogram_peak_feature.apex is not None:
            use_rt_apex = self.search_results.chromatogram_peak_feature.apex
        else:
            use_rt_apex = self.transition_list.get_peptide_retention_time(self.transition_settings.selected_peptide, self.transition_settings.selected_charge)

        if self.search_results.mobilogram_peak_feature.apex is not None:
            use_im_apex = self.search_results.mobilogram_peak_feature.apex
        else:
            use_im_apex = self.transition_list.get_peptide_ion_mobility(self.transition_settings.selected_peptide, self.transition_settings.selected_charge)

        # Use search results RT boundaries if available and search results qvalue and intensity
        if self.search_results.chromatogram_peak_feature.leftWidth is not None and self.search_results.chromatogram_peak_feature.rightWidth is not None:
            use_rt_boundaries = [self.search_results.chromatogram_peak_feature.leftWidth, self.search_results.chromatogram_peak_feature.rightWidth]
        else:
            # TODO: Need to figure a better way of dealing with this. Downstream code expects a list of two values
            use_rt_boundaries = [0, 8000]

        if self.search_results.chromatogram_peak_feature.qvalue is not None:
            use_qvalue = self.search_results.chromatogram_peak_feature.qvalue
        else:
            use_qvalue = None

        if self.search_results.chromatogram_peak_feature.area_intensity is not None:
            use_area_intensity = self.search_results.chromatogram_peak_feature.area_intensity
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
        return peptide_dict

    @st.cache_resource(show_spinner="Loading data...")
    def load_targeted_experiment(_self, mzml_files: List[str]):
        _self.targeted_exp = TargeteddiaPASEFLoader(mzml_files, _self.targeted_exp_params)
        _self.targeted_exp.load_mzml_data()
        return _self.targeted_exp

    @st.cache_resource(show_spinner="Accessing data...")
    def targeted_data_access(_self, _targeted_exp: TargeteddiaPASEFLoader) -> None:
        _targeted_exp.targeted_diapasef_data_access()

    @st.cache_resource(show_spinner="Extracting data...")
    def targeted_extraction(_self, _targeted_exp: TargeteddiaPASEFLoader, peptide_coord: Dict) -> None:
        _targeted_exp.reduce_targeted_spectra(peptide_coord)

    # @st.cache_data(show_spinner="Returning data as dataframe...")  
    def get_targeted_data(_self, _targeted_exp: TargeteddiaPASEFLoader):
        print("HERE")
        print(_self.target_transition_list)
        targeted_data = _targeted_exp.get_targeted_dataframe(_self.get_mslevel_list(), _self.transition_list.get_peptide_product_mz_list(_self.transition_settings.selected_peptide, _self.transition_settings.selected_charge), _self.target_transition_list)

        return targeted_data
    
    def load_transition_group(_self, _targeted_exp: TargeteddiaPASEFLoader):
        return _targeted_exp.loadTransitionGroup(_self.target_transition_list)
    