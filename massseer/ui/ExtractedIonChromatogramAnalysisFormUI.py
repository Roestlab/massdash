import streamlit as st 

# Internal
from massseer.ui.util import clicked

class ExtractedIonChromatogramAnalysisFormUI:   
    def __init__(self) -> None:
        """
        Initializes the ExtractedIonChromatogramAnalysisFormUI class.
        """
        self.load_toy_dataset = None
        self.osw_file_path = None
        self.sqmass_file_path_input = None
        
    def create_ui(self):    
        """
        Creates the user interface for the ExtractedIonChromatogramAnalysisForm.

        This function displays the UI elements for the form, including input fields for the OSW file path and sqMass file path,
        a button to load an OpenSwath example, and a submit button to begin the visualization.

        Returns:
            None
        """
        st.write("This workflow is designed for post-extracted ion chromatogram data. For example sqMass files generated from an OpenSwathWorkflow experiment.")

        st.title("OpenSwath")

        load_toy_dataset = st.button('Load OpenSwath Example', on_click=clicked , args=['load_toy_dataset_xic_data'], key =  'load_toy_dataset_xic_data', help="Loads the OpenSwath example dataset.")
        
        if load_toy_dataset:
            st.session_state.workflow = "xic_data"
            st.session_state.WELCOME_PAGE_STATE = False
        
        # Create form for inputting file paths and submit button
        with st.form(key = "xic_data_form"):
            
            st.subheader("Input OSW file")
            self.osw_file_path = st.text_input("Enter file path",  value=None, placeholder="*.osw", key='osw_file_path_tmp', help="Path to the OpenSwathWorkflow output file (*.osw)")

            st.subheader("Input sqMass file/directory")
            self.sqmass_file_path_input = st.text_input("Enter file path", value=None, placeholder="*.sqMass", key='sqmass_file_path_input_tmp', help="Path to the sqMass file (*.sqMass) or path to a directory containing sqMass files.")
                
            # Submit button for form
            begin_button = st.form_submit_button('Begin Visualization')
            
            if begin_button:
                st.session_state.workflow = "xic_data"
                st.session_state.WELCOME_PAGE_STATE = False