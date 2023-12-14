import streamlit as st
import numpy as np
import pandas as pd
from typing import List, Dict

# UI imports
from massseer.file_handling_ui import TransitionListUI

# Server side imports
from massseer.util import get_logger
from massseer.util_ui import MassSeerGUI
from massseer.loaders.SpectralLibraryLoader import SpectralLibraryLoader
from massseer.loaders.DiaNNLoader import DiaNNLoader    
from massseer.loaders.TargetedDIALoader import TargeteddiaPASEFLoader
from massseer.loaders.TargetedDIADataAccess import TargeteddiaPASEFConfig
# from massseer.targeted_data_extraction import TargeteddiaPASEFExperiment

class TargetedExperimentUI(TransitionListUI):
    def __init__(self, massseer_gui: MassSeerGUI, transition_list: SpectralLibraryLoader) -> None:
        super().__init__()
        self.massseer_gui = massseer_gui
        self.transition_list = transition_list
        self.target_transition_list = None
        self.search_results = None
        self.targeted_exp_params = TargeteddiaPASEFConfig()

        if 'protein_list' not in st.session_state:   
            st.session_state['protein_list'] = []


    def show(self) -> None:
        self.show_protein_selection()
        self.show_peptide_selection()
        self.show_charge_state_selection()
        self.show_transition_list()
        self.show_chromatogram_plot()

    @staticmethod
    @st.cache_data(show_spinner=False)
    def filter_search_results_by_qvalue(_diann_data: DiaNNLoader, qvalue_threshold: float) -> pd.DataFrame:
        return _diann_data.filter_search_results_proteins_by_qvalue(qvalue_threshold)
    
    @st.cache_data(show_spinner=False)
    def get_protein_list(_self, qvalue_threshold, _diann_data: DiaNNLoader=None) -> List[str]:
        diann_qvalue_filtered_analytes = _self.filter_search_results_by_qvalue(_diann_data, qvalue_threshold)
        protein_list = diann_qvalue_filtered_analytes['Protein.Ids'].unique().tolist()
        # Filter for only proteins in the transition list
        protein_list = [protein for protein in protein_list if protein in _self.transition_list.get_unique_proteins()]
        return protein_list, diann_qvalue_filtered_analytes

    @st.cache_data(show_spinner=False)
    def get_peptide_list(_self, selected_proten,  _diann_qvalue_filtered_analytes: pd.DataFrame=None) -> List[str]:
        peptide_list = _diann_qvalue_filtered_analytes[_diann_qvalue_filtered_analytes['Protein.Ids'] == selected_proten]['Modified.Sequence'].unique().tolist()
        # Filter for only the peptides that are in the transition list
        peptide_list = [peptide for peptide in peptide_list if peptide in _self.transition_list.get_unique_peptides_per_protein(_self.transition_settings.selected_protein)]
        return peptide_list

    def show_transition_information(self, diann_data: DiaNNLoader=None) -> None:
        # Create a UI for the transition list
        self.transition_settings = TransitionListUI()
        if self.massseer_gui.diann_report_file_path_input != "*.tsv":
            # QValue threshold numeric input to filter search results and filter transition list based on filtered search results
            self.transition_settings.qvalue_threshold = st.sidebar.number_input("Filter Proteins by QValue", value=0.01, format="%.9f", help="If a search results file is supplied, you can filter the protein/precursor list by the QValue." )
            protein_list, diann_qvalue_filtered_analytes = self.get_protein_list(self.transition_settings.qvalue_threshold, diann_data)
            # Get protein lists
            st.session_state['protein_list'] = protein_list
        else:
            st.session_state['protein_list'] = self.transition_list.get_unique_proteins()

        # Show proteins
        self.transition_settings.show_protein_selection(st.session_state['protein_list'])

        # Get filtered peptides if a search results file is supplied
        if self.massseer_gui.diann_report_file_path_input != "*.tsv":
            peptide_list = self.get_peptide_list(self.transition_settings.selected_protein, diann_qvalue_filtered_analytes)
        else:
            peptide_list = self.transition_list.get_unique_peptides_per_protein(self.transition_settings.selected_protein)

        # Show peptides for selected protein
        self.transition_settings.show_peptide_selection(peptide_list)

        # Get filtered precursor charge states if a search results file is supplied
        if self.massseer_gui.diann_report_file_path_input != "*.tsv":
            charge_list = diann_qvalue_filtered_analytes[(diann_qvalue_filtered_analytes['Protein.Ids'] == self.transition_settings.selected_protein) & (diann_qvalue_filtered_analytes['Modified.Sequence'] == self.transition_settings.selected_peptide)]['Precursor.Charge'].unique().tolist()
            precursor_mz = diann_qvalue_filtered_analytes[(diann_qvalue_filtered_analytes['Protein.Ids'] == self.transition_settings.selected_protein) & (diann_qvalue_filtered_analytes['Modified.Sequence'] == self.transition_settings.selected_peptide)]['Precursor.Mz'].unique().tolist()[0]
        else:
            charge_list = self.transition_list.get_unique_charge_states_per_peptide(self.transition_settings.selected_peptide)
            precursor_mz = self.transition_list.get_peptide_precursor_mz(self.selected_peptide, self.selected_charge)

        # Show charge states for selected peptide
        self.transition_settings.show_charge_selection(charge_list, precursor_mz)

        # Show library features
        self.transition_settings.show_library_features(self.transition_list)

        # Filter the transition list based on the selected protein, peptide and charge state
        self.target_transition_list =  self.transition_list.filter_for_target_transition_list(self.transition_settings.selected_protein, self.transition_settings.selected_peptide, self.transition_settings.selected_charge)

    def show_search_results_information(self) -> None:
        st.sidebar.divider()
        st.sidebar.subheader("Search results")
        
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
            self.targeted_exp_params.rt_window = st.number_input("RT window (seconds)", value=35)
            # UI for IM extraction window in 1/K0
            self.targeted_exp_params.im_window = st.number_input("IM window (1/K0)", value=0.0600, format="%.8f")

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

    def get_targeted_extraction_params_dict(self) -> dict:
        extraction_params_dict = {
            'mslevel': self.get_mslevel_list(),
            'ms1_mz_tol': self.targeted_exp_params.ms1_mz_tol,
            'mz_tol': self.targeted_exp_params.mz_tol,
            'rt_window': self.targeted_exp_params.rt_window,
            'im_window': self.targeted_exp_params.im_window
        }
        return extraction_params_dict

    @st.cache_resource(show_spinner="Loading data...")
    def load_targeted_experiment(_self, mzml_files: List[str]):
        # print(_self.targeted_exp_params)
        _self.targeted_exp = TargeteddiaPASEFLoader(mzml_files, _self.targeted_exp_params)
        _self.targeted_exp.load_mzml_data()
        return _self.targeted_exp

    @st.cache_resource(show_spinner="Accessing data...")
    def targeted_data_access(_self, _targeted_exp: TargeteddiaPASEFLoader) -> None:
        _targeted_exp.targeted_diapasef_data_access()

    @st.cache_resource(show_spinner="Extracting data...")
    def targeted_extraction(_self, _targeted_exp: TargeteddiaPASEFLoader, peptide_coord: Dict, config) -> None:
        _targeted_exp.reduce_targeted_spectra(peptide_coord, config)

    # @st.cache_data(show_spinner="Returning data as dataframe...")  
    def get_targeted_data(_self, _targeted_exp: TargeteddiaPASEFLoader):
        targeted_data = _targeted_exp.get_targeted_dataframe(_self.get_mslevel_list(), _self.transition_list.get_peptide_product_mz_list(_self.transition_settings.selected_peptide, _self.transition_settings.selected_charge), _self.target_transition_list)

        return targeted_data
    
    def load_transition_group(_self, _targeted_exp: TargeteddiaPASEFLoader):
        return _targeted_exp.loadTransitionGroup(_self.target_transition_list)
    