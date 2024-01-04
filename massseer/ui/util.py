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
    
def st_mutable_write(text=None):
    """
    Creates a mutable container that can be updated with text.
    
    Args:
        text (str): The text to be written to the container.
        
    Returns:
        st.empty(): The mutable container.
    """
    write_container = st.empty()
    if text is not None:
        write_container.write(text)
    return write_container