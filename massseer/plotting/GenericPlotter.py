
from abc import ABC, abstractmethod
from typing import List, Optional, Literal
from massseer.structs.TransitionGroupFeature import TransitionGroupFeature
from massseer.structs.TransitionGroup import TransitionGroup

class PlotConfig:
    """
    A class representing the configuration for a plot.

    Attributes:
    -----------
    title : str or None
        The title of the plot.
    subtitle : str or None
        The subtitle of the plot.
    x_axis_label : str
        The label for the x-axis.
    y_axis_label : str
        The label for the y-axis.
    smoothing_dict : dict
        A dictionary containing the parameters for smoothing the data.
    x_range : tuple or None
        The range of values to be displayed on the x-axis.
    y_range : tuple or None
        The range of values to be displayed on the y-axis.
    scale_intensity : bool
        A flag indicating whether to scale the intensity of the data.
    """
    def __init__(self):
        self.include_ms1 = True
        self.include_ms2 = True
        self.num_plot_columns = 2
        self.title = None
        self.subtitle = None
        self.x_axis_label = "Retention Time"
        self.y_axis_label = "Intensity"
        self.smoothing_dict = {'type': 'sgolay', 'sgolay_polynomial_order': 3, 'sgolay_frame_length': 11}
        self.x_range = None
        self.y_range = None
        self.scale_intensity = False
        self.aggregate_mslevels = False
        self.type_of_heatmap = "m/z vs retention time"
        self.type_of_3d_plot = "3D Scatter Plot"
        self.type_of_comparison = "retention time vs ion mobility"
        self.context = "streamlit" # or "jupyter"

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

class GenericPlotter(ABC):
    """ 
    This is a generic plotter class 
    """

    def __init__(self, config: PlotConfig):
        self.include_ms1 = config.include_ms1
        self.include_ms2 = config.include_ms2
        self.title = config.title
        self.subtitle = config.subtitle
        self.x_axis_label = config.x_axis_label
        self.y_axis_label = config.y_axis_label
        self.smoothing_dict = config.smoothing_dict
        self.x_range = config.x_range
        self.y_range = config.y_range
        self.scale_intensity = config.scale_intensity

    @abstractmethod
    def plot(self, transitionGroup: TransitionGroup, features: Optional[List[TransitionGroupFeature]] = None, plot_type: Literal['chromatogram', 'mobilogram', 'spectrum'] = 'chromatogram'):
        pass




