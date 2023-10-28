import streamlit as st

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

    def __init__(self):
        self.do_peak_picking = 'none'
        self.do_consensus_chrom = 'none'
        self.scale_intensity = False
        self.consensus_chrom_mode = None
        self.percentile_start = None
        self.percentile_end = None
        self.threshold = 0
        self.auto_threshold = True

    def create_ui(self):
        """
        Creates the user interface for setting the algorithm parameters.
        """
        # Perform Peak Picking
        self.do_peak_picking = st.sidebar.selectbox("Peak Picking", ['none', 'PeakPickerMRM'])

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

