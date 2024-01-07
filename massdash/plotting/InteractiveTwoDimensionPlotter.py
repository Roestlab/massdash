from typing import List, Tuple

# Data modules
import numpy as np
import pandas as pd

# Plotting modules
from bokeh.models import HoverTool, CrosshairTool, Title
from bokeh.plotting import figure
from matplotlib import cm

# Plotting
from .GenericPlotter import PlotConfig
# Structs
from structs.FeatureMap import FeatureMap

def rgb_to_hex(rgb):
    """
    Converts an RGB color value to its corresponding hexadecimal representation.

    Args:
        rgb (tuple): A tuple containing the RGB values as floats between 0 and 1.

    Returns:
        str: The hexadecimal representation of the RGB color.

    Example:
        >>> rgb_to_hex((0.5, 0.75, 1.0))
        '#7fbfff'
    """
    return "#{:02x}{:02x}{:02x}".format(int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))

class InteractiveTwoDimensionPlotter:
    """
    A class for interactive two-dimensional plotting.

    Attributes:
        df (pd.DataFrame): The input DataFrame containing the data for plotting.
        config (PlotConfig): The configuration for plotting.
        
    Methods:
        plot: Plot the data.
        plot_individual_heatmaps: Plot a heatmap based on the provided DataFrame.
        plot_aggregated_heatmap: Plot an aggregated heatmap based on the provided DataFrame.
        get_axis_titles: Returns the axis titles based on the type of heatmap.
        get_plot_parameters: Get parameters for plotting.
        prepare_array: Prepare the array for plotting.
        create_heatmap_plot: Create a heatmap plot.
    """

    # Convert the Matplotlib colormap to a list of RGB hex colors
    AFMHOT_CMAP = [rgb_to_hex(cm.afmhot_r(i)[:3]) for i in range(256)]

    def __init__(self, config: PlotConfig):
        """
        Initialize the InteractiveTwoDimensionPlotter instance.

        Args:
            config (PlotConfig): The configuration for plotting.
        """
        self.config = config
        self.fig = None # set by the plot method

    def plot(self, featureMap: FeatureMap):
        """
        Plot the data.

        Parameters:
        - aggregate: bool, optional (default=False)
            Whether to aggregate the data before plotting.
        """
        if self.config.aggregate_mslevels:
            plots = self.plot_aggregated_heatmap(featureMap)
        else:
            plots = self.plot_individual_heatmaps(featureMap)
        self.fig = plots
        return plots

    def plot_individual_heatmaps(self, featureMap: FeatureMap):
        """
        Plot a heatmap based on the provided featureMap
        """
        df = featureMap.feature_df
        if self.config.type_of_heatmap == "m/z vs retention time":
            arr = df.pivot_table(index='mz', columns='rt', values='int', aggfunc="sum")
        elif self.config.type_of_heatmap == "m/z vs ion mobility":
            arr = df.pivot_table(index='mz', columns='im', values='int', aggfunc="sum")
        elif self.config.type_of_heatmap == "retention time vs ion mobility":
            arr = df.pivot_table(index='im', columns='rt', values='int', aggfunc="sum")

        linked_crosshair = CrosshairTool(dimensions="both")

        two_d_plots = []
        for (ms_level, Annotation, product_mz), group_df in df.sort_values(by=['ms_level', 'Annotation', 'product_mz']).groupby(['ms_level', 'Annotation', 'product_mz']):
            if not self.config.include_ms1 and ms_level == 1:
                continue
            
            if not self.config.include_ms2 and ms_level == 2:
                continue

            if self.config.type_of_heatmap == "m/z vs retention time":
                arr = group_df.pivot_table(index='mz', columns='rt', values='int', aggfunc="sum")
            elif self.config.type_of_heatmap == "m/z vs ion mobility":
                arr = group_df.pivot_table(index='mz', columns='im', values='int', aggfunc="sum")
            elif self.config.type_of_heatmap == "retention time vs ion mobility":
                arr = group_df.pivot_table(index='im', columns='rt', values='int', aggfunc="sum")

            im_arr, rt_arr, dw_main, dh_main, rt_min, rt_max, im_min, im_max = self.get_plot_parameters(arr)
            arr = self.prepare_array(arr)

            title_text = f"MS{ms_level} | {Annotation} | {product_mz} m/z"

            plot = self.create_heatmap_plot(title_text, arr, rt_min, rt_max, im_min, im_max, dw_main, dh_main, linked_crosshair, two_d_plots)

            two_d_plots.append(plot)

        return two_d_plots

    def plot_aggregated_heatmap(self, featureMap: FeatureMap):
        """
        Plot an aggregated heatmap based on the provided DataFrame.

        Args:
            df (pd.DataFrame): The input DataFrame.
        
        Returns:
            List[figure]: A list of two-dimensional plots.
        """
        df = featureMap.feature_df
        if not self.config.include_ms1:
            self.df = self.df[self.df['ms_level'] != 1]
        if not self.config.include_ms2:
            self.df = self.df[self.df['ms_level'] != 2]
            
        if self.config.type_of_heatmap == "m/z vs retention time":
            arr = df.pivot_table(index='mz', columns='rt', values='int', aggfunc="sum")
        elif self.config.type_of_heatmap == "m/z vs ion mobility":
            arr = df.pivot_table(index='mz', columns='im', values='int', aggfunc="sum")
        elif self.config.type_of_heatmap == "retention time vs ion mobility":
            arr = df.pivot_table(index='im', columns='rt', values='int', aggfunc="sum")

        im_arr, rt_arr, dw_main, dh_main, rt_min, rt_max, im_min, im_max = self.get_plot_parameters(arr)

        linked_crosshair = CrosshairTool(dimensions="both")

        arr = self.prepare_array(arr)

        title_text = f"Aggregated"

        two_d_plots = []
        plot = self.create_heatmap_plot(title_text, arr, rt_min, rt_max, im_min, im_max, dw_main, dh_main, linked_crosshair, two_d_plots)
        two_d_plots.append(plot)
        return two_d_plots

    def get_axis_titles(self) -> Tuple[str, str]:
        """
        Returns the axis titles based on the type of heatmap.

        Returns:
            Tuple[str, str]: The axis titles.
        """
        if self.config.type_of_heatmap == "m/z vs retention time":
            return "Retention time (s)", "m/z"
        elif self.config.type_of_heatmap == "m/z vs ion mobility":
            return "Ion mobility (1/K0)", "m/z"
        elif self.config.type_of_heatmap == "retention time vs ion mobility":
            return "Retention time (s)", "Ion mobility (1/K0)"

    def get_plot_parameters(self, arr: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, float, float, float, float, float, float]:
        """
        Get parameters for plotting.

        Args:
            arr (pd.DataFrame): The input DataFrame.
            
        Returns:
            Tuple[np.ndarray, np.ndarray, float, float, float, float, float, float]: The parameters for plotting.
        """
        im_arr = arr.index.to_numpy()
        rt_arr = arr.columns.to_numpy()

        dw_main = rt_arr.max() - rt_arr.min()
        dh_main = im_arr.max() - im_arr.min()

        rt_min, rt_max, im_min, im_max = rt_arr.min(), rt_arr.max(), im_arr.min(), im_arr.max()

        return im_arr, rt_arr, dw_main, dh_main, rt_min, rt_max, im_min, im_max

    def prepare_array(self, arr: pd.DataFrame) -> np.ndarray:
        """
        Prepare the array for plotting.

        Args:
            arr (pd.DataFrame): The input DataFrame.
            
        Returns:
            np.ndarray: The prepared array.
        """
        arr = arr.to_numpy()
        arr[np.isnan(arr)] = 0
        return arr

    def create_heatmap_plot(self, title_text: str, arr: np.ndarray, rt_min: float, rt_max: float, im_min: float, im_max: float, dw_main: float, dh_main: float, linked_crosshair, two_d_plots: List[figure]) -> figure:
        """
        Create a heatmap plot.

        Args:
            title_text (str): The title text.
            arr (np.ndarray): The input array.
            rt_min (float): The minimum retention time.
            rt_max (float): The maximum retention time.
            im_min (float): The minimum ion mobility.
            im_max (float): The maximum ion mobility.
            dw_main (float): The width of the main plot.
            dh_main (float): The height of the main plot.
            linked_crosshair: The linked crosshair.
            two_d_plots (List[figure]): The list of two-dimensional plots.
        
        Returns:
            figure: The heatmap plot.
        """
        x_axis_title, y_axis_title = self.get_axis_titles()
        plot = figure(x_range=(rt_min, rt_max), y_range=(im_min, im_max), x_axis_label=x_axis_title, y_axis_label=y_axis_title)
        
        # Add title
        if self.config.title is not None:
            plot.title.text = self.config.title
            plot.title.text_font_size = "16pt"
            plot.title.align = "center"

        if self.config.subtitle is not None:
            # Create a subtitle
            plot.add_layout(Title(text=self.config.subtitle + " | " + title_text, text_font_style="italic"), 'above')

        heatmap_img = plot.image(image=[arr], x=rt_min, y=im_min, dw=dw_main, dh=dh_main, palette=self.AFMHOT_CMAP)

        hover = HoverTool(renderers=[heatmap_img], tooltips=[("Value", "@image")])
        plot.add_tools(hover)
        plot.add_tools(linked_crosshair)

        plot.grid.visible = False

        return plot

    def show(self):
        """
        Show the plots.
        """
        from bokeh.plotting import show
        from bokeh.io import output_notebook 
        output_notebook()
        if isinstance(self.fig, list):
            for fig in self.fig:
                show(fig)
        else:
            show(self.fig)

