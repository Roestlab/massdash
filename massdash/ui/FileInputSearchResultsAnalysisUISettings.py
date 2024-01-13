import streamlit as st
import pandas as pd

# UI
from .SearchResultsAnalysisFormUI import SearchResultsAnalysisFormUI
# Util
from ..util import copy_attributes

class FileInputSearchResultsAnalysisUISettings:
    """
    Class to create the user interface for the 
    """
    def __init__(self) -> None:
        """
        Initializes the 
        """
        self.feature_file_entries = {}
        self.feature_file_path = None
        self.feature_file_type = None

    def create_ui(self, feature_file_entries: dict):
        """
        Creates the user interface for inputting file paths.

        Args:
            feature_file_path (str): Path to the feature file (*.osw / *.tsv)
            feature_file_type (str): File type of the feature file (OpenSwath / DIA-NN)
        """
        st.sidebar.subheader("Input Search Results")

        file_list_container = st.sidebar.container()
        file_list_container.empty()
        self.feature_file_entries = feature_file_entries
        
        with file_list_container:
            # self.feature_file_entries = feature_file_entries
            df = pd.DataFrame(feature_file_entries).T
            df.rename(columns={'search_results_file_path':'File', 'search_results_exp_name':'Experiment', 'search_results_file_type':'Type'}, inplace=True)
            file_list_container.dataframe(df, hide_index=True)

