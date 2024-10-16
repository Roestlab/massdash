"""
massdash/ui/RawTargetedExtractionAnalysisFormUI
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import streamlit as st 

# UI
from .util import clicked, display_input_section

class RawTargetedExtractionAnalysisFormUI:   
    """
    Class to create the user interface for the RawTargetedExtractionAnalysisForm.
    
    Attributes:
        transition_list_file_path (streamlit.text_input): A text input field for the transition list file path.
        raw_file_path_input (streamlit.text_input): A text input field for the raw file path.
        osw_file_path_raw_workflow (streamlit.text_input): A text input field for the PyProphet scored OSW file path.
        diann_report_file_path_input (streamlit.text_input): A text input field for the DIA-NN report file path.
        
    Methods:
        create_ui: Creates the user interface for the RawTargetedExtractionAnalysisForm.
    """
    def __init__(self) -> None:
        """
        Initializes the RawTargetedExtractionAnalysisFormUI class.
        """
        self.transition_list_file_path = None
        self.raw_file_path_input = None
        self.feature_file_path = None
        self.feature_file_type = None
        
    def create_ui(self, isStreamlitCloud: bool = False):    
        """
        Creates the user interface for the RawTargetedExtractionAnalysisForm.

        This function displays the UI elements for the form, including input fields for the OSW file path and sqMass file path,
        a button to load an OpenSwath example, and a submit button to begin the visualization.

        Returns:
            None
        """
        st.title("Raw Targeted Data Extraction")
        st.write("This workflow is designed for raw mass spectrometry data. For example `.mzML` files generated from a DIA experiment.")

        col1, col2, col3 = st.columns([0.2, 0.2, 0.6])
        load_toy_dataset = col1.button('Load Raw Targeted Data Extraction Example', on_click=clicked , args=['load_toy_dataset_raw_data'], key='load_toy_dataset_raw_data', help="Loads the raw targeted data extraction example dataset.")
        load_toy_dataset_im = col2.button('Load Raw IM Targeted Data Extraction Example', on_click=clicked , args=['load_toy_dataset_raw_data_im'], key='load_toy_dataset_raw_data_im', help="Loads the raw targeted data with IM extraction example dataset.")
        
        if load_toy_dataset:
            st.session_state.workflow = "raw_data"
            st.session_state.WELCOME_PAGE_STATE = False
        if load_toy_dataset_im:
            st.session_state.workflow = "raw_data"
            st.session_state.WELCOME_PAGE_STATE = False
        
        # Do not add the file input section if running on streamlit cloud
        if not isStreamlitCloud:
            # Create form for inputting file paths and submit button
            with st.container(border=True):
                self.transition_list_file_path = display_input_section("Input Transition List", "transition_list_file_path", [("Transition List Files", ".pqp"), ("Transition List Files", ".tsv")], "Select Transition List File", "*.pqp")
                self.raw_file_path_input = display_input_section("Input Raw file", "raw_file_path_input", [("Raw MS Files", ".mzML")], "Select Raw MS Data File", "*.mzML")

                cols = st.columns([0.05, 0.65, 0.3], gap="small")

                # Submit button for form
                begin_button = st.button('Begin Targeted Extraction')
                
                if begin_button:
                    st.session_state.workflow = "raw_data"
                st.session_state.WELCOME_PAGE_STATE = False