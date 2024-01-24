"""
massdash/ui/PeakPickingUISettings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import streamlit as st

# UI
from .ChromatogramPlotUISettings import ChromatogramPlotUISettings
from .pyPeakPickerMRMUISettings import pyPeakPickerMRMUISettings
from .ConformerPickerUISettings import ConformerPickerUISettings
from .MRMTransitionGroupPickerUISettings import MRMTransitionGroupPickerUISettings

class PeakPickingUISettings:
    """
    A class representing the peak picking settings for the MassDashGUI.

    Attributes:
    do_peak_picking : str
        The type of peak picking to perform. Defaults to 'none'.
    peak_pick_on_displayed_chrom : bool
        Whether to perform peak picking on the displayed chromatogram. Defaults to True.
    peak_picker_algo_settings : pyPeakPickerMRMUISettings/MRMTransitionGroupPickerUISettings
    
    Methods:
    create_ui : None
        Creates the user interface for the PeakPickingUISettings.
    gety_settings : dict
        Returns the current algorithm settings as a dictionary.
    """
    def __init__(self):
        self.do_peak_picking = 'none'
        self.peak_pick_on_displayed_chrom = True
        self.peak_picker_algo_settings = None
            
    def create_ui(self, plot_settings: ChromatogramPlotUISettings):
        """
        Creates the user interface for setting the algorithm parameters.
        
        Args:
        plot_settings : ChromatogramPlotUISettings
            The plot settings for the chromatogram.
        """
        st.sidebar.divider()
        st.sidebar.title("Peak Picking")

        ## Perform Peak Picking
        self.do_peak_picking = st.sidebar.selectbox("Peak Picking", ['none', 'Feature File Boundaries', 'pyPeakPickerMRM', 'MRMTransitionGroupPicker', 'Conformer'], help="Peak picking method to use.")

        if self.do_peak_picking != 'none':
            ## Perform peak picking on displayed chromatogram, or adjust smoothing separately for peak picking?
            self.peak_pick_on_displayed_chrom = st.sidebar.checkbox("Peak Pick with Displayed Chromatogram", value=True, help="If checked, peak picking will be performed on the displayed chromatogram. If unchecked, peak picking will be performed on the raw chromatogram or you set different smoothing parameters for peak picking.") 

        if self.do_peak_picking == "pyPeakPickerMRM":
            self.peak_picker_algo_settings = pyPeakPickerMRMUISettings(self)
            self.peak_picker_algo_settings.create_ui(plot_settings)
        elif self.do_peak_picking == "Feature File Boundaries":
            pass
        elif self.do_peak_picking == "MRMTransitionGroupPicker":
            self.peak_picker_algo_settings = MRMTransitionGroupPickerUISettings(self)
            self.peak_picker_algo_settings.create_ui(plot_settings)
        elif self.do_peak_picking == "Conformer":
            self.peak_picker_algo_settings = ConformerPickerUISettings(self)
            self.peak_picker_algo_settings.create_ui(plot_settings)

    def get_settings(self):
        """
        Returns the current algorithm settings as a dictionary.
        """
        return {
            "do_peak_picking": self.do_peak_picking,
            "peak_pick_on_displayed_chrom": self.peak_pick_on_displayed_chrom
        }

