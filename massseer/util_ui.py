import streamlit as st

from massseer.plotting_ui import ChromatogramPlotSettings
from massseer.algo_ui import AlgorithmUISettings

class MassSeerGUI:
    def __init__(self):
        self.welcome_container = st.empty()

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
                self.tab1, self.tab2 = st.tabs(["sqMass Data", "Raw Data"])
                with self.tab1:
                    st.subheader("OpenSwath")

                    self.load_toy_dataset = st.button('Load OpenSwath Example', on_click=self.clicked , args=['load_toy_dataset'])

                    st.title("Input OSW file")
                    self.osw_file_path = st.text_input("Enter file path", "*.osw", key='osw_file_path_tmp')

                    st.title("Input sqMass file")
                    self.sqmass_file_path_input = st.text_input("Enter file path", "*.sqMass", key='sqmass_file_path_input_tmp')

                with self.tab2:
                    st.subheader("Raw Targeted Data Extraction")

                    # /media/justincsing/ExtraDrive1/Documents2/Roest_Lab/Github/MassSeer/tests/test_data/josh/diann/K562-Library-Default_osw_6Frags_diann.tsv
                    # /media/justincsing/ExtraDrive1/Documents2/Roest_Lab/Github/MassSeer/tests/test_data/josh/90min-SP-30cm-2um-K562-100nL-25ng_DIA_Slot1-5_1_550_3-7-2021.mzML
                    # /media/justincsing/ExtraDrive1/Documents2/Roest_Lab/Github/MassSeer/tests/test_data/josh/diann/jsc718.5808924.0/report.tsv
                    # Test protein: O15258
                    # Test peptide: (UniMod:1)SEGDSVGESVHGKPSVVYR
                    # >>> d.loc[(d['Q.Value'] <= 0.000001) & (d['PG.Q.Value'] <= 0.001) & (d['Protein.Ids']=='O15258')][['RT', 'RT.Start', 'RT.Stop', 'iRT']]
                    #             RT   RT.Start    RT.Stop        iRT
                    # 518  51.864735  51.715942  52.043346  41.704933
                    # OSW
                    # Test protein: P28482
                    # Test peptide: .(UniMod:1)AAAAAAGAGPEM(UniMod:35)VR
                    # EXP_RT    EXP_IM    LEFT_WIDTH    RIGHT_WIDTH
                    # 3451.43	1.0257943970575	3445.74365234375	3461.81396484375
                    # SCORE_MS2 QValue: 1.90126796378053e-05
                    # OSW Highets intensity and lowest pvalue
                    # Test protein: P0C0S5
                    # Test peptide: AGLQFPVGR
                    # EXP_RT    EXP_IM    LEFT_WIDTH    RIGHT_WIDTH
                    # 4566.88   0.822054
                    # SCORE_MS2 QValue: 0.000019
                    # APEX Intensity: 791382.719254
                    st.title("Input Transition List")
                    self.transition_list_file_path = st.text_input("Enter file path", "*.pqp / *.tsv", key='raw_data_transition_list')

                    st.title("Input Raw file")
                    self.raw_file_path_input = st.text_input("Enter file path", "*.mzML", key='raw_data_file_path')

                    # Tabs for different data workflows
                    st.title("Input Search Results")
                    self.raw_data_osw, self.raw_data_diann = st.tabs(["OSW", "DIA-NN"])
                    with self.raw_data_osw:
                        st.subheader("OpenSwath")
                        self.osw_file_path = st.text_input("Enter file path", "*.osw", key='raw_data_osw_file_pat')

                    with self.raw_data_diann:
                        st.subheader("DIA-NN")
                        self.diann_report_file_path_input = st.text_input("Enter file path", "*.tsv", key='diann_report_file_path')

        return self

    def show_chromatogram_plot_settings(self, include_raw_data_settings=False):
        self.chromatogram_plot_settings = ChromatogramPlotSettings(self)
        self.chromatogram_plot_settings.create_sidebar(include_raw_data_settings)
        return self

    def show_algorithm_settings(self):
        self.alogrithm_settings = AlgorithmUISettings(self)
        self.alogrithm_settings.create_ui(self.chromatogram_plot_settings)
        return self