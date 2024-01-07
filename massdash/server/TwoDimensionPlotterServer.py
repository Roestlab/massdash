"""
massdash/server/TwoDimensionPlotterServer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

from os.path import basename
from bokeh.layouts import gridplot
from typing import Dict

# Plotting
from massdash.plotting.GenericPlotter import PlotConfig
from massdash.plotting.InteractiveTwoDimensionPlotter import InteractiveTwoDimensionPlotter
# Structs
from massdash.structs.FeatureMap import FeatureMap
# UI
from massdash.ui.TransitionListUISettings import TransitionListUISettings
from massdash.ui.ChromatogramPlotUISettings import ChromatogramPlotUISettings


class TwoDimensionPlotterServer:
    """
    Class for generating two-dimensional plots based on targeted data.

    Args:
        targeted_data dict[FeatureMap]: A dictionary of feature maps, each entry corresponds with one run
        transition_list_ui (TransitionListUISettings): An instance of TransitionListUISettings class.
        chrom_plot_settings (ChromatogramPlotUISettings): An instance of ChromatogramPlotUISettings class.

    Attributes:
        targeted_data (dict): A dictionary containing targeted data.
        transition_list_ui (TransitionListUISettings): An instance of TransitionListUISettings class.
        chrom_plot_settings (ChromatogramPlotUISettings): An instance of ChromatogramPlotUISettings class.
        plot_obj_dict (dict): A dictionary to store the generated plots.

    Methods:
        generate_two_dimensional_plots: Generates two-dimensional plots based on the targeted data.
        _get_plot_settings: Retrieves the plot settings for a specific file.

    """

    def __init__(self, targeted_data: dict[FeatureMap], transition_list_ui: TransitionListUISettings, chrom_plot_settings: ChromatogramPlotUISettings):
        self.targeted_data = targeted_data
        self.transition_list_ui = transition_list_ui
        self.chrom_plot_settings = chrom_plot_settings
        self.plot_obj_dict = {}

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

    def _get_plot_settings(self, file: str) -> dict:
        """
        Retrieves the plot settings for a specific file.

        Args:
            file (str): The file for which to retrieve the plot settings.

        Returns:
            dict: A dictionary containing the plot settings.

        """
        plot_settings_dict = self.chrom_plot_settings.get_settings()
        plot_settings_dict['title'] = basename(file)
        plot_settings_dict['subtitle'] = f"{self.transition_list_ui.transition_settings.selected_protein} | {self.transition_list_ui.transition_settings.selected_peptide}_{self.transition_list_ui.transition_settings.selected_charge}"
        return plot_settings_dict
