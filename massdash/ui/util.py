"""
massdash/ui/util
~~~~~~~~~~~~~~~~
"""

from os import getcwd
from os.path import dirname
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

def get_parent_directory(input_file: str=None):
    """
    Get the parent directory of a file, if no file is provided, the current working directory is returned.

    Args:
        input_file (str): The path to the feature file.

    Returns:
        str: The parent directory.
    """
    if input_file is None:
        parent_dir = getcwd()
    else:
        parent_dir = dirname(input_file)
    return parent_dir

def tk_file_dialog(file_type: list = [], title: str = "Select File", parent_dir: str = getcwd()):
    """
    Creates a Tkinter file dialog for selecting a file.

    Args:
        file_type (list): List of tuples specifying file types and their corresponding extensions.
                           Example: [("Text files", "*.txt"), ("CSV files", "*.csv")]
        title (str): The title of the file dialog.
        parent_dir (str): The path to the parent directory of the file dialog.

    Returns:
        str: The path to the selected file.
    """
    root = Tk()
    root.withdraw()
    file_type.extend([("All files", "*.*")])
    file_path = filedialog.askopenfilename(filetypes=file_type, title=title, initialdir=parent_dir)
    root.destroy()
    return file_path


def display_input_section(title, key_base: str, file_extension: str, dialog_title: str, placeholder: str, st_cols = None):
    """
    Display an input section with a title, file browsing button, and text input field.

    Parameters:
        title (str): The title of the input section.
        key_base (str): The base key used for storing session state variables
        file_extension (str): The file extension to filter when browsing for files.
        dialog_title (str): The title of the file browsing dialog.
        placeholder (str): The placeholder text for the text input field.
        st_cols (streamlit.columns): The columns to display the input section in.

    Returns:
        str: The value entered in the text input field.
    """
    st.subheader(title)
    if st_cols is None:
        st_cols = st.columns([0.05, 0.95], gap="small")
    with st_cols[0]:
        st.write("\n")
        st.write("\n")
        dialog_button = st.button("📁", key=f'{key_base}_browse', help=f"Browse for the {title} file.")
        if dialog_button:
            st.session_state.tmp_input_dict[key_base] = tk_file_dialog(file_extension, dialog_title, get_parent_directory(st.session_state.tmp_input_dict[key_base]))    
    with st_cols[1]:
        input_value = st.text_input("Enter file path", value=st.session_state.tmp_input_dict[key_base],
                                    placeholder=placeholder, key=f'{key_base}_tmp',
                                    help=f"Path to the {title} file ({file_extension})")
    return input_value
