"""
massdash/ui/ExtractedIonChromatogramAnalysisFormUI
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import streamlit as st 

# UI Utils
from .util import clicked, display_input_section
from .widgets.FileInput import FileInput

class ExtractedIonChromatogramAnalysisFormUI:
    """
    Class to create the user interface for the ExtractedIonChromatogramAnalysisForm.
    
    Attributes:
        osw_file_path (streamlit.text_input): A text input field for the OpenSwath file path.
        sqmass_file_path_input (streamlit.text_input): A text input field for the sqMass file path.
        
    Methods:
        create_ui: Creates the user interface for the ExtractedIonChromatogramAnalysisForm.
    """
    def __init__(self) -> None:
        """
        Initializes the ExtractedIonChromatogramAnalysisFormUI class.
        """
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
        
        with st.container(border=True):
            # self.osw_file_path = display_input_section("Input OSW file", "osw_file_path", [("OpenSwath Files", ".osw")], "Select OpenSwath File", "*.osw")
            self.osw_file_path = FileInput("Input OSW file", "osw_file_path", [("OpenSwath Files", ".osw")], "Select OpenSwath File", "*.osw").create_ui()
            self.sqmass_file_path_input = FileInput("Input sqMass file/directory", "sqmass_file_path_input", [("sqMass Files", ".sqMass")], "Select sqMass File", "*.sqMass").create_ui()
                
            # Submit button for form
            begin_button = st.button('Begin Visualization', key='begin_button', help="Begin the visualization.")
            
            if begin_button:
                st.session_state.workflow = "xic_data"
                st.session_state.WELCOME_PAGE_STATE = False
