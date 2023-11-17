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
        self.load_toy_dataset = None
        self.osw_file_path = None
        self.sqmass_file_path_input = None
        self.file_input_settings = None
        self.chromatogram_plot_settings = None
        self.peak_picking_settings = None
        self.concensus_chromatogram_settings = None


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

                    st.subheader("OpenSwath")

                    self.load_toy_dataset = st.button('Load OpenSwath Example', on_click=self.clicked , args=['load_toy_dataset'])

                    st.title("Input OSW file")
                    self.osw_file_path = st.text_input("Enter file path", "*.osw", key='osw_file_path_tmp')

                    st.title("Input sqMass file")
                    self.sqmass_file_path_input = st.text_input("Enter file path", "*.sqMass", key='sqmass_file_path_input_tmp')

        return self

    def show_file_input_settings(self, feature_file_path=None, xic_file_path=None):
        """
        Displays the file input settings.

        Args:
            feature_file_path (str): The path to the feature file.
            xic_file_path (str): The path to the XIC file.

        Returns:
            None
        """
        self.file_input_settings = FileInputUISettings(self)
        self.file_input_settings.create_ui(feature_file_path, xic_file_path)
        self.file_input_settings.get_sqmass_files()
        st.sidebar.divider()