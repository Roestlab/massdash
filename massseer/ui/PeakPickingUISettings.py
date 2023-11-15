import streamlit as st
import pyopenms as po

class PeakPickerMRM_UI:
    def __init__(self) -> None:
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
    
    def print_peak_picker_params(self):
        peak_picker_params = self.peak_picker.getParameters()
        parameter_dict = {key: peak_picker_params.getValue(key) for key in peak_picker_params.keys()}
        print("*"*75)
        print("\tPeakPickerMRM Parameters:")
        print("*"*75)
        for key, value in parameter_dict.items():
            print(f"{key.decode('utf-8')}: {value}")
        print("*"*75)

class PeakPickingUISettings:
    """
    A class to manage the user interface settings for the MassSeer algorithm.

    Attributes:
    -----------
    do_peak_picking : str
        The peak picking method to use.
    """

    def __init__(self, massseer_gui):
        self.massseer_gui = massseer_gui

        self.do_peak_picking = 'none'
        self.peak_pick_on_displayed_chrom = True
        self.PeakPickerMRMParams = PeakPickerMRM_UI()
    
    def create_ui(self, plot_settings):
        """
        Creates the user interface for setting the algorithm parameters.
        """
        st.sidebar.divider()
        st.sidebar.title("Peak Picking")
        ## Perform Peak Picking
        self.do_peak_picking = st.sidebar.selectbox("Peak Picking", ['none', 'OSW-PyProphet', 'PeakPickerMRM'])
        if self.do_peak_picking != 'none':
            ## Perform peak picking on displayed chromatogram, or adjust smoothing separately for peak picking?
            self.peak_pick_on_displayed_chrom = st.sidebar.checkbox("Peak Pick with Displayed Chromatogram", value=True) 

        if self.do_peak_picking == "PeakPickerMRM":
            if not self.peak_pick_on_displayed_chrom:
                with st.sidebar.expander("Advanced Settings"):
                    self.PeakPickerMRMParams = PeakPickerMRM_UI()
                    # Check to use Gaussian smoothing
                    self.PeakPickerMRMParams.use_gauss = st.checkbox("Use Gaussian Smoothing", value=False) 
                    if self.PeakPickerMRMParams.use_gauss:      
                        # Gaussian Width
                        self.PeakPickerMRMParams.gauss_width = st.number_input("Width of the Gaussian smoothing", min_value=0.0, value=30.0)
                    else:
                        # Widget for sgolay_frame_length
                        self.PeakPickerMRMParams.sgolay_frame_length = st.number_input("Savitzky-Golay Frame Length", value=11, step=2, min_value=1)

                        # Widget for sgolay_polynomial_order
                        self.PeakPickerMRMParams.sgolay_polynomial_order = st.number_input("Savitzky-Golay Polynomial Order", value=3, min_value=1)

                    # Widget for peak_width
                    self.PeakPickerMRMParams.peak_width = st.number_input("Minimum Peak Width (seconds)", value=-1.0, step=1.0)

                    # Widget for signal_to_noise
                    self.PeakPickerMRMParams.signal_to_noise = st.number_input("Signal-to-Noise Threshold", value=1.0, step=0.1, min_value=0.0)

                    # Widget for sn_win_len
                    self.PeakPickerMRMParams.sn_win_len = st.number_input("Signal-to-Noise Window Length", value=1000.0, step=10.0)

                    # Widget for sn_bin_count
                    self.PeakPickerMRMParams.sn_bin_count = st.number_input("Signal-to-Noise Bin Count", value=30, step=1, min_value=1)

                    # Widget for remove_overlapping_peaks
                    self.PeakPickerMRMParams.remove_overlapping_peaks = st.selectbox("Remove Overlapping Peaks", ['true', 'false'])

                    # Widget for method
                    self.PeakPickerMRMParams.method = st.selectbox("Peak Picking Method", ['legacy', 'corrected'], index=1)
            else:
                self.PeakPickerMRMParams = PeakPickerMRM_UI()

                if plot_settings.do_smoothing == "gauss":      
                    # Gaussian Width
                    self.PeakPickerMRMParams.gauss_width = st.number_input("Width of the Gaussian smoothing", min_value=0.0, value=30.0)
                elif plot_settings.do_smoothing == "sgolay":
                    # Widget for sgolay_frame_length
                    self.PeakPickerMRMParams.sgolay_frame_length = plot_settings.smoothing_dict['sgolay_frame_length']

                    # Widget for sgolay_polynomial_order
                    self.PeakPickerMRMParams.sgolay_polynomial_order = plot_settings.smoothing_dict['sgolay_polynomial_order']

                # Set/Update PeakPickerMRM paramters
                self.PeakPickerMRMParams.set_peak_picker_params()
        elif self.do_peak_picking == "OSW-PyProphet":
            print(self.massseer_gui.osw_file_path)

    def get_settings(self):
        """
        Returns the current algorithm settings as a dictionary.
        """
        return {
            "do_peak_picking": self.do_peak_picking,
            "peak_pick_on_displayed_chrom": self.peak_pick_on_displayed_chrom,
            "PeakPickerMRMParams": self.PeakPickerMRMParams
        }

