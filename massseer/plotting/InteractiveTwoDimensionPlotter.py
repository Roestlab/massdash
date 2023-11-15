from typing import List, Tuple
import numpy as np
import pandas as pd
from bokeh.models import HoverTool, CrosshairTool
from bokeh.plotting import figure
from matplotlib import cm


def rgb_to_hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))

class InteractiveTwoDimensionPlotter:
    """
    A class for interactive two-dimensional plotting.

    Attributes:
    - df: pd.DataFrame
        The input DataFrame containing the data for plotting.
    """

    # Convert the Matplotlib colormap to a list of RGB hex colors
    AFMHOT_CMAP = [rgb_to_hex(cm.afmhot_r(i)[:3]) for i in range(256)]


    def __init__(self, df: pd.DataFrame):
        """
        Initialize the InteractiveTwoDimensionPlotter instance.

        Parameters:
        - df: pd.DataFrame
            The input DataFrame containing the data for plotting.
        """
        self.df = df

    def plot(self, aggregate: bool = False):
        """
        Plot the data.

        Parameters:
        - aggregate: bool, optional (default=False)
            Whether to aggregate the data before plotting.
        """
        if aggregate:
            plots = self.plot_aggregated_heatmap()
        else:
            plots = self.plot_individual_heatmaps()
        return plots

    def plot_individual_heatmaps(self):
        """
        Plot a heatmap based on the provided DataFrame.
        """
        arr = self.df.pivot_table(index='im', columns='rt', values='int', aggfunc=np.sum)

        im_arr, rt_arr, dw_main, dh_main, rt_min, rt_max, im_min, im_max = self.get_plot_parameters(arr)

        linked_crosshair = CrosshairTool(dimensions="both")

        two_d_plots = []
        for (ms_level, Annotation, product_mz), group_df in self.df.sort_values(by=['ms_level', 'Annotation', 'product_mz']).groupby(['ms_level', 'Annotation', 'product_mz']):
            arr = group_df.pivot_table(index='im', columns='rt', values='int', aggfunc=np.sum)
            arr = self.prepare_array(arr)

            title_text = f"MS{ms_level} | {Annotation} | {product_mz} m/z"

            plot = self.create_heatmap_plot(title_text, arr, rt_min, rt_max, im_min, im_max, dw_main, dh_main, linked_crosshair, two_d_plots)

            two_d_plots.append(plot)

        return two_d_plots

    def plot_aggregated_heatmap(self):
        """
        Plot an aggregated heatmap based on the provided DataFrame.
        """
        arr = self.df.pivot_table(index='im', columns='rt', values='int', aggfunc=np.sum)

        im_arr, rt_arr, dw_main, dh_main, rt_min, rt_max, im_min, im_max = self.get_plot_parameters(arr)

        linked_crosshair = CrosshairTool(dimensions="both")

        arr = self.prepare_array(arr)

        title_text = f"Aggregated"

        two_d_plots = []
        plot = self.create_heatmap_plot(title_text, arr, rt_min, rt_max, im_min, im_max, dw_main, dh_main, linked_crosshair, two_d_plots)
        two_d_plots.append(plot)
        return two_d_plots

    def get_plot_parameters(self, arr: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, float, float, float, float, float, float]:
        """
        Get parameters for plotting.

        Parameters:
        - arr: pd.DataFrame
            The DataFrame for which parameters are needed.

        Returns:
        - Tuple[np.ndarray, np.ndarray, float, float, float, float, float, float]
            Tuple containing parameters: im_arr, rt_arr, dw_main, dh_main, rt_min, rt_max, im_min, im_max.
        """
        im_arr = arr.index.to_numpy()
        rt_arr = arr.columns.to_numpy()

        dw_main = rt_arr.max() - rt_arr.min()
        dh_main = im_arr.max() - im_arr.min()

        rt_min, rt_max, im_min, im_max = rt_arr.min(), rt_arr.max(), im_arr.min(), im_arr.max()

        print(f"RT min: {rt_min} | IM min: {im_min} | dw: {dw_main} | dh: {dh_main}")

        return im_arr, rt_arr, dw_main, dh_main, rt_min, rt_max, im_min, im_max

    def prepare_array(self, arr: pd.DataFrame) -> np.ndarray:
        """
        Prepare the array for plotting.

        Parameters:
        - arr: pd.DataFrame
            The input DataFrame.

        Returns:
        - np.ndarray
            The prepared array.
        """
        arr = arr.to_numpy()
        arr[np.isnan(arr)] = 0
        return arr

    def create_heatmap_plot(self, title_text: str, arr: np.ndarray, rt_min: float, rt_max: float, im_min: float, im_max: float, dw_main: float, dh_main: float, linked_crosshair, two_d_plots: List[figure]) -> figure:
        """
        Create a heatmap plot.

        Parameters:
        - title_text: str
            The title text for the plot.
        - arr: np.ndarray
            The array to be plotted.
        - rt_min: float
            Minimum value for the rt axis.
        - rt_max: float
            Maximum value for the rt axis.
        - im_min: float
            Minimum value for the im axis.
        - im_max: float
            Maximum value for the im axis.
        - dw_main: float
            Width of the plot.
        - dh_main: float
            Height of the plot.
        - linked_crosshair: CrosshairTool
            The linked crosshair tool.
        - two_d_plots: List[figure]
            List of previously created 2D plots.

        Returns:
        - figure
            The created Bokeh figure.
        """
        plot = figure(title=title_text, x_range=(rt_min, rt_max), y_range=(im_min, im_max))

        heatmap_img = plot.image(image=[arr], x=rt_min, y=im_min, dw=dw_main, dh=dh_main, palette=self.AFMHOT_CMAP)

        hover = HoverTool(renderers=[heatmap_img], tooltips=[("Value", "@image")])
        plot.add_tools(hover)
        plot.add_tools(linked_crosshair)

        plot.grid.visible = False

        return plot