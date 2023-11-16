import streamlit as st

class ConcensusChromatogramUISettings:
    def __init__(self):
        """
        Initializes the ConcensusChromatogramUISettings class.
        """
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
        st.sidebar.divider()
        st.sidebar.title("Chromatgoram Transformations")
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