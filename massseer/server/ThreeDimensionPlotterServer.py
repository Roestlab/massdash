from os.path import basename

# Plotting
from massseer.plotting.GenericPlotter import PlotConfig
from massseer.plotting.InteractiveThreeDimensionPlotter import InteractiveThreeDimensionPlotter
# UI
from massseer.ui.TransitionListUISettings import TransitionListUISettings
from massseer.ui.ChromatogramPlotUISettings import ChromatogramPlotUISettings


class ThreeDimensionalPlotter:
    """
    Class for generating three-dimensional plots based on targeted data.

    Args:
        targeted_data (dict): A dictionary containing targeted data.
        transition_list_ui (TransitionListUISettings): An instance of TransitionListUISettings class.
        chrom_plot_settings (ChromatogramPlotUISettings): An instance of ChromatogramPlotUISettings class.

    Attributes:
        targeted_data (dict): A dictionary containing targeted data.
        transition_list_ui (TransitionListUISettings): An instance of TransitionListUISettings class.
        chrom_plot_settings (ChromatogramPlotUISettings): An instance of ChromatogramPlotUISettings class.
        plot_obj_dict (dict): A dictionary to store the generated plot objects.

    Methods:
        generate_three_dimensional_plots: Generates three-dimensional plots based on the targeted data.
        _get_plot_settings: Retrieves the plot settings for a specific file.

    """

    def __init__(self, targeted_data, transition_list_ui: TransitionListUISettings, chrom_plot_settings: ChromatogramPlotUISettings):
        self.targeted_data = targeted_data
        self.transition_list_ui = transition_list_ui
        self.chrom_plot_settings = chrom_plot_settings
        self.plot_obj_dict = {}

    def generate_three_dimensional_plots(self):
        """
        Generates three-dimensional plots based on the targeted data.

        Returns:
            None
        """
        for file, tr_df in self.targeted_data.items():
            if not tr_df.empty:
                plot_settings_dict = self._get_plot_settings(file.filename)
                plot_config = PlotConfig()
                plot_config.update(plot_settings_dict)
                plotter = InteractiveThreeDimensionPlotter(tr_df, plot_config)
                three_d_plots = plotter.plot()
                self.plot_obj_dict[file] = three_d_plots
        return self

    def _get_plot_settings(self, file) -> dict:
        """
        Retrieves the plot settings for a specific file.

        Args:
            file (str): The file name.

        Returns:
            dict: A dictionary containing the plot settings.
        """
        plot_settings_dict = self.chrom_plot_settings.get_settings()
        plot_settings_dict['title'] = basename(file)
        plot_settings_dict['subtitle'] = f"{self.transition_list_ui.transition_settings.selected_protein} | {self.transition_list_ui.transition_settings.selected_peptide}_{self.transition_list_ui.transition_settings.selected_charge}"
        return plot_settings_dict