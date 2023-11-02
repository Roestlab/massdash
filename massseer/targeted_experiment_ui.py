import streamlit as st

# UI imports
from massseer.file_handling_ui import TransitionListUI

# Server side imports
from massseer.transition_list import TransitionList
from massseer.targeted_data_extraction import TargeteddiaPASEFExperiment

class TargetedExperimentUI(TransitionListUI):
    def __init__(self, transition_list: TransitionList) -> None:
        super().__init__()
        self.transition_list = transition_list

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
        self.transition_settings.show_charge_selection(self.transition_list.get_unique_charge_states_per_peptide(self.transition_settings.selected_peptide))

    def show_extraction_parameters(self) -> None:
        st.sidebar.subheader("Extraction parameters")
        # UI for two column checkbox to include MS1 and/or MS2
        col1, col2 = st.sidebar.columns(2)
        with col1:
            self.include_ms1 = st.checkbox("Include MS1", value=True)
        with col2:
            self.include_ms2 = st.checkbox("Include MS2", value=True)
        # Advanced UI paramaters
        with st.sidebar.expander("Advanced parameters", expanded=False):
            # UI for MS1 MZ tolerance in ppm
            self.ms1_mz_tolerance = st.number_input("MS1 m/z tolerance (ppm)", value=20)
            # UI for MS2 MZ tolerance in ppm
            self.ms2_mz_tolerance = st.number_input("MS2 m/z tolerance (ppm)", value=20)
            # UI for RT extraction window in seconds
            self.rt_window = st.number_input("RT window (seconds)", value=600)
            # UI for IM extraction window in 1/K0
            self.im_window = st.number_input("IM window (1/K0)", value=0.06)
    
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
        peptide_dict = {}
        peptide_dict[self.transition_settings.selected_peptide + "_" + str(self.transition_settings.selected_charge)] = {
            'peptide': self.transition_settings.selected_peptide, 'precursor_mz': self.transition_list.get_peptide_precursor_mz(self.transition_settings.selected_peptide, self.transition_settings.selected_charge), 
            'charge': self.transition_settings.selected_charge, 
            'rt_apex': self.transition_list.get_peptide_retention_time(self.transition_settings.selected_peptide, self.transition_settings.selected_charge),
            'im_apex': self.transition_list.get_peptide_ion_mobility(self.transition_settings.selected_peptide, self.transition_settings.selected_charge),
            'qvalue': None, 
            'product_mz': self.transition_list.get_peptide_product_mz_list(self.transition_settings.selected_peptide, self.transition_settings.selected_charge),
            'product_charge': self.transition_list.get_peptide_product_charge_list(self.transition_settings.selected_peptide, self.transition_settings.selected_charge),
            'product_annotation': self.transition_list.get_peptide_fragment_annotation_list(self.transition_settings.selected_peptide, self.transition_settings.selected_charge),
            'product_detecting': [], 
            'rt_boundaries': ''}
        return peptide_dict

    # @st.cache_resource(show_spinner="Loading data...")
    def load_targeted_experiment(_self, mzml_file_path: str) -> None:

        print(_self.get_peptide_dict())

        _self.targeted_exp = TargeteddiaPASEFExperiment(mzml_file_path, _self.ms1_mz_tolerance, _self.ms2_mz_tolerance, _self.rt_window, _self.im_window, _self.get_mslevel_list(), "ondisk")
        _self.targeted_exp.load_data()

    def targeted_extraction(self) -> None:
        self.targeted_exp.reduce_spectra(self.get_peptide_dict())
        print(self.targeted_exp.filtered.get_df())