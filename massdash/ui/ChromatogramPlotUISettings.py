"""
massdash/ui/ChromatogramPlotUISettings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import streamlit as st

# Constants
from ..constants import SMOOTHING_DICT

class ChromatogramPlotUISettings:
    """
    A class for managing the settings for a chromatogram plot.

    Attributes:
        include_ms1 (bool): Whether to include MS1 traces in the plot.
        include_ms2 (bool): Whether to include MS2 traces in the plot.
        num_plot_columns (int): The number of columns to display the plots in.
        set_x_range (bool): Whether to set a custom x-axis range for the plot.
        set_y_range (bool): Whether to set a custom y-axis range for the plot.
        do_smoothing (str): The type of smoothing to apply to the chromatograms.
        smoothing_dict (dict): A dictionary of additional settings for the smoothing.

    Methods:
        create_ui(): Creates a sidebar in Streamlit for adjusting the plot settings.
        get_settings(): Returns a dictionary of the current plot settings.
    """
    def __init__(self):
        self.include_ms1 = True
        self.include_ms2 = True
        self.num_plot_columns = 2
        self.hide_legends = False
        self.link_plot_ranges = False
        self.set_x_range = False
        self.set_y_range = False
        self.do_smoothing = 'none'
        self.smoothing_dict = {}
        self.scale_intensity = False
        self.display_plot_dimension_type = '1D'
        self.display_spectrum = False
        self.display_chromatogram = True
        self.display_mobilogram = True
        self.display_extracted_data_as_df = True
        self.aggregate_mslevels = False
        self.type_of_heatmap = "m/z vs retention time"
        self.type_of_3d_plot = "3D Scatter Plot"
        self.type_of_comparison = "retention time vs ion mobility"
        

    def create_ui(self, include_raw_data_settings: bool=False, is_ion_mobility_data: bool=False):
        """
        Creates a sidebar in Streamlit for adjusting the plot settings.

        Args:
            include_raw_data_settings (bool): Whether to include raw data settings in the sidebar. Defaults to False.
            is_ion_mobility_data (bool): Whether the data is ion mobility data. Defaults to False.

        Returns:
            self (ChromatogramPlotSettings): The current instance of the ChromatogramPlotSettings class.
        """
        st.sidebar.divider()
        st.sidebar.title("Plotting Settings")
        # Add checkboxes in the sidebar to include MS1 and/or MS2 traces
        col1, col2 = st.sidebar.columns(2)
        with col1:
            self.include_ms1 = st.checkbox("Show MS1 Traces", value=self.include_ms1, help="Show MS1 traces in the chromatogram plot.")
        with col2:
            self.include_ms2 = st.checkbox("Show MS2 Traces", value=self.include_ms2, help="Show MS2 traces in the chromatogram plot.")

        # If raw data, add checkboxes to display spectrum, chromatogram and mobilgoram plots
        if include_raw_data_settings:
            self.display_plot_dimension_type = st.sidebar.selectbox("Display Plot Type", ['1D', '2D', '3D'])
            if self.display_plot_dimension_type == '1D':
                    self.display_spectrum = st.sidebar.checkbox("Display Spectrum", value=False)
                    self.display_chromatogram = st.sidebar.checkbox("Display Chromatogram", value=True)
                    if is_ion_mobility_data:
                        self.display_mobilogram = st.sidebar.checkbox("Display Mobilogram", value=True)
                    else:
                        self.display_mobilogram = False
            if self.display_plot_dimension_type == '2D':
                self.aggregate_mslevels = st.sidebar.checkbox("Aggregate MS Levels", value=False, help="Aggregate MS1 and MS2 data into a single feature map.")
                if is_ion_mobility_data:
                    self.type_of_heatmap = st.sidebar.selectbox("Type of Heatmap", ["m/z vs retention time", "m/z vs ion mobility", "retention time vs ion mobility"], index=2, help="The type of heatmap to display.")
                else:
                    self.type_of_heatmap = st.sidebar.selectbox("Type of Heatmap", ["m/z vs retention time"], index=0, help="The type of heatmap to display.")
            if self.display_plot_dimension_type == '3D':
                self.aggregate_mslevels = st.sidebar.checkbox("Aggregate MS Levels", value=False, help="Aggregate MS1 and MS2 data into a single feature map.")
                if is_ion_mobility_data:
                    self.type_of_3d_plot = st.sidebar.selectbox("Type of 3D Plot", ["3D Line Plot", "3D Scatter Plot", "3D Surface Plot"], help="The type of 3D plot to display.")
                else:
                    self.type_of_3d_plot = st.sidebar.selectbox("Type of 3D Plot", ["3D Line Plot"], help="The type of 3D plot to display.")
                
                if self.type_of_3d_plot == "3D Surface Plot":
                    self.type_of_comparison = st.sidebar.selectbox("Type of Comparison", ["retention time vs ion mobility", "retention time vs m/z", "ion mobility vs m/z", "retention time vs ion mobility vs m/z"], help="The type of heatmap to display.")
                    
            self.display_extracted_data_as_df = st.sidebar.checkbox("Display Extracted Data as DataFrame", value=True, help="Display the extracted data as a DataFrame.")

        with st.sidebar.expander("Advanced Settings"):
            # Display plots in N columns
            self.num_plot_columns = st.number_input("Number of Columns", min_value=1, value=self.num_plot_columns, help="The number of columns to display the plots in.")
            
            # Toggle to hide legends
            self.hide_legends = st.checkbox("Hide Legends", value=False, help="Hide the legends in the chromatogram plot.")

            # Add Checkboxes for setting x-range and y-range
            col1, col2, col3 = st.columns(3)
            with col1:
                self.link_plot_ranges = st.checkbox("Link plots", value=self.set_x_range, help="Link the x and y ranges of the plots.", disabled=True)
            with col2:
                self.set_x_range = st.checkbox("Share x-range", value=self.set_x_range, help="Share the x-range of the plots.")
            with col3:
                self.set_y_range = st.checkbox("Share y-range", value=self.set_y_range, help="Share the y-range of the plots.")

            # Perform Smoothing of the chromatograms
            self.do_smoothing = st.selectbox("Smoothing", list(SMOOTHING_DICT.keys()), help="The type of smoothing to apply to the chromatograms.")
            
            self.smoothing_dict = SMOOTHING_DICT[self.do_smoothing]
            if self.smoothing_dict['type'] == 'sgolay':
                # Create two columns for side-by-side widgets
                col1, col2 = st.columns(2)

                # Add widget for sgolay_polynomial_order in the first column
                self.smoothing_dict['sgolay_polynomial_order'] = col1.number_input("Polynomial Order", min_value=1, max_value=10, value=3, step=1, help="The order of the polynomial to use for smoothing the chromatograms.")

                # Add widget for sgolay_frame_length in the second column
                self.smoothing_dict['sgolay_frame_length'] = col2.number_input("Frame Length", min_value=1, max_value=50, value=11, step=1, help="The length of the frame to use for smoothing the chromatograms.")

            if self.smoothing_dict['type'] == 'gauss':
                # Create two columns for side-by-side widgets
                col1, col2 = st.columns(2)

                # Add widget for gaussian_sigma in the first column
                self.smoothing_dict['gaussian_sigma'] = col1.number_input("Sigma", min_value=1.0, max_value=10.0, value=2.0, step=0.1, help="The gaussian sigma to use for smoothing the chromatograms.")

                # Add widget for gaussian_window in the second column
                self.smoothing_dict['gaussian_window'] = col2.number_input("Window Length", min_value=1, max_value=50, value=11, step=1, help="The size of the window to use for smoothing the chromatograms.")

            self.scale_intensity = st.checkbox("Scale Intensity", value=False, key='plotting_settings_scale_intensity', help="Scale the intensity of the chromatograms to the same maximum value.")
        return self  # Return self for method chaining

    def get_settings(self):
        """
        Returns a dictionary of the current plot settings.

        Returns:
            settings (dict): A dictionary of the current plot settings.
        """
        return {
            "include_ms1": self.include_ms1,
            "include_ms2": self.include_ms2,
            "num_plot_columns": self.num_plot_columns,
            "hide_legends": self.hide_legends,
            "set_x_range": self.set_x_range,
            "set_y_range": self.set_y_range,
            "do_smoothing": self.do_smoothing,
            "smoothing_dict": self.smoothing_dict,
            "scale_intensity": self.scale_intensity,
            "aggregate_mslevels": self.aggregate_mslevels,
            "type_of_heatmap": self.type_of_heatmap,
            "type_of_3d_plot": self.type_of_3d_plot,
            "type_of_comparison": self.type_of_comparison
        }
