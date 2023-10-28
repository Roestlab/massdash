import streamlit as st

def chromatogram_plotting_settings():
    """
    This function creates a sidebar with plotting settings for chromatograms. It includes checkboxes to include MS1 and/or MS2 traces, and an expander with advanced settings. The advanced settings include checkboxes for setting x-range and y-range, and a selectbox for smoothing the chromatograms. If sgolay smoothing is selected, it creates two columns for side-by-side widgets to set the polynomial order and frame length.
    
    Returns:
    include_ms1 (bool): Whether to include MS1 traces in the plot.
    include_ms2 (bool): Whether to include MS2 traces in the plot.
    set_x_range (bool): Whether to set a custom x-range for the plot.
    set_y_range (bool): Whether to set a custom y-range for the plot.
    do_smoothing (str): The type of smoothing to perform on the chromatograms ('sgolay' or 'none').s
    smoothing_dict (dict): A dictionary with the smoothing settings.
    """
    smoothing_dict = {}

    st.sidebar.title("Plotting Settings")
    # Add checkboxes in the sidebar to include MS1 and/or MS2 traces
    include_ms1 = st.sidebar.checkbox("Include MS1 Traces", value=True)
    include_ms2 = st.sidebar.checkbox("Include MS2 Traces", value=True)

    with st.sidebar.expander("Advanced Settings"):

        # Add Checkboxes for setting x-range and y-range
        set_x_range = st.checkbox("Set x-range", value=False)
        set_y_range = st.checkbox("Set y-range", value=False)

        # Perform Smoothing of the chromatograms
        do_smoothing = st.selectbox("Smoothing", ['sgolay', 'none'])
        
        smoothing_dict['type'] = do_smoothing
        if do_smoothing == 'sgolay':
            # Create two columns for side-by-side widgets
            col1, col2 = st.columns(2)

            # Add widget for sgolay_polynomial_order in the first column
            sgolay_polynomial_order = col1.number_input("Polynomial Order", min_value=1, max_value=10, value=3, step=1)

            # Add widget for sgolay_frame_length in the second column
            sgolay_frame_length = col2.number_input("Frame Length", min_value=1, max_value=50, value=11, step=1)

            smoothing_dict['sgolay_polynomial_order'] = sgolay_polynomial_order
            smoothing_dict['sgolay_frame_length'] = sgolay_frame_length
    return include_ms1, include_ms2, set_x_range, set_y_range, do_smoothing,  smoothing_dict

