import streamlit as st

import os
import fnmatch

from massseer.ui.BaseUISettings import BaseUISettings

class FileInputRawDataUISettings(BaseUISettings):
    def __init__(self) -> None:
        """
        Initializes the FileInputRawDataUISettings class.
        """
        self.transition_list_file_path = None
        self.raw_file_path_input = None
        self.feature_file_path = None 
        self.threads = None

    def create_ui(self, transition_list_file_path: str=None, raw_file_path: str=None, feature_file_path: str=None):
        """
        Creates the user interface for inputting file paths.

        Args:
            transition_list_file_path (str, optional): The file path for the transition list file. Defaults to None.
            raw_file_path (str, optional): The file path for the raw file. Defaults to None.
            feature_file_path (str, optional): The file path for the search results output file. Defaults to None.
        """
        st.sidebar.subheader("Input Transition List")
        self.transition_list_file_path = st.sidebar.text_input("Enter file path", transition_list_file_path, key='raw_data_transition_list', help="Path to the transition list file (*.pqp / *.tsv)")

        st.sidebar.subheader("Input Raw file")
        self.raw_file_path_input = st.sidebar.text_input("Enter file path", raw_file_path, key='raw_data_file_path', help="Path to the raw file (*.mzML)")

        # Tabs for different data workflows
        st.sidebar.subheader("Input Search Results")
        self.feature_file_path = st.sidebar.text_input("Enter file path", feature_file_path, key='feature_file_path', help="Path to the search results output file. Can be an Pyprophet scored OpenSwath file or a DIA-NN report file (*.osw / *.tsv)")

