"""
massdash/server/SearchResultsAnalysisServer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import os
import numpy as np
import pandas as pd
import streamlit as st

import timeit
from datetime import timedelta

# UI
from ..ui.SearchResultsAnalysisUI import SearchResultsAnalysisUI
# Loaders
from ..loaders import ResultsLoader
# Plotting
from ..plotting.SearchResultAnalysisPlotter import SearchResultAnalysisPlotter, SearchResultAnalysisPlotConfig
# Utils
from ..util import conditional_decorator, check_streamlit

class SearchResultsAnalysisServer:
    """
    A class representing the server-side functionality for search results analysis.
    """

    def __init__(self, massdash_gui) -> None:
        """
        Initializes the SearchResultsAnalysisServer object.

        Args:
        massdash_gui : object
            An object representing the MassDash GUI.
        """
        self.massdash_gui = massdash_gui
        self.file_input_settings = None
        self.analysis_settings = None
        self.analysis = None

    @conditional_decorator(st.cache_resource, check_streamlit)
    def load_results(_self, _feature_file_entries: dict) -> None:
        """
        Loads the search result entries from the file input settings.

        Args:
        feature_file_entries_dict : dict
            A dictionary containing the search result entries.
        """
        return ResultsLoader(rsltsFile=_feature_file_entries)
    
    @conditional_decorator(st.cache_resource, check_streamlit)
    def plot_identifications(_self, _plotter, _resultsLoader: ResultsLoader) -> None:
        """
        Plots the identifications.

        Args:
        plotter : object
            An object representing the plotter.
        resultsLoader : object
            An object representing the results loader.
        """
        return _plotter.plotIdentifications(_resultsLoader)
    
    @conditional_decorator(st.cache_resource, check_streamlit)
    def plot_quantifications(_self, _plotter, _resultsLoader: ResultsLoader) -> None:
        """
        Plots the quantifications.

        Args:
        plotter : object
            An object representing the plotter.
        resultsLoader : object
            An object representing the results loader.
        """
        return _plotter.plotQuantifications(_resultsLoader)
    
    @conditional_decorator(st.cache_resource, check_streamlit)
    def plot_cv(_self, _plotter, _resultsLoader: ResultsLoader) -> None:
        """
        Plots the coefficient of variation.

        Args:
        plotter : object
            An object representing the plotter.
        resultsLoader : object
            An object representing the results loader.
        """
        return _plotter.plotCV(_resultsLoader)
    
    @conditional_decorator(st.cache_resource, check_streamlit)
    def plot_upset(_self, _plotter, _resultsLoader: ResultsLoader) -> None:
        """
        Plots the UpSet diagram.

        Args:
        plotter : object
            An object representing the plotter.
        resultsLoader : object
            An object representing the results loader.
        """
        return _plotter.plotUpset(_resultsLoader)
    
    @conditional_decorator(st.cache_resource, check_streamlit)
    def plot_score_distribution(_self, _plotter, _resultsLoader: ResultsLoader) -> None:
        """
        Plots the score distribution.

        Args:
        plotter : object
            An object representing the plotter.
        resultsLoader : object
            An object representing the results loader.
        """
        return _plotter.plotScoreDistribution(_resultsLoader, _self.analysis_settings.selected_score_table, _self.analysis_settings.selected_score_col, _self.analysis_settings.selected_score_table_context)
  
    def main(self) -> None:
        """
        Main function for the search results analysis server.
        """
        # Create a UI for the analysis type
        self.analysis_type = SearchResultsAnalysisUI()
        self.analysis_type.analysis_type()

        # self.load_search_result_entries.clear()
        resultsLoader = self.load_results(self.massdash_gui.file_input_settings.feature_file_entries)

        # Create a UI for the analysis
        if self.analysis_type.analysis == "Results":
            self.analysis_type.show_identification_settings()
            plot_dict = {}
            plot_container = st.container()
            search_results_plots_container = st.container()
            search_results_plots_container.empty()

            config = SearchResultAnalysisPlotConfig()
            config.update(dict(aggregate=self.analysis_type.aggregate_identifications))
            plotter = SearchResultAnalysisPlotter()
            if "Identification" in self.analysis_type.plot_types:
                plot_dict['identifications'] = self.plot_identifications(plotter, resultsLoader)

            if "Quantification" in self.analysis_type.plot_types:
                plot_dict['quantifications'] = self.plot_quantifications(plotter, resultsLoader) 
            
            if "CV" in self.analysis_type.plot_types: 
                plot_dict['coefficient_of_variation'] = self.plot_cv(plotter, resultsLoader)
            
            if "UpSet" in self.analysis_type.plot_types:
                plot_dict['upset_diagram'] = self.plot_upset(plotter, resultsLoader) 
            
            self.analysis_type.show_plots(plot_container, plot_dict, num_cols=self.analysis_type.num_cols)
            
        else: # self.analysis_type.analysis == "Score Distributions"
            search_results_plots_container = st.container()
            search_results_plots_container.empty()

            config = SearchResultAnalysisPlotConfig()

            plotter = SearchResultAnalysisPlotter()

            plot = self.plot_score_distribution( plotter, resultsLoader) 

            st.bokeh_chart(plot, use_container_width=True)
           