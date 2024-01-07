"""
massdash/server/OneDimensionPlotterServer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

from os.path import basename
import streamlit as st

# Plotting
from plotting.GenericPlotter import PlotConfig
from plotting.InteractivePlotter import InteractivePlotter
# Server
from .PeakPickingServer import PeakPickingServer
# Structs
from structs.TransitionGroup import TransitionGroup
from structs.TransitionGroupFeature import TransitionGroupFeature
from structs.FeatureMap import FeatureMap
# UI
from ui.TransitionListUISettings import TransitionListUISettings
from ui.ChromatogramPlotUISettings import ChromatogramPlotUISettings
from ui.PeakPickingUISettings import PeakPickingUISettings

class OneDimensionPlotterServer:
    """
    A class that generates chromatogram plots for a given transition group dictionary.

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
                 feature_map_dict: dict[FeatureMap], 
                 transition_list_ui: TransitionListUISettings, chrom_plot_settings: ChromatogramPlotUISettings, 
                 peak_picking_settings: PeakPickingUISettings,
                 verbose: bool=False):
        self.feature_map_dict = feature_map_dict 
        self.transition_list_ui = transition_list_ui
        self.chrom_plot_settings = chrom_plot_settings
        self.peak_picking_settings = peak_picking_settings
        self.plot_obj_dict = {}
        self.verbose = verbose

    def generate_chromatogram_plots(self):
        """
        Generates chromatogram plots for each file in the transition group dictionary.
        """
        for file, feature_map in self.feature_map_dict.items():
            run_plots_list = []
            
            # Generate Spectrum Plot 
            if self.chrom_plot_settings.display_spectrum:
                tr_group = feature_map.to_spectra()
                plot_settings_dict = self._get_plot_settings('m/z', 'Intensity', file, 'spectra')
                plot_spectrum_obj = self._generate_plot(tr_group, plot_settings_dict)
                run_plots_list.append(plot_spectrum_obj)

            # Generate Chromatogram Plot
            if self.chrom_plot_settings.display_chromatogram:
                tr_group = feature_map.to_chromatograms()
                # Perform peak picking if enabled
                peak_picker = PeakPickingServer(self.peak_picking_settings, self.chrom_plot_settings)
                tr_group_feature_data = peak_picker.perform_peak_picking(tr_group_data={'tmp':tr_group}, transition_list_ui=self.transition_list_ui)
                plot_settings_dict = self._get_plot_settings('Retention Time (s)', 'Intensity', file, 'chromatogram')
                plot_obj = self._generate_plot(tr_group, plot_settings_dict, tr_group_feature_data['tmp'])
                run_plots_list.append(plot_obj)

            # Generate Mobilogram Plot
            if self.chrom_plot_settings.display_mobilogram:
                tr_group = feature_map.to_mobilograms()
                plot_settings_dict = self._get_plot_settings('Ion Mobility (1/K0)', 'Intensity', file, 'mobilogram')
                plot_mobilo_obj = self._generate_plot(tr_group, plot_settings_dict)
                run_plots_list.append(plot_mobilo_obj)

            self.plot_obj_dict[file] = run_plots_list
        return self

    def _get_plot_settings(self, x_label: str, y_label: str, file: str, plot_type=None) -> dict:
        """
        Returns the plot settings dictionary for a given plot type.

        Args:
            x_label (str): The label for the x-axis.
            y_label (str): The label for the y-axis.
            file (str): The file name.
            plot_type (str, optional): The type of plot. Defaults to None.

        Returns:
            dict: The plot settings dictionary.
        """
        plot_settings_dict = self.chrom_plot_settings.get_settings()
        plot_settings_dict['x_axis_label'] = x_label
        plot_settings_dict['y_axis_label'] = y_label
        plot_settings_dict['title'] = basename(file)
        plot_settings_dict['subtitle'] = f"{self.transition_list_ui.transition_settings.selected_protein} | {self.transition_list_ui.transition_settings.selected_peptide}_{self.transition_list_ui.transition_settings.selected_charge}"

        if plot_type:
            plot_settings_dict['plot_type'] = plot_type

        return plot_settings_dict

    def _generate_plot(self, tr_group: TransitionGroup, plot_settings_dict: dict, tr_group_feature: TransitionGroupFeature=None):
        """
        Generates a plot object for a given transition group and plot settings.

        Args:
            tr_group (TransitionGroup): An object representing a transition group.
            plot_settings_dict (dict): The plot settings dictionary.
            tr_group_feature (TransitionGroupFeature, optional): An object representing the transition group feature data. Defaults to None.

        Returns:
            bokeh.plotting.figure.Figure: The generated plot object.
        """
        plot_config = PlotConfig()
        plot_config.update(plot_settings_dict)
        try:
            plotter = InteractivePlotter(plot_config, self.verbose)
            plot_obj = plotter.plot(tr_group, features=tr_group_feature, plot_type=plot_settings_dict['plot_type'])
            return plot_obj
        except ValueError:
            st.error("Failed to generate plot! There may be no data for selected transition group.")
            return None
