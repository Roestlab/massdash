import streamlit as st

from massseer.ui.ChromatogramPlotUISettings import ChromatogramPlotUISettings
from massseer.ui.pyPeakPickerMRMUISettings import pyPeakPickerMRMUISettings
from massseer.ui.MRMTransitionGroupPickerUISettings import MRMTransitionGroupPickerUISettings

class PeakPickingUISettings:
    """
    A class representing the peak picking settings for the MassSeerGUI.

    Attributes:
    -----------
    massseer_gui : MassSeerGUI
        The MassSeerGUI instance associated with these peak picking settings.
    do_peak_picking : str
        The type of peak picking to perform. Defaults to 'none'.
    peak_pick_on_displayed_chrom : bool
        Whether to perform peak picking on the displayed chromatogram. Defaults to True.
    mslevels : str
        The MS levels to perform peak picking on. Defaults to 'ms2'.
    PeakPickerMRMParams : PeakPickerMRM_UI
        The peak picking parameters for MRM scans.
    smoother : str
        The type of smoothing to perform. Defaults to 'sgolay'.
    sgolay_frame_length : int
        The frame length for Savitzky-Golay smoothing. Defaults to 11.
    sgolay_polynomial_order : int
        The polynomial order for Savitzky-Golay smoothing. Defaults to 3.
    gauss_width : float
        The width of the Gaussian smoothing. Defaults to 30.0.
    """
    def __init__(self, massseer_gui):
        self.massseer_gui = massseer_gui

        self.do_peak_picking = 'none'
        self.peak_pick_on_displayed_chrom = True
        self.peak_picker_algo_settings = None
            
    def create_ui(self, plot_settings: ChromatogramPlotUISettings):
        """
        Creates the user interface for setting the algorithm parameters.
        """
        st.sidebar.divider()
        st.sidebar.title("Peak Picking")

        ## Perform Peak Picking
        self.do_peak_picking = st.sidebar.selectbox("Peak Picking", ['none', 'OSW-PyProphet', 'pyPeakPickerMRM', 'MRMTransitionGroupPicker'], help="Peak picking method to use.")

        if self.do_peak_picking != 'none':
            ## Perform peak picking on displayed chromatogram, or adjust smoothing separately for peak picking?
            self.peak_pick_on_displayed_chrom = st.sidebar.checkbox("Peak Pick with Displayed Chromatogram", value=True, help="If checked, peak picking will be performed on the displayed chromatogram. If unchecked, peak picking will be performed on the raw chromatogram or you set different smoothing parameters for peak picking.") 

        if self.do_peak_picking == "pyPeakPickerMRM":
            self.peak_picker_algo_settings = pyPeakPickerMRMUISettings(self)
            self.peak_picker_algo_settings.create_ui(plot_settings)
        elif self.do_peak_picking == "OSW-PyProphet":
            pass
        elif self.do_peak_picking == "MRMTransitionGroupPicker":
            self.peak_picker_algo_settings = MRMTransitionGroupPickerUISettings(self)
            self.peak_picker_algo_settings.create_ui(plot_settings)

    def get_settings(self):
        """
        Returns the current algorithm settings as a dictionary.
        """
        return {
            "do_peak_picking": self.do_peak_picking,
            "peak_pick_on_displayed_chrom": self.peak_pick_on_displayed_chrom
        }

