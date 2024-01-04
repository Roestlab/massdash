import streamlit as st 

# Internal
from massseer.ui.util import clicked

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
            st.subheader("Input Search Results")

            cols = st.columns([0.7, 0.3])
            self.feature_file_path = cols[0].text_input("Enter file path of the feature file", value=None, placeholder="*.osw / *.tsv", key='feature_file_path_tmp', help="Path to the feature file (*.osw / *.tsv) from an OpenSwath or DIA-NN workflow")
            self.feature_file_type = cols[1].selectbox("Select file type", options=["OpenSWATH", "DIA-NN"], key='feature_file_type_tmp', help="Select the file type of the feature file")
                
            # Submit button for form
            begin_button = st.form_submit_button('Begin Targeted Extraction')
            
            if begin_button:
                st.session_state.workflow = "raw_data"
                st.session_state.WELCOME_PAGE_STATE = False