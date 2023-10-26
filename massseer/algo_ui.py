import streamlit as st

def algo_ui_widgets():
    """
    This function creates UI widgets for the MassSeer algorithm. It allows the user to select peak picking options, 
    generate consensus chromatograms, and scale intensity. If the user selects to generate a consensus chromatogram, 
    they can choose the aggregation method and set the percentile threshold. 

    Returns:
    - do_peak_picking (bool): Whether or not to perform peak picking.
    - do_consensus_chrom (bool): whether or not to generate a consensus chromatogram.
    - scale_intensity (bool): Whether or not to scale intensity.
    - consensus_chrom_mode (str): The aggregation method selected by the user.
    - percentile_start (float): The starting percentile threshold selected by the user.
    - percentile_end (float): The ending percentile threshold selected by the user.
    - auto_threshold (bool): Whether or not to auto-compute the percentile threshold.
    """
    # Perform Peak Picking
    do_peak_picking = st.sidebar.selectbox("Peak Picking", ['none', 'PeakPickerMRM'])

    ## Make a consensus chromatogram
    do_consensus_chrom = st.sidebar.selectbox("Generate Consensus Chromatogram", ['none', 'run-specific', 'global'])
    scale_intensity = st.sidebar.checkbox("Scale Intensity", value=False)

    if do_consensus_chrom != 'none':
        consensus_chrom_mode = st.sidebar.selectbox("Select aggregation method", ['averaged', 'median', 'percentile_average'])

        ## Average the chromatograms
        if consensus_chrom_mode == 'percentile_average':
            auto_threshold = st.sidebar.checkbox("Auto-Compute Percentile Threshold", value=True)
            
            if not auto_threshold:
                percentile_start=st.sidebar.number_input('Percentile start', value=25.00, min_value=0.00, max_value=100.00, step=0.01)
                percentile_end=st.sidebar.number_input('Percentile end', value=90.00, min_value=0.00, max_value=100.00, step=0.01) 
                threshold=st.sidebar.number_input('Threshold', value=0.00, min_value=0.00, max_value=1000000.00, step=0.01)
            else: 
                percentile_start=st.sidebar.number_input('Percentile start', value=99.9, min_value=0.00, max_value=100.00, step=0.01)
                percentile_end = 100
                threshold=0
        else:
            percentile_end = None
            percentile_start = None
            threshold= 0
            auto_threshold = None
    else: 
        consensus_chrom_mode = None
        percentile_end = None
        percentile_start = None
        threshold= 0
        auto_threshold = None
    return do_peak_picking, do_consensus_chrom, scale_intensity, consensus_chrom_mode, percentile_start, percentile_end, threshold, auto_threshold