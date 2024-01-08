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
        # cols = st.sidebar.columns(spec=[0.7, 0.3])
        # self.feature_file_path = cols[0].text_input("Enter file path", feature_file_path, key='search_results_analysis_osw_file_path', help="Path to the search results file (*.osw / *.tsv)")
        # self.feature_file_type = cols[1].text_input("Type", feature_file_type, key='search_results_analysis_osw_file_type', help="Select the file type of the search results file.")
        file_list_container = st.sidebar.container()
        file_list_container.empty()

        search_results_form = SearchResultsAnalysisFormUI()
        search_results_form.create_forum(st.sidebar, st_type="sidebar", feature_file_entries_dict=feature_file_entries)
        copy_attributes(search_results_form, self)
        
        with file_list_container:
            # self.feature_file_entries = feature_file_entries
            df = pd.DataFrame(self.feature_file_entries).T
            df.rename(columns={'search_results_file_path':'File', 'search_results_exp_name':'Experiment', 'search_results_file_type':'Type'}, inplace=True)
            file_list_container.dataframe(df, hide_index=True)

