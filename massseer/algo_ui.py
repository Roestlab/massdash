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

class AlgorithmUISettings:
    """
    A class to manage the user interface settings for the MassSeer algorithm.

    Attributes:
    -----------
    do_peak_picking : str
        The peak picking method to use.
    do_consensus_chrom : str
        The consensus chromatogram generation method to use.
    scale_intensity : bool
        Whether to scale the intensity of the chromatograms.
    consensus_chrom_mode : str
        The aggregation method to use for generating the consensus chromatogram.
    percentile_start : float
        The starting percentile for the percentile average aggregation method.
    percentile_end : float
        The ending percentile for the percentile average aggregation method.
    threshold : float
        The threshold for the percentile average aggregation method.
    auto_threshold : bool
        Whether to automatically compute the percentile threshold for the percentile average aggregation method.
    """

    def __init__(self, massseer_gui):
        self.massseer_gui = massseer_gui

        self.do_peak_picking = 'none'
        self.do_consensus_chrom = 'none'
        self.scale_intensity = False
        self.consensus_chrom_mode = None
        self.percentile_start = None
        self.percentile_end = None
        self.threshold = 0
        self.auto_threshold = True
    
    def create_ui(self, plot_settings):
        """
        Creates the user interface for setting the algorithm parameters.
        """
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


        ## Make a consensus chromatogram
        self.do_consensus_chrom = st.sidebar.selectbox("Generate Consensus Chromatogram", ['none', 'run-specific', 'global'])
        self.scale_intensity = st.sidebar.checkbox("Scale Intensity", value=False)

        if self.do_consensus_chrom != 'none':
            self.consensus_chrom_mode = st.sidebar.selectbox("Select aggregation method", ['averaged', 'median', 'percentile_average'])

            ## Average the chromatograms
            if self.consensus_chrom_mode == 'percentile_average':
                self.auto_threshold = st.sidebar.checkbox("Auto-Compute Percentile Threshold", value=True)

                if not self.auto_threshold:
                    self.percentile_start = st.sidebar.number_input('Percentile start', value=25.00, min_value=0.00, max_value=100.00, step=0.01)
                    self.percentile_end = st.sidebar.number_input('Percentile end', value=90.00, min_value=0.00, max_value=100.00, step=0.01)
                    self.threshold = st.sidebar.number_input('Threshold', value=0.00, min_value=0.00, max_value=1000000.00, step=0.01)
                else:
                    self.percentile_start = st.sidebar.number_input('Percentile start', value=99.9, min_value=0.00, max_value=100.00, step=0.01)
                    self.percentile_end = 100
                    self.threshold = 0
            else:
                self.percentile_end = None
                self.percentile_start = None
                self.threshold = 0
                self.auto_threshold = None
        else:
            self.consensus_chrom_mode = None
            self.percentile_end = None
            self.percentile_start = None
            self.threshold = 0
            self.auto_threshold = None

    def get_settings(self):
        """
        Returns the current algorithm settings as a dictionary.
        """
        return {
            "do_peak_picking": self.do_peak_picking,
            "do_consensus_chrom": self.do_consensus_chrom,
            "scale_intensity": self.scale_intensity,
            "consensus_chrom_mode": self.consensus_chrom_mode,
            "percentile_start": self.percentile_start,
            "percentile_end": self.percentile_end,
            "threshold": self.threshold,
            "auto_threshold": self.auto_threshold,
        }

