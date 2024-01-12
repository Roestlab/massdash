"""
massdash/ui/util
~~~~~~~~~~~~~~~~
"""

import streamlit as st
from tkinter import Tk, filedialog

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

def tk_file_dialog(file_type: str=""):
    """
    Creates a Tkinter file dialog for selecting a file.
    
    Args:
        file_type (str): The file type to be selected.
        
    Returns:
        str: The path to the selected file.
    """
    root = Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=[(f"{file_type} files", file_type)] if file_type else [])
    root.destroy()
    return file_path

def display_input_section(title, key_base, file_extension, placeholder):
    """
    Display an input section with a title, file browsing button, and text input field.

    Parameters:
        title (str): The title of the input section.
        key_base (str): The base key used for storing session state variables
        file_extension (str): The file extension to filter when browsing for files.
        placeholder (str): The placeholder text for the text input field.

    Returns:
        str: The value entered in the text input field.
    """
    st.subheader(title)

    cols = st.columns([0.1, 1.9], gap="small")
    with cols[0]:
        st.write("\n")
        st.write("\n\n\n\n")
        dialog_button = st.button("Browse", key=f'{key_base}_browse', help=f"Browse for the {title} file.")
        if dialog_button:
            st.session_state.tmp_input_dict[key_base] = tk_file_dialog(file_extension)
    with cols[1]:
        input_value = st.text_input("Enter file path", value=st.session_state.tmp_input_dict[key_base],
                                    placeholder=placeholder, key=f'{key_base}_tmp',
                                    help=f"Path to the {title} file ({file_extension})")
        
    return input_value
