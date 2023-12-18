import os
import numpy as np
import pandas as pd
import streamlit as st

import timeit
from datetime import timedelta

# UI
from massseer.ui.MassSeerGUI import MassSeerGUI
from massseer.ui.SearchResultsAnalysisUI import SearchResultsAnalysisUI
# Loaders
from massseer.loaders.OSWDataAccess import OSWDataAccess
# Plotting
from massseer.plotting.SearchResultAnalysisPlots import SearchResultAnalysisPlots
# Utils
from massseer.util import conditional_decorator, check_streamlit

class SearchResultsAnalysisServer:
    """
    A class representing the server-side functionality for search results analysis.
    """

    def __init__(self, massseer_gui) -> None:
        """
        Initializes the SearchResultsAnalysisServer object.

        Args:
        massseer_gui : object
            An object representing the MassSeer GUI.
        """
        self.massseer_gui = massseer_gui
        self.file_input_settings = None
        self.analysis_settings = None
        self.analysis = None

    def load_search_result_entries(self, feature_file_entries: dict) -> None:
        """
        Loads the search result entries from the file input settings.

        Args:
        feature_file_entries_dict : dict
            A dictionary containing the search result entries.
        """
        print(feature_file_entries)
        data_access_dict = {}
        for entry, entry_data in feature_file_entries.items():
            if entry_data['search_results_file_type'] == "OpenSwath":
                data_access = OSWDataAccess(entry_data['search_results_file_path'])
                data_access_dict[entry] = data_access   
        return data_access_dict
    
    @conditional_decorator(st.cache_resource, check_streamlit)
    def load_score_distribution_data(_self, _data_access_dict, score_column=None, score_table_context=None):
        """
        Loads the score distribution data from the data access object.

        Args:
        data_access_dict : dict
            A dictionary containing the data access objects.
        score_column : str
            The score column to be loaded.
        """
        score_distributions_dict = {}
        for entry, data_access in _data_access_dict.items():
            score_distributions_dict[entry] = data_access.get_score_distribution(score_table=score_column, context=score_table_context)
        return score_distributions_dict
                


    def main(self) -> None:
        """
        Main function for the search results analysis server.
        """
        # Create a UI for the analysis type
        self.analysis_type = SearchResultsAnalysisUI()
        self.analysis_type.analysis_type()

        search_results_access_dict = self.load_search_result_entries(self.massseer_gui.file_input_settings.feature_file_entries)

        # Create a UI for the analysis
        if self.analysis_type.analysis == "Identifications":
            print("In development, coming soon!")
            pass
        elif self.analysis_type.analysis == "Quantifications":
            print("In development, coming soon!")
            pass
        elif self.analysis_type.analysis == "Score Distributions":
            self.analysis_type.show_score_tables(search_results_access_dict)
            
            if self.analysis_type.selected_score_table in ["SCORE_MS1", "SCORE_MS2", "SCORE_TRANSITION"]:
                score_df = self.load_score_distribution_data(search_results_access_dict, self.analysis_type.selected_score_table)
            elif self.analysis_type.selected_score_table in ["SCORE_PEPTIDE", "SCORE_IPF", "SCORE_PROTEIN", "SCORE_GENE"]:
                self.analysis_type.show_score_table_contexts(search_results_access_dict)
                score_df = self.load_score_distribution_data(search_results_access_dict, self.analysis_type.selected_score_table, self.analysis_type.selected_score_table_context)
            self.analysis_type.show_score_distribution_score_colums(score_df)
            for entry, df in score_df.items():
                
                plotter = SearchResultAnalysisPlots()
                pobj = plotter.plot_score_distributions(df, self.analysis_type.selected_score_col)
                st.bokeh_chart(pobj, use_container_width=True)
                
                st.dataframe(df)
