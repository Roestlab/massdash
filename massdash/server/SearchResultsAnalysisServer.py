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
from massseer.loaders.access.OSWDataAccess import OSWDataAccess
# from massseer.loaders.DiaNNLoader import DiaNNLoader
# from massseer.loaders.DreamDIALoader import DreamDIALoader
from massseer.loaders.access.ResultsTSVDataAccess import ResultsTSVDataAccess
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

    @conditional_decorator(st.cache_resource, check_streamlit)
    def load_search_result_entries(_self, _feature_file_entries: dict) -> None:
        """
        Loads the search result entries from the file input settings.

        Args:
        feature_file_entries_dict : dict
            A dictionary containing the search result entries.
        """
        data_access_dict = {}
        for entry, entry_data in _feature_file_entries.items():
            print(f"Loading search results from {entry_data['search_results_file_path']}")
            if entry_data['search_results_file_type'] == "OpenSWATH":
                data_access = OSWDataAccess(entry_data['search_results_file_path'], mode='gui')
                data_access_dict[entry_data['search_results_exp_name']] = data_access   
            elif entry_data['search_results_file_type'] == "DIA-NN":
                data_access = ResultsTSVDataAccess(entry_data['search_results_file_path'], entry_data['search_results_file_type'])
                data_access_dict[entry_data['search_results_exp_name']] = data_access
            elif entry_data['search_results_file_type'] == "DreamDIA":
                data_access = ResultsTSVDataAccess(entry_data['search_results_file_path'], entry_data['search_results_file_type'])
                data_access_dict[entry_data['search_results_exp_name']] = data_access
            else:
                raise ValueError(f"Search results file type {entry_data['search_results_file_type']} not supported.")
        return data_access_dict
    
    @conditional_decorator(st.cache_resource, check_streamlit)
    def get_data(_self, _data_access_dict, biological_level, qvalue_threshold):
        data_dict = {}
        for entry, data_access in _data_access_dict.items():
            if isinstance(data_access, OSWDataAccess):
                data_dict[entry] = data_access.df[ data_access.df['Qvalue'] < qvalue_threshold ]
                # Add entry name to dataframe   
                data_dict[entry]['entry'] = entry
            if isinstance(data_access, ResultsTSVDataAccess):
                data_dict[entry] = data_access.df[ data_access.df['Qvalue'] < qvalue_threshold ]
                # Add entry name to dataframe   
                data_dict[entry]['entry'] = entry
            
        return data_dict
    
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
            print(f"Getting score distribution for {entry}")
            score_distributions_dict[entry] = data_access.get_score_distribution(score_table=score_column, context=score_table_context)
        return score_distributions_dict
                


    def main(self) -> None:
        """
        Main function for the search results analysis server.
        """
        # Create a UI for the analysis type
        self.analysis_type = SearchResultsAnalysisUI()
        self.analysis_type.analysis_type()

        # self.load_search_result_entries.clear()
        search_results_access_dict = self.load_search_result_entries(self.massseer_gui.file_input_settings.feature_file_entries)

        # Create a UI for the analysis
        if self.analysis_type.analysis == "Results":
            
            self.analysis_type.show_identification_settings()
            # self.get_data.clear()
            ident_data_dict = self.get_data(search_results_access_dict, self.analysis_type.biological_level, self.analysis_type.qvalue_threshold)

            plot_container = st.container()

            # get overlapping columnn names
            overlapping_columns = set.intersection(*[set(df.columns) for df in ident_data_dict.values()])
            # st.write(f"overlapping_columns: {overlapping_columns}")
            ident_data = pd.concat([df[overlapping_columns] for df in ident_data_dict.values()], axis=0)
            # st.write(ident_data)
            
            search_results_plots_container = st.container()
            search_results_plots_container.empty()
            
            plot_dict = {}
            
            plotter = SearchResultAnalysisPlots()
            if "Identification" in self.analysis_type.plot_types:
                pobj = plotter.plot_identifications(ident_data, self.analysis_type.aggregate_identifications)
                plot_dict['identifications'] = pobj

            if "Quantification" in self.analysis_type.plot_types:
                pobj2 = plotter.plot_quantifications(ident_data)
                plot_dict['quantifications'] = pobj2
            
            if "CV" in self.analysis_type.plot_types: 
                pboj3 = plotter.plot_coefficient_of_variation(ident_data)
                plot_dict['coefficient_of_variation'] = pboj3
            
            if "UpSet" in self.analysis_type.plot_types:
                pobj4 = plotter.plot_upset_diagram(ident_data)
                plot_dict['upset_diagram'] = pobj4
            
            self.analysis_type.show_plots(plot_container, plot_dict, num_cols=self.analysis_type.num_cols)
            
        elif self.analysis_type.analysis == "Score Distributions":
            self.analysis_type.show_score_tables(search_results_access_dict)
            
            if self.analysis_type.selected_score_table in ["SCORE_MS1", "SCORE_MS2", "SCORE_TRANSITION"]:
                score_df = self.load_score_distribution_data(search_results_access_dict, self.analysis_type.selected_score_table)
            elif self.analysis_type.selected_score_table in ["SCORE_PEPTIDE", "SCORE_IPF", "SCORE_PROTEIN", "SCORE_GENE"]:
                self.analysis_type.show_score_table_contexts(search_results_access_dict)
                score_df = self.load_score_distribution_data(search_results_access_dict, self.analysis_type.selected_score_table, self.analysis_type.selected_score_table_context)
            self.analysis_type.show_score_distribution_score_colums(score_df)
            
            search_results_plots_container = st.container()
            search_results_plots_container.empty()
            
            search_results_tabs = st.tabs([entry for entry in score_df.keys()])
            
            counter =  0
            for entry, df in score_df.items():
                plotter = SearchResultAnalysisPlots()
                pobj = plotter.plot_score_distributions(df, self.analysis_type.selected_score_col)
                with search_results_plots_container:
                    st.bokeh_chart(pobj, use_container_width=True)
                with search_results_tabs[counter]:
                    st.dataframe(df)
                    counter += 1

