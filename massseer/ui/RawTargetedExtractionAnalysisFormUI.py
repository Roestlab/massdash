import streamlit as st 

# Internal
from massseer.ui.util import clicked

class RawTargetedExtractionAnalysisFormUI:   
    def __init__(self) -> None:
        """
        Initializes the RawTargetedExtractionAnalysisFormUI class.
        """
        self.transition_list_file_path = None
        self.raw_file_path_input = None
        self.osw_file_path_raw_workflow = None
        self.diann_report_file_path_input = None
        
    def create_ui(self):    
        """
        Creates the user interface for the RawTargetedExtractionAnalysisForm.

        This function displays the UI elements for the form, including input fields for the OSW file path and sqMass file path,
        a button to load an OpenSwath example, and a submit button to begin the visualization.

        Returns:
            None
        """
        st.write("This workflow is designed for raw mass spectrometry data. For example .mzML files generated from a DIA experiment.")

        st.title("Raw Targeted Data Extraction")

        load_toy_dataset = st.button('Load Raw Targeted Data Extraction Example', on_click=clicked , args=['load_toy_dataset_raw_data'], key='load_toy_dataset_raw_data', help="Loads the raw targeted data extraction example dataset.")
        
        if load_toy_dataset:
            st.session_state.workflow = "raw_data"
            st.session_state.WELCOME_PAGE_STATE = False
        
        # Create form for inputting file paths and submit button
        with st.form(key = "raw_data_form"):
            
            st.subheader("Input Transition List")
            self.transition_list_file_path = st.text_input("Enter file path", value=None, placeholder="*.pqp / *.tsv", key='raw_data_transition_list_tmp', help="Path to the transition list file (*.pqp / *.tsv)")

            st.subheader("Input Raw file")
            self.raw_file_path_input = st.text_input("Enter file path", value=None, placeholder="*.mzML", key='raw_data_file_path_tmp', help="Path to the raw file (*.mzML)")

            # Tabs for different data workflows
            st.subheader("Input Search Results (Optional)")
            raw_data_osw, raw_data_diann = st.tabs(["OpenSwath", "DIA-NN"])
            with raw_data_osw:
                self.osw_file_path_raw_workflow = st.text_input("Enter file path of the PyProphet scored OSW file", value=None, placeholder="*.osw", key='raw_data_osw_file_pat_tmp', help="Path to the PyProphet scored OSW file (*.osw)")

            with raw_data_diann:
                self.diann_report_file_path_input = st.text_input("Enter file path of DIA-NNs report file", value=None, placeholder="*.tsv", key='diann_report_file_path_tmp', help="Path to the DIA-NN report file (*.tsv)")
                
            # Submit button for form
            begin_button = st.form_submit_button('Begin Targeted Extraction')
            
            if begin_button:
                st.session_state.workflow = "raw_data"
                st.session_state.WELCOME_PAGE_STATE = False