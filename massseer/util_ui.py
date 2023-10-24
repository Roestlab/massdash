import streamlit as st

def clicked(button):
    """
    Updates the session state to indicate that a button has been clicked.

    Args:
        button (str): The name of the button that was clicked.

    Returns:
        None
    """
    st.session_state.clicked[button] = True


def show_welcome_message():
    """
    Displays a welcome message and input fields for OpenSwath and DIA-NN workflows.

    Returns:
    welcome_container (streamlit.container): A container for the welcome message.
    load_toy_dataset (streamlit.button): A button to load the OpenSwath example dataset.
    osw_file_path (streamlit.text_input): A text input field for the OpenSwath file path.
    sqmass_file_path_input (streamlit.text_input): A text input field for the sqMass file path.
    """
    # Add a welcome message
    welcome_container = st.empty()
    with welcome_container:
        with st.container():
            st.title("Welcome to MassSeer!")
            st.write("MassSeer is a powerful platform designed for researchers and analysts in the field of mass spectrometry.")
            st.write("It enables the visualization of chromatograms, algorithm testing, and parameter optimization, crucial for data analysis and experimental design.")
            st.write("This tool is an indispensable asset for researchers and laboratories working with DIA (Data-Independent Acquisition) data.")

            # Tabs for different data workflows
            tab1, tab2 = st.tabs(["OpenSwath", "DIA-NN"])
            with tab1:
                st.subheader("OpenSwath")

                load_toy_dataset = st.button('Load OpenSwath Example', on_click=clicked , args=['load_toy_dataset'])
                st.title("Input OSW file")
                osw_file_path = st.text_input("Enter file path", "*.osw", key='osw_file_path_tmp')

                st.title("Input sqMass file")
                sqmass_file_path_input = st.text_input("Enter file path", "*.sqMass", key='sqmass_file_path_input_tmp')

    return welcome_container, load_toy_dataset, osw_file_path, sqmass_file_path_input
