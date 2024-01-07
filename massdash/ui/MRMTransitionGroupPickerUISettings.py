import streamlit as st

# UI
from .ChromatogramPlotUISettings import ChromatogramPlotUISettings


class MRMTransitionGroupPickerUISettings:
    """
    Settings for the user interface of the MRMTransitionGroupPicker algorithm.

    Attributes:
    main_peak_picking_settings : PeakPickingSettings
        The peak picking settings for the main chromatogram.
    mslevels : str
        The MS levels to consider for peak picking. Possible values are "ms1", "ms2", and "ms1ms2".
    smoother : str
        The smoothing method to use. Possible values are "original", "gauss", and "sgolay".
    sgolay_frame_length : int
        The frame length of the Savitzky-Golay filter, if `smoother` is "sgolay".
    sgolay_polynomial_order : int
        The polynomial order of the Savitzky-Golay filter, if `smoother` is "sgolay".
    gauss_width : float
        The width of the Gaussian filter, if `smoother` is "gauss".
        
    Methods:
    create_ui : None
        Creates the user interface for the MRMTransitionGroupPicker app.
    """

    def __init__(self, main_peak_picking_settings) -> None:
        """
        Initializes a new instance of the MRMTransitionGroupPickerUISettings class.

        Args:
        main_peak_picking_settings : PeakPickingSettings
            The peak picking settings for the main chromatogram.
        """
        self.main_peak_picking_settings = main_peak_picking_settings
        self.mslevels = "ms2"
        self.smoother = "sgolay"
        self.sgolay_frame_length = 11
        self.sgolay_polynomial_order = 3
        self.gauss_width = 30.0

    def create_ui(self, plot_settings: ChromatogramPlotUISettings):
        """
        Creates the user interface for the MRMTransitionGroupPicker app.

        Args:
        plot_settings : ChromatogramPlotUISettings
            The plot settings for the chromatogram.
        """
        if not self.main_peak_picking_settings.peak_pick_on_displayed_chrom:
            with st.sidebar.expander("Advanced Settings"):
                self.mslevels = st.selectbox("MS Levels", ["ms1", "ms2","ms1ms2"], index=1, help="MS levels to consider for peak picking.")
                self.smoother = st.selectbox("Smoothing", ["original", "gauss", "sgolay"], index=2, help="Smoothing method to use.")
                if self.smoother == "gauss":
                    self.gauss_width = st.number_input("Width of the Gaussian smoothing", min_value=0.0, value=30.0, help="Width of the Gaussian smoothing.")
                elif self.smoother == "sgolay":
                    self.sgolay_frame_length = st.number_input("Savitzky-Golay Frame Length", value=11, step=2, min_value=1, help="Savitzky-Golay frame length.")
                    self.sgolay_polynomial_order = st.number_input("Savitzky-Golay Polynomial Order", value=3, min_value=1, help="Savitzky-Golay polynomial order.")
        else:
            self.smoother = plot_settings.do_smoothing
            if self.smoother == "gauss":
                self.gauss_width = st.number_input("Width of the Gaussian smoothing", min_value=0.0, value=30.0, help="Width of the Gaussian smoothing.")
            elif self.smoother == "sgolay":
                self.sgolay_frame_length = plot_settings.smoothing_dict['sgolay_frame_length']
                self.sgolay_polynomial_order = plot_settings.smoothing_dict['sgolay_polynomial_order']
