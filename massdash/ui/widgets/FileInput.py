import os
import tempfile
import streamlit as st

# UI Utils
from ..util import display_input_section
# Utils
from ...util import check_package

Tk, filedialog, TKINTER_AVAILABLE = check_package("tkinter", ["Tk", "filedialog"])

class FileInput():
    def __init__(self, title, key_base: str, file_extension: str, dialog_title: str, placeholder: str, st_cols = None):
        """
        Creates a file input widget.

        Args:
            title (str): The title of the widget.
            key_base (str): The key base for the widget.
            file_extension (str): The file extension to filter for.
            dialog_title (str): The title of the file dialog.
            placeholder (str): The placeholder text for the file input.
            st_cols (int): The number of columns for the file input widget.
        """
        self.title = title
        self.key_base = key_base
        self.file_extension = file_extension
        self.dialog_title = dialog_title
        self.placeholder = placeholder
        self.st_cols = st_cols

    def create_ui(self):
        """
        Creates the user interface for the file input widget.

        Returns:
            str: The path to the selected file.
        """
        if TKINTER_AVAILABLE:
            file_path = display_input_section(self.title, self.key_base, [(self.placeholder, self.file_extension)], self.dialog_title, self.file_extension, st_cols=self.st_cols)
            return file_path
        else:
            # Create a streamlit file dialog
            uploaded_file = st.file_uploader(self.title, help=f"Path to the {self.title} file ({self.file_extension})")
            if uploaded_file:
                temp_dir = tempfile.mkdtemp()
                file_path = os.path.join(temp_dir, uploaded_file.name)
                with open(file_path, "wb") as f:
                        f.write(uploaded_file.getvalue())
                return file_path