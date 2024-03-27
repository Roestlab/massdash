"""
massdash/server/SearchResultsAnalysisServer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import os
import numpy as np
import pandas as pd
import streamlit as st
from io import BytesIO # https://discuss.streamlit.io/t/cannot-change-matplotlib-figure-size/10295/6

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
    
    #TODO caching this is not working
    #@conditional_decorator(st.cache_resource, check_streamlit)
    def plot_score_distribution(_self, _resultsLoader: ResultsLoader) -> None:
        """
        Plots the score distribution.

        Args:
        plotter : object
            An object representing the plotter.
        resultsLoader : object
            An object representing the results loader.
        """
        config = SearchResultAnalysisPlotConfig()
        config.update(dict(aggregate=_self.analysis_type.aggregate_runs))
        plotter = SearchResultAnalysisPlotter(config=config)
        if _self.analysis_type.selected_analyte == "Protein":
            return plotter.plotProteinDistribution(_resultsLoader)
        elif _self.analysis_type.selected_analyte == "Peptide":
            return plotter.plotPeptideDistribution(_resultsLoader)
        else: # _self.analysis_type.selected_analyte == "Peptide Precursor"
            if _self.analysis_type.show_more_scores:
                return plotter.plotScoreDistribution(_resultsLoader, 
                                                      _self.analysis_type.selected_score_table, 
                                                      _self.analysis_type.selected_score)
            else:
                return plotter.plotPrecursorDistribution(_resultsLoader)
  
    def main(self) -> None:
        """
        Main function for the search results analysis server.
        """
        # Create a UI for the analysis type
        self.analysis_type = SearchResultsAnalysisUI()
        self.analysis_type.analysis_type()
        self.analysis_type.show_aggregation()

        # self.load_search_result_entries.clear()
        # TODO clean up GUI less information needed then what is provided
        files_to_load = pd.DataFrame(self.massdash_gui.file_input_settings.feature_file_entries).T['search_results_file_path'].values
        resultsLoader = self.load_results(files_to_load)

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
                fig = self.plot_upset(plotter, resultsLoader) 
                buf = BytesIO()
                fig.savefig(buf, format="png")
                plot_dict['upset_diagram'] = buf
            
            self.analysis_type.show_plots(plot_container, plot_dict, num_cols=self.analysis_type.num_cols)
            
        else: # self.analysis_type.analysis == "Score Distributions"
            search_results_plots_container = st.container()
            search_results_plots_container.empty()

            self.analysis_type.show_score_tables(resultsLoader)
            plot = self.plot_score_distribution(resultsLoader) 

            st.bokeh_chart(plot, use_container_width=True)
           