"""
massdash/ui/pyPeakPickerMRMUISettings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import streamlit as st
import pyopenms as po

# UI
from massdash.ui.ChromatogramPlotUISettings import ChromatogramPlotUISettings

class pyPeakPickerMRMUISettings:
    """
    A class representing the python based PeakPickerMRM peak picking UI settings for the MassDashGUI.
    
    Attributes:
        main_peak_picking_settings : PeakPickingSettings
            The peak picking settings for the main chromatogram.
        mslevels : str
            The MS levels to consider for peak picking. Possible values are "ms1", "ms2", and "ms1ms2".
        PeakPickerMRMParams : PeakPickerMRM_UI
            The peak picking parameters for the pyOpenMS PeakPickerMRM algorithm.
            
    Methods:
        create_ui : None
            Creates the user interface for the pyPeakPickerMRMUISettings.
    """
    def __init__(self, main_peak_picking_settings):
        """
        Initializes the pyPeakPickerMRMUISettings class.
        
        Args:
            main_peak_picking_settings : PeakPickingSettings
                The peak picking settings for the main chromatogram.
        """
        self.main_peak_picking_settings = main_peak_picking_settings
        self.mslevels = "ms2"
        self.PeakPickerMRMParams = PeakPickerMRM_UI()

    def create_ui(self, plot_settings: ChromatogramPlotUISettings):
        """
        Creates the user interface for setting the algorithm parameters.
        
        Args:
            plot_settings : ChromatogramPlotUISettings
                The plot settings for the chromatogram.
        """
        if not self.main_peak_picking_settings.peak_pick_on_displayed_chrom:
            with st.sidebar.expander("Advanced Settings"):
                self.mslevels = st.selectbox("MS Levels", ["ms1", "ms2","ms1ms2"], index=1, help="MS levels to consider for peak picking.")
                self.PeakPickerMRMParams = PeakPickerMRM_UI()
                # Check to use Gaussian smoothing
                self.PeakPickerMRMParams.use_gauss = st.checkbox("Use Gaussian Smoothing", value=False, help="If checked, Gaussian smoothing will be used. If unchecked, Savitzky-Golay smoothing will be used.") 
                if self.PeakPickerMRMParams.use_gauss:      
                    # Gaussian Width
                    self.PeakPickerMRMParams.gauss_width = st.number_input("Width of the Gaussian smoothing", min_value=0.0, value=30.0, help="Width of the Gaussian smoothing.")
                else:
                    # Widget for sgolay_frame_length
                    self.PeakPickerMRMParams.sgolay_frame_length = st.number_input("Savitzky-Golay Frame Length", value=11, step=2, min_value=1, help="Savitzky-Golay frame length.")

                    # Widget for sgolay_polynomial_order
                    self.PeakPickerMRMParams.sgolay_polynomial_order = st.number_input("Savitzky-Golay Polynomial Order", value=3, min_value=1, help="Savitzky-Golay polynomial order.")

                # Widget for peak_width
                self.PeakPickerMRMParams.peak_width = st.number_input("Minimum Peak Width (seconds)", value=-1.0, step=1.0, help="Minimum peak width in seconds. If -1, the peak width is estimated from the signal-to-noise ratio. If 0, the peak width is estimated from the peak shape. If > 0, the peak width is fixed to the given value.")

                # Widget for signal_to_noise
                self.PeakPickerMRMParams.signal_to_noise = st.number_input("Signal-to-Noise Threshold", value=1.0, step=0.1, min_value=0.0, help="Signal-to-noise threshold. Peaks with a signal-to-noise ratio below this threshold are discarded.")

                # Widget for sn_win_len
                self.PeakPickerMRMParams.sn_win_len = st.number_input("Signal-to-Noise Window Length", value=1000.0, step=10.0, help="Signal-to-noise window length in seconds. The signal-to-noise ratio is computed in a window of this length.")

                # Widget for sn_bin_count
                self.PeakPickerMRMParams.sn_bin_count = st.number_input("Signal-to-Noise Bin Count", value=30, step=1, min_value=1, help="Signal-to-noise bin count. The signal-to-noise ratio is computed in a window of sn_win_len seconds. The window is divided into sn_bin_count bins and the maximum intensity in each bin is determined. The signal-to-noise ratio is then computed as the mean of these maximum intensities.")

                # Widget for remove_overlapping_peaks
                self.PeakPickerMRMParams.remove_overlapping_peaks = st.selectbox("Remove Overlapping Peaks", ['true', 'false'], help="If true, overlapping peaks are removed. If false, overlapping peaks are not removed.")

                # Widget for method
                self.PeakPickerMRMParams.method = st.selectbox("Peak Picking Method", ['legacy', 'corrected'], index=1, help="Peak picking method. The legacy method is the original implementation. The corrected method is a corrected version of the legacy method. The corrected method is recommended.")
        else:
            self.PeakPickerMRMParams = PeakPickerMRM_UI()

            if plot_settings.do_smoothing == "gauss":      
                # Gaussian Width
                self.PeakPickerMRMParams.gauss_width = st.number_input("Width of the Gaussian smoothing", min_value=0.0, value=30.0, help="Width of the Gaussian smoothing.")
            elif plot_settings.do_smoothing == "sgolay":
                # Widget for sgolay_frame_length
                self.PeakPickerMRMParams.sgolay_frame_length = plot_settings.smoothing_dict['sgolay_frame_length']

                # Widget for sgolay_polynomial_order
                self.PeakPickerMRMParams.sgolay_polynomial_order = plot_settings.smoothing_dict['sgolay_polynomial_order']

            # Set/Update PeakPickerMRM paramters
            self.PeakPickerMRMParams.set_peak_picker_params()

class PeakPickerMRM_UI:
    """
    A class for setting peak picking parameters for pyOpenMS's PeakPickerMRM.

    Attributes:
    peak_picker : PeakPickerMRM object
        An instance of PeakPickerMRM class.
    use_gauss : bool
        A boolean indicating whether to use Gaussian smoothing.
    gauss_width : float
        The width of the Gaussian smoothing window.
    sgolay_frame_length : int
        The length of the Savitzky-Golay filter window.
    sgolay_polynomial_order : int
        The order of the polynomial used in the Savitzky-Golay filter.
    peak_width : float
        The width of the peak.
    signal_to_noise : float
        The signal-to-noise ratio.
    sn_win_len : float
        The length of the signal-to-noise window.
    sn_bin_count : int
        The number of bins used in the signal-to-noise calculation.
    remove_overlapping_peaks : str
        A string indicating whether to remove overlapping peaks.
    method : str
        A string indicating the method used for peak picking.
        
    Methods:
    set_peak_picker_params : PeakPickerMRM_UI object
        Set peak picking parameters for PeakPickerMRM.
    __str__ : str
        Return a string representation of the PeakPickerMRM parameters.
    """
    def __init__(self) -> None:
        """
        Initializes the PeakPickerMRM_UI class.
        """
        self.peak_picker = po.PeakPickerMRM()
        self.use_gauss = False
        self.gauss_width = 30.0
        self.sgolay_frame_length = 11
        self.sgolay_polynomial_order = 3
        self.peak_width = -1.0
        self.signal_to_noise = 1.0
        self.sn_win_len = 1000.0
        self.sn_bin_count = 30
        self.remove_overlapping_peaks = 'false'
        self.method = 'corrected'
    
    def set_peak_picker_params(self):
        """
        Set peak picking parameters for PeakPickerMRM.

        Returns:
        self : PeakPickerMRM_UI object
            Returns the instance of the PeakPickerMRM_UI class.
        """
        peak_picker_params = self.peak_picker.getParameters()
        peak_picker_params.setValue(b'gauss_width', self.gauss_width)
        peak_picker_params.setValue(b'use_gauss', 'true' if self.use_gauss else 'false')
        peak_picker_params.setValue(b'sgolay_frame_length', self.sgolay_frame_length)
        peak_picker_params.setValue(b'sgolay_polynomial_order', self.sgolay_polynomial_order)
        peak_picker_params.setValue(b'peak_width', self.peak_width)
        peak_picker_params.setValue(b'signal_to_noise', self.signal_to_noise)
        peak_picker_params.setValue(b'sn_win_len', self.sn_win_len)
        peak_picker_params.setValue(b'sn_bin_count', self.sn_bin_count)
        peak_picker_params.setValue(b'remove_overlapping_peaks', self.remove_overlapping_peaks)
        peak_picker_params.setValue(b'method', self.method)
        self.peak_picker.setParameters(peak_picker_params)

        return self
    
    def __str__(self):
        """
        Return a string representation of the PeakPickerMRM parameters.

        Returns:
        --------
        output : str
            A string representation of the PeakPickerMRM parameters.
        """
        peak_picker_params = self.peak_picker.getParameters()
        parameter_dict = {key: peak_picker_params.getValue(key) for key in peak_picker_params.keys()}
        output = ""
        output += "*"*75 + "\n"
        output += "\tPeakPickerMRM Parameters:\n"
        output += "*"*75 + "\n"
        for key, value in parameter_dict.items():
            output += f"{key.decode('utf-8')}: {value}\n"
        output += "*"*75 + "\n"
        return output