import streamlit as st

from massseer.ui.FileInputUISettings import FileInputUISettings

class MassSeerGUI:
    def __init__(self):
        """
        Initializes the MassSeerGUI class.

        Args:
            None

        Returns:
            None
        """
        self.welcome_container = st.empty()
        self.tab1 = None
        self.tab2 = None
        self.workflow = None
        self.load_toy_dataset = None
        self.osw_file_path = None
        self.sqmass_file_path_input = None
        self.file_input_settings = None
        self.chromatogram_plot_settings = None
        self.peak_picking_settings = None
        self.concensus_chromatogram_settings = None
        self.transition_list_file_path = None
        self.raw_file_path_input = None
        self.diann_report_file_path_input = None
        self.raw_data_osw = None
        self.raw_data_diann = None
        self.begin_button = None
        
        # initialize load_toy_dataset key in clicked session state
        # This is needed because streamlit buttons return True when clicked and then default back to False.
        # See: https://discuss.streamlit.io/t/how-to-make-st-button-content-stick-persist-in-its-own-section/45694/2
        if 'clicked' not in st.session_state:
            st.session_state.clicked  = {'load_toy_dataset':False}


    def clicked(self, button):
        """
        Updates the session state to indicate that a button has been clicked.

        Args:
            button (str): The name of the button that was clicked.

        Returns:
            None
        """
        st.session_state.clicked[button] = True

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
        # welcome_container = st.empty()
        with self.welcome_container:
            with st.container():
                st.title("Welcome to MassSeer!")
                st.write("MassSeer is a powerful platform designed for researchers and analysts in the field of mass spectrometry.")
                st.write("It enables the visualization of chromatograms, algorithm testing, and parameter optimization, crucial for data analysis and experimental design.")
                st.write("This tool is an indispensable asset for researchers and laboratories working with DIA (Data-Independent Acquisition) data.")

                # Tabs for different data workflows
                self.tab1, self.tab2 = st.tabs(["Extracted Ion Chromatograms", "Raw Mass Spectrometry Data"])

                with self.tab1:

                    st.write("This workflow is designed for post-extracted ion chromatogram data. For example sqMass files generated from an OpenSwathWorkflow experiment.")

                    st.title("OpenSwath")

                    self.load_toy_dataset = st.button('Load OpenSwath Example', on_click=self.clicked , args=['load_toy_dataset'])

                    st.subheader("Input OSW file")
                    self.osw_file_path = st.text_input("Enter file path", "*.osw", key='osw_file_path_tmp')

                    st.subheader("Input sqMass file")
                    self.sqmass_file_path_input = st.text_input("Enter file path", "*.sqMass", key='sqmass_file_path_input_tmp')
                    
                    if self.load_toy_dataset:
                        self.workflow = "xic_data"
                    elif self.osw_file_path is not None and self.sqmass_file_path_input is not None:
                        self.workflow = "xic_data"
                    
                with self.tab2:
                    
                    st.write("This workflow is designed for raw mass spectrometry data. For example .mzML files generated from a DIA experiment.")

                    st.title("Raw Targeted Data Extraction")

                    self.load_toy_dataset = st.button('Load Raw Targeted Data Extraction Example', on_click=self.clicked , args=['load_toy_dataset'])
                    
                    if self.load_toy_dataset:
                        self.workflow = "raw_data"

                    st.subheader("Input Transition List")
                    self.transition_list_file_path = st.text_input("Enter file path", "*.pqp / *.tsv", key='raw_data_transition_list')

                    st.subheader("Input Raw file")
                    self.raw_file_path_input = st.text_input("Enter file path", "*.mzML", key='raw_data_file_path')

                    # Tabs for different data workflows
                    st.subheader("Input Search Results (Optional)")
                    self.raw_data_osw, self.raw_data_diann = st.tabs(["OpenSwath", "DIA-NN"])
                    with self.raw_data_osw:
                        self.osw_file_path = st.text_input("Enter file path of the PyProphet scored OSW file", "*.osw", key='raw_data_osw_file_pat')

                    with self.raw_data_diann:
                        st.subheader("DIA-NN")
                        self.diann_report_file_path_input = st.text_input("Enter file path of DIA-NNs report file", "*.tsv", key='diann_report_file_path')
                        
                    self.begin_button = st.button('Begin', on_click=self.clicked , args=['begin'])
                    
                    if self.begin_button:
                        self.workflow = "raw_data"

        return self

    def show_file_input_settings(self, feature_file_path=None, xic_file_path=None, transition_list_file_path=None):
        """
        Displays the file input settings.

        Args:
            feature_file_path (str): The path to the feature file.
            xic_file_path (str): The path to the XIC file.

        Returns:
            None
        """
        self.file_input_settings = FileInputUISettings(self.workflow)
        if self.workflow == "xic_data":
            self.file_input_settings.create_ui(feature_file_path, xic_file_path)
            self.file_input_settings.get_sqmass_files()
        elif self.workflow == "raw_data":
            self.file_input_settings.create_ui(transition_list_file_path, xic_file_path, feature_file_path)
        st.sidebar.divider()