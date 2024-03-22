"""
massdash/plotting/GenericPlotter
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""


from abc import ABC, abstractmethod
from typing import List, Optional, Literal

# Structs
from ..structs.TransitionGroupFeature import TransitionGroupFeature
from ..structs.TransitionGroup import TransitionGroup

class PlotConfig:
    """
    A class representing the configuration for a plot.

    Attributes:
        include_ms1 (bool): A flag indicating whether to include MS1 data.
        include_ms2 (bool): A flag indicating whether to include MS2 data.
        num_plot_columns (int): The number of columns to be displayed in the plot.
        hide_legends (bool): A flag indicating whether to hide the legends in the plot.
        title (str): The title of the plot.
        subtitle (str): The subtitle of the plot.
        x_axis_label (str): The label for the x-axis.
        y_axis_label (str): The label for the y-axis.
        smoothing_dict (dict): A dictionary containing the parameters for smoothing the data.
            e.g. {'type': 'sgolay', 'sgolay_polynomial_order': 3, 'sgolay_frame_length': 11}
            e.g. {'type': 'none'}
        x_range (tuple): The range of values to be displayed on the x-axis.
        y_range (tuple): The range of values to be displayed on the y-axis.
        scale_intensity (bool): A flag indicating whether to scale the intensity of the data.
        aggregate_mslevels (bool): A flag indicating whether to aggregate the data within an MS level.
        type_of_heatmap (str): The type of heatmap to be displayed. (Only used for InteractiveTwoDimensionalPlotter)
        type_of_3d_plot (str): The type of 3D plot to be displayed. (Only used for InteractiveThreeDimensionalPlotter)
        type_of_comparison (str): The type of comparison to be displayed. (Only used for InteractivePlotter)
        context (str): The context in which the plot is being displayed.
             valid: "streamlit", "jupyter" 
        normalization_dict (dict): A dictionary containing the parameters for normalizing the data (2D heatmap only)
    """
    def __init__(self):
        self.include_ms1 = True
        self.include_ms2 = True
        self.num_plot_columns = 2
        self.hide_legends = False
        self.title = None
        self.subtitle = None
        self.x_axis_label = "Retention Time"
        self.y_axis_label = "Intensity"
        # Default for 1D smoothing
        self.smoothing_dict = dict(type='none', # alternative sgolay or guass 
                                   sgolay_polynomial_order=3, 
                                   sgolay_frame_length=11, 
                                   gaussian_sigma=2.0, 
                                   gaussian_window=11)
        #ALTERNATIVE 1D: self.smoothing_dict = {'type': ['sgolay', 'gauss'], 'sgolay_polynomial_order': 3, 'sgolay_frame_length': 11, 'gaussian_sigma': 2.0, 'gaussian_window': 11}
        #ALTERNATIVE 2D: self.smoothing_dict = {'type': 'gauss', 'gaussian_sigma': 1.2}

        self.x_range = None
        self.y_range = None
        self.scale_intensity = False
        self.aggregate_mslevels = False
        self.type_of_heatmap = "m/z vs retention time"
        self.type_of_3d_plot = "3D Scatter Plot"
        self.type_of_comparison = "retention time vs ion mobility"
        self.context = "streamlit" # or "jupyter"
        self.normalization_dict = {'type':'none'} # or {'type':'equalization', 'bins': (int)}
        self.ms_level_str = 'ms1ms2'

    def __str__(self):
        return f"{'-'*8} PlotConfig {'-'*8}\ninclude_ms1: {self.include_ms1}\ninclude_ms2: {self.include_ms2}\nnum_plot_columns: {self.num_plot_columns}\ntitle: {self.title}\nsubtitle: {self.subtitle}\nx_axis_label: {self.x_axis_label}\ny_axis_label: {self.y_axis_label}\nsmoothing_dict: {self.smoothing_dict}\nx_range: {self.x_range}\ny_range: {self.y_range}\nscale_intensity: {self.scale_intensity}\naggregate_mslevels: {self.aggregate_mslevels}\ntype_of_heatmap: {self.type_of_heatmap}\ntype_of_3d_plot: {self.type_of_3d_plot}\ntype_of_comparison: {self.type_of_comparison}\n{'-'*30}"

    def update(self, config_dict):
        """
        Update the configuration attributes using a dictionary.

        Args:
            config_dict (dict): A dictionary containing configuration values.
        """
        for key, value in config_dict.items():
            if hasattr(self, key):
                setattr(self, key, value)
                
        if self.include_ms1 and self.include_ms2:
            self.ms_level_str = 'ms1ms2'
        elif self.include_ms1 and not self.include_ms2:
            self.ms_level_str = 'ms1'
        elif not self.include_ms1 and self.include_ms2:
            self.ms_level_str = 'ms2'

class GenericPlotter(ABC):
    """ 
    A Generic plotter abstract class.
    """

    def __init__(self, config: PlotConfig):
        self.include_ms1 = config.include_ms1
        self.include_ms2 = config.include_ms2
        self.hide_legends = config.hide_legends
        self.title = config.title
        self.subtitle = config.subtitle
        self.x_axis_label = config.x_axis_label
        self.y_axis_label = config.y_axis_label
        self.smoothing_dict = config.smoothing_dict
        self.x_range = config.x_range
        self.y_range = config.y_range
        self.scale_intensity = config.scale_intensity
        self.normalization_dict = config.normalization_dict
        self.ms_level_str = config.ms_level_str
            
    @abstractmethod
    def plot(self, transitionGroup: TransitionGroup, features: Optional[List[TransitionGroupFeature]] = None, plot_type: Literal['chromatogram', 'mobilogram', 'spectrum'] = 'chromatogram'):
        pass




