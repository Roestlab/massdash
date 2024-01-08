"""
massdash/ui/MassDashGUI
~~~~~~~~~~~~~~~~~~~~~~~
"""

import streamlit as st

# UI
from .FileInputXICDataUISettings import FileInputXICDataUISettings
from .FileInputRawDataUISettings import FileInputRawDataUISettings
from .FileInputSearchResultsAnalysisUISettings import FileInputSearchResultsAnalysisUISettings
from .ExtractedIonChromatogramAnalysisFormUI import ExtractedIonChromatogramAnalysisFormUI
from .RawTargetedExtractionAnalysisFormUI import RawTargetedExtractionAnalysisFormUI
from .SearchResultsAnalysisFormUI import SearchResultsAnalysisFormUI
# Utils
from ..util import copy_attributes

class MassDashGUI:
    """
    Class to create the user interface for 
    
    Attributes:
        welcome_container (streamlit.container): A container for the welcome message.
        file_input_settings (FileInputXICDataUISettings/FileInputRawDataUISettings): A container for the file input settings.
        
    Methods:
        show_welcome_message: Displays a welcome message and input fields for OpenSwath and DIA-NN workflows.
        show_file_input_settings: Displays the file input settings.
    """
    def __init__(self, verbose, perf, perf_output="MassDash_Performance_Report.txt"):
        """
        Initializes the MassDashGUI class.

        Args:
            verbose (bool): Enables verbose mode.
            perf (bool): Enables performance mode.
            perf_output (str): The path to the performance output file.

        Returns:
            None
        """
        self.welcome_container = st.empty()
        self.file_input_settings = None
        self.verbose = verbose
        self.perf = perf
        self.perf_output = perf_output
        
        # initialize load_toy_dataset key in clicked session state
        # This is needed because streamlit buttons return True when clicked and then default back to False.
        # See: https://discuss.streamlit.io/t/how-to-make-st-button-content-stick-persist-in-its-own-section/45694/2
        if 'clicked' not in st.session_state:
            st.session_state.clicked  = {'load_toy_dataset_xic_data':False, 'load_toy_dataset_raw_data':False, 'load_toy_dataset_search_results_analysis':False}
            
        if 'workflow' not in st.session_state:
            st.session_state.workflow = None
            
    def show_welcome_message(self):
        """
        Displays a welcome message and input fields for OpenSwath and DIA-NN workflows.

        Returns:
        welcome_container (streamlit.container): A container for the welcome message.
        load_toy_dataset (streamlit.button): A button to load the OpenSwath example dataset.
        osw_file_path (streamlit.text_input): A text input field for the OpenSwath file path.
        sqmass_file_path_input (streamlit.text_input): A text input field for the sqMass file path.
        """
        # Add a welcome message
        # welcome_container = st.empty()FileInputXICDataUISettings
        if st.session_state.WELCOME_PAGE_STATE:
            with self.welcome_container:
                with st.container():
                    st.title("Welcome to MassDash!")
                    st.write("MassDash is a powerful platform designed for researchers and analysts in the field of mass spectrometry.")
                    st.write("It enables the visualization of chromatograms, algorithm testing, and parameter optimization, crucial for data analysis and experimental design.")
                    st.write("This tool is an indispensable asset for researchers and laboratories working with DIA (Data-Independent Acquisition) data.")

                    # Tabs for different data workflows
                    tab1, tab2, tab3 = st.tabs(["Extracted Ion Chromatograms", "Raw Mass Spectrometry Data", "Search Results Analysis"])

                    with tab1:
                        xic_form = ExtractedIonChromatogramAnalysisFormUI()
                        xic_form.create_ui()
                        copy_attributes(xic_form, self)
                        
                    with tab2:
                        raw_data_form = RawTargetedExtractionAnalysisFormUI()
                        raw_data_form.create_ui()
                        copy_attributes(raw_data_form, self)
                        
                    with tab3:
                        search_results_form = SearchResultsAnalysisFormUI()
                        search_results_form.create_ui()
                        copy_attributes(search_results_form, self)

        return self

    def show_file_input_settings(self, feature_file_path=None, xic_file_path=None, transition_list_file_path=None, feature_file_type=None, feature_file_entries_dict: dict=None):
        """
        Displays the file input settings.

        Args:
            feature_file_path (str): The path to the feature file.
            xic_file_path (str): The path to the XIC file.

        Returns:
            None
        """
        if st.session_state.workflow == "xic_data":
            self.file_input_settings = FileInputXICDataUISettings()
            self.file_input_settings.create_ui(feature_file_path, xic_file_path)
            self.file_input_settings.get_sqmass_files()
        elif st.session_state.workflow == "raw_data":
            self.file_input_settings = FileInputRawDataUISettings()
            self.file_input_settings.create_ui(transition_list_file_path, xic_file_path, feature_file_path, feature_file_type)
            self.file_input_settings.get_mzml_files()
        elif st.session_state.workflow == "search_results_analysis":
            self.file_input_settings = FileInputSearchResultsAnalysisUISettings()
            self.file_input_settings.create_ui(feature_file_entries_dict)
        st.sidebar.divider()