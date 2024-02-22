"""
massdash/server/FeatureMapPlotterServer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

from typing import Dict
from os.path import basename
from bokeh.layouts import gridplot
from collections import defaultdict
import streamlit as st

# Loaders
from ..loaders.GenericChromatogramLoader import GenericChromatogramLoader
# Plotting
from ..plotting import PlotConfig, InteractivePlotter, InteractiveThreeDimensionPlotter, InteractiveTwoDimensionPlotter
# Server
from .PeakPickingServer import PeakPickingServer
# Structs
from ..structs import FeatureMapCollection, TransitionGroupCollection, TransitionGroupFeatureCollection
# UI
from ..ui.TransitionListUISettings import TransitionListUISettings
from ..ui.ChromatogramPlotUISettings import ChromatogramPlotUISettings
from ..ui.PeakPickingUISettings import PeakPickingUISettings

class FeatureMapPlotterServer:
    """
    A class that generates plots from FeatureMaps

    Args:
        feature_map_dict (dict): A dictionary containing transition groups.
        transition_list_ui (TransitionListUISettings): An object representing the transition list UI.
        chrom_plot_settings (ChromatogramPlotUISettings): An object representing the chromatogram plot settings.

    Attributes:
        feature_map_dict (dict): A dictionary containing transition groups.
        transition_list_ui (object): An object representing the transition list UI.
        chrom_plot_settings (ChromatogramPlotUISettings): An object representing the chromatogram plot settings.
        plot_obj_dict (dict): A dictionary containing the generated plot objects.

    Methods:
        generate_chromatogram_plots: Generates chromatogram plots for each file in the transition group dictionary.
        _get_plot_settings: Returns the plot settings dictionary for a given plot type.
        _generate_plot: Generates a plot object for a given transition group and plot settings.

    """

    def __init__(self, 
                 featureMapCollection: FeatureMapCollection,
                 chrom_loader: GenericChromatogramLoader,
                 transition_list_ui: TransitionListUISettings, 
                 chrom_plot_settings: ChromatogramPlotUISettings, 
                 peak_picking_settings: PeakPickingUISettings, 
                 verbose: bool=False):
        self.featureMapCollection = featureMapCollection
        self.chrom_loader = chrom_loader
        self.transition_list_ui = transition_list_ui
        self.chrom_plot_settings = chrom_plot_settings
        self.peak_picking_settings = peak_picking_settings
        self.plot_obj_dict = defaultdict(list) # a dictionary of plot objects with the mapping <RunName>:[<PlotObject>] (multiple plots per run allowed)
        self.verbose = verbose


    def generate_plots(self):
        """
        Generates plots based on user settings

        Returns:
            None
        """
        if self.chrom_plot_settings.display_plot_dimension_type == '1D':
            self.generate_one_dimensional_plots()
        elif self.chrom_plot_settings.display_plot_dimension_type == '2D':
            self.generate_two_dimensional_plots()
        elif self.chrom_plot_settings.display_plot_dimension_type == '3D':
            self.generate_three_dimensional_plots()
        else:
            raise ValueError(f"Invalid plot dimension: {self.chrom_plot_settings.plot_dimension}. Valid options are '1D', '2D', and '3D'.")

        return self

    def generate_one_dimensional_plots(self):
        """
        Generates plots for each file in the transition group dictionary.
        """


        if self.chrom_plot_settings.display_spectrum:
            spectra = self.featureMapCollection.to_spectra()
            plot_settings_dict = self._get_plot_settings('m/z', 'Intensity', 'spectra')
            self._generate_plots_helper(spectra, plot_settings_dict)

        if self.chrom_plot_settings.display_chromatogram:
            chromatograms = self.featureMapCollection.to_chromatograms()

            # Perform peak picking or add features 
            if self.peak_picking_settings.do_peak_picking == 'Feature File Boundaries':
                tr_group_feature_data = self.chrom_loader.loadTransitionGroupFeatures(self.transition_list_ui.transition_settings.selected_peptide,
                    self.transition_list_ui.transition_settings.selected_charge)

            elif self.peak_picking_settings.do_peak_picking in ['pyPeakPickerMRM', 'MRMTransitionGroupPicker', 'Conformer']:
                # Perform peak picking if enabled
                peak_picker = PeakPickingServer(self.peak_picking_settings, self.chrom_plot_settings)
                tr_group_feature_data = peak_picker.perform_peak_picking(tr_group_data=chromatograms, 
                                                                            spec_lib=self.chrom_loader.libraryFile)
            elif self.peak_picking_settings.do_peak_picking == 'none':
                tr_group_feature_data = None
                pass

            else:
                raise ValueError(f"Invalid peak picking algorithm: {self.peak_picking_settings.do_peak_picking}. Valid options are 'Feature File Boundaries', 'pyPeakPickerMRM', 'MRMTransitionGroupPicker', and 'Conformer'.")

            plot_settings_dict = self._get_plot_settings('Retention Time (s)', 'Intensity', 'chromatogram')
            self._generate_plots_helper(chromatograms, plot_settings_dict, tr_group_feature_data)
        
        if self.chrom_plot_settings.display_mobilogram:
            mobilograms = self.featureMapCollection.to_mobilograms()
            plot_settings_dict = self._get_plot_settings('Ion Mobility (1/K0)', 'Intensity', 'mobilogram')
            self._generate_plots_helper(mobilograms, plot_settings_dict)

    def generate_two_dimensional_plots(self):
        """
        Generates two-dimensional plots based on the targeted data.

        For each file in the targeted data, if the data is not empty, it retrieves the plot settings,
        creates an instance of InteractiveTwoDimensionPlotter, generates the two-dimensional plots,
        and stores them in the plot_obj_dict.

        Returns:
            None
        """
        for file, tr_df in self.targeted_data.items():
            if not tr_df.empty():
                plot_settings_dict = self._get_plot_settings(file)
                plot_config = PlotConfig()
                plot_config.update(plot_settings_dict)
                plotter = InteractiveTwoDimensionPlotter(plot_config)
                two_d_plots = plotter.plot(tr_df)
                p = gridplot(two_d_plots, ncols=self.chrom_plot_settings.num_plot_columns, sizing_mode='stretch_width')
                self.plot_obj_dict[file] = p
        return self
    
    def generate_three_dimensional_plots(self):
        """
        Generates three-dimensional plots based on the targeted data.

        Returns:
            None
        """
        for file, tr_df in self.targeted_data.items():
            if not tr_df.empty():
                plot_settings_dict = self._get_plot_settings(file)
                plot_config = PlotConfig()
                plot_config.update(plot_settings_dict)
                plotter = InteractiveThreeDimensionPlotter(plot_config)
                three_d_plots = plotter.plot(tr_df)
                self.plot_obj_dict[file] = three_d_plots
        return self
    
    def _get_plot_settings(self, x_label: str, y_label: str, plot_type=None) -> dict:
        """
        Returns the plot settings dictionary for a given plot type.

        Args:
            x_label (str): The label for the x-axis.
            y_label (str): The label for the y-axis.
            plot_type (str, optional): The type of plot. Defaults to None.

        Returns:
            dict: The plot settings dictionary.
        """
        plot_settings_dict = self.chrom_plot_settings.get_settings()
        plot_settings_dict['x_axis_label'] = x_label
        plot_settings_dict['y_axis_label'] = y_label
        plot_settings_dict['subtitle'] = f"{self.transition_list_ui.transition_settings.selected_protein} | {self.transition_list_ui.transition_settings.selected_peptide}_{self.transition_list_ui.transition_settings.selected_charge}"

        if plot_type:
            plot_settings_dict['plot_type'] = plot_type

        return plot_settings_dict

    def _generate_plots_helper(self, tr_group_collection: TransitionGroupCollection, 
                               plot_settings_dict: dict, 
                               tr_group_feature_collection: TransitionGroupFeatureCollection=None):
        """
        Generates a plot object for a given transition group and plot settings.

        Args:
            tr_group (TransitionGroupCollection): A collection of TransitionGroup objects with the mapping <RunName>:<TransitionGroup>.
            plot_settings_dict (dict): The plot settings dictionary.
            tr_group_feature (TransitionGroupFeatureCollection, optional): A collection of TransitionGroupFeature objects with the mapping <RunName>:[<TransitionGroupFeature>]. Defaults to None.

        Returns:
            bokeh.plotting.figure.Figure: The generated plot object.
        """
        try:
            for run, tr_group in tr_group_collection.items():
                plot_config = PlotConfig()
            plot_config.update(plot_settings_dict)
            plot_settings_dict['title'] = basename(run)
            plotter = InteractivePlotter(plot_config, self.verbose)
            self.plot_obj_dict[run].append(plotter.plot(tr_group, 
                                                        features=None if tr_group_feature_collection is None else tr_group_feature_collection[run], 
                                                            plot_type=plot_settings_dict['plot_type']))
        except ValueError:
            st.error("Failed to generate plot! There may be no data for selected transition group.")
  