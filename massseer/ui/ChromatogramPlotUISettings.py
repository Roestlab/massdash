import streamlit as st

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
        self.link_plot_ranges = False
        self.set_x_range = False
        self.set_y_range = False
        self.do_smoothing = 'none'
        self.smoothing_dict = {}
        self.scale_intensity = False

    def create_ui(self):
        """
        Creates a sidebar in Streamlit for adjusting the plot settings.

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

        with st.sidebar.expander("Advanced Settings"):
            # Display plots in N columns
            self.num_plot_columns = st.number_input("Number of Columns", min_value=1, value=self.num_plot_columns, help="The number of columns to display the plots in.")

            # Add Checkboxes for setting x-range and y-range
            col1, col2, col3 = st.columns(3)
            with col1:
                self.link_plot_ranges = st.checkbox("Link plots", value=self.set_x_range, help="Link the x and y ranges of the plots.", disabled=True)
            with col2:
                self.set_x_range = st.checkbox("Share x-range", value=self.set_x_range, help="Share the x-range of the plots.")
            with col3:
                self.set_y_range = st.checkbox("Share y-range", value=self.set_y_range, help="Share the y-range of the plots.")

            # Perform Smoothing of the chromatograms
            self.do_smoothing = st.selectbox("Smoothing", ['sgolay', 'none'], help="The type of smoothing to apply to the chromatograms.")

            self.smoothing_dict['type'] = self.do_smoothing
            if self.do_smoothing == 'sgolay':
                # Create two columns for side-by-side widgets
                col1, col2 = st.columns(2)

                # Add widget for sgolay_polynomial_order in the first column
                self.smoothing_dict['sgolay_polynomial_order'] = col1.number_input("Polynomial Order", min_value=1, max_value=10, value=3, step=1, help="The order of the polynomial to use for smoothing the chromatograms.")

                # Add widget for sgolay_frame_length in the second column
                self.smoothing_dict['sgolay_frame_length'] = col2.number_input("Frame Length", min_value=1, max_value=50, value=11, step=1, help="The length of the frame to use for smoothing the chromatograms.")
            
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
            "set_x_range": self.set_x_range,
            "set_y_range": self.set_y_range,
            "do_smoothing": self.do_smoothing,
            "smoothing_dict": self.smoothing_dict,
        }