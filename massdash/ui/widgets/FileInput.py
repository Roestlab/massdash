import os
import tempfile
import streamlit as st

# UI Utils
from ..util import get_parent_directory, tk_file_dialog, display_input_section
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

    def create_ui(self, type="regular", entry_number=0, feature_file_path_entry=None):
        """
        Creates the user interface for the file input widget.

        Returns:
            str: The path to the selected file.
        """
        if TKINTER_AVAILABLE:
            if type == "search_results_analysis":
                with self.st_cols[0]:
                    st.write("\n")
                    st.write("\n\n\n\n")
                    dialog_button = st.button("📁", key=f'search_results_browser_{entry_number}', help=f"Browse for the search results file.")
                    if dialog_button:
                        parent_dir = get_parent_directory(st.session_state.tmp_input_dict[feature_file_path_entry])
                        st.session_state.tmp_input_dict[feature_file_path_entry] = tk_file_dialog(file_type=[("OpenSwath Files", ".osw"), ("Feature File", ".tsv")], title="Select Feature File", parent_dir=parent_dir)
                
                file_path = self.st_cols[1].text_input("Enter file path", value=st.session_state.tmp_input_dict[feature_file_path_entry], placeholder="*.osw / *.tsv", key=f"search_results_{entry_number}", help="Path to the  search results file (*.osw / *.tsv)")
            else:
                file_path = display_input_section(self.title, self.key_base, [(self.placeholder, self.file_extension)], self.dialog_title, self.file_extension, st_cols=self.st_cols)
            return file_path
        else:
            if self.st_cols is None:
                self.st_cols = st
            elif len(self.st_cols) > 1:
                self.st_cols = self.st_cols[1]
            # Create a streamlit file dialog
            uploaded_file = self.st_cols.file_uploader(self.title, key=f"{self.title}_entry_{entry_number}", help=f"Path to the {self.title} file ({self.file_extension})")
            if uploaded_file:
                temp_dir = tempfile.mkdtemp()
                file_path = os.path.join(temp_dir, uploaded_file.name)
                with open(file_path, "wb") as f:
                        f.write(uploaded_file.getvalue())
                return file_path