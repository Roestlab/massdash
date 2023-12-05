import streamlit as st

import os
import fnmatch

from massseer.ui.BaseUISettings import BaseUISettings

class FileInputRawDataUISettings(BaseUISettings):
    """
    Class to create the user interface for the FileInputXICDataUISettings.
    
    Attributes:
        transition_list_file_path (streamlit.text_input): A text input field for the transition list file path.
        raw_file_path_input (streamlit.text_input): A text input field for the raw file path.
        feature_file_path (streamlit.text_input): A text input field for the search results output file path.
        raw_file_path_list (list): List of full file paths to *.mzML files in the directory or the file itself.
        threads (int): Number of threads to use for processing the files.
    
    Methods:
        create_ui: Creates the user interface for the FileInputXICDataUISettings.
        get_mzml_files: Given a path to a directory or a file, returns a list of full file paths to *.mzML files in the directory or the file itself.
    """
    def __init__(self) -> None:
        """
        Initializes the FileInputRawDataUISettings class.
        """
        self.transition_list_file_path = None
        self.raw_file_path_input = None
        self.feature_file_path = None 
        self.raw_file_path_list = None
        self.threads = None

    def create_ui(self, transition_list_file_path: str=None, raw_file_path: str=None, feature_file_path: str=None):
        """
        Creates the user interface for inputting file paths.

        Args:
            transition_list_file_path (str, optional): The file path for the transition list file. Defaults to None.
            raw_file_path (str, optional): The file path for the raw file. Defaults to None.
            feature_file_path (str, optional): The file path for the search results output file. Defaults to None.
        """
        st.sidebar.subheader("Input Transition List")
        self.transition_list_file_path = st.sidebar.text_input("Enter file path", transition_list_file_path, key='raw_data_transition_list', help="Path to the transition list file (*.pqp / *.tsv)")

        st.sidebar.subheader("Input Raw file")
        self.raw_file_path_input = st.sidebar.text_input("Enter file path", raw_file_path, key='raw_data_file_path', help="Path to the raw file (*.mzML)")

        # Tabs for different data workflows
        st.sidebar.subheader("Input Search Results")
        self.feature_file_path = st.sidebar.text_input("Enter file path", feature_file_path, key='feature_file_path', help="Path to the search results output file. Can be an Pyprophet scored OpenSwath file or a DIA-NN report file (*.osw / *.tsv)")

    def get_mzml_files(self, threads: int=1):
        """
        Given a path to a directory or a file, returns a list of full file paths to *.mzML files in the directory or the file itself.
        If the input path is a directory, the function displays a selection box in the sidebar to select the *.mzML files.
        If the input path is a file, the function returns a list containing only the input file path.
        The function also displays a slider to select the number of threads to use for processing the files.
        
        Parameters:
        raw_file_path_input (str): Path to a directory or a file
        
        Returns:
        raw_file_path_list (list): List of full file paths to *.mzML files in the directory or the file itself.
        threads (int): Number of threads to use for processing the files.
        """
        
        if os.path.isfile(self.raw_file_path_input):
            raw_file_path_list = [self.raw_file_path_input]
        else:
            # Check to ensure directory exists otherwise throw error
            if not os.path.isdir(self.raw_file_path_input):
                raise ValueError(f"Error: Directory {self.raw_file_path_input} does not exist!")
            
            # 1. Get the list of files in the directory
            files_in_directory = os.listdir(self.raw_file_path_input)
            
            #2. Filter the files based on the *.mzML file extension (case-insensitive)
            files_in_directory = [filename for filename in files_in_directory if fnmatch.fnmatch(filename.lower(), '*.mzml')]

            # 3. Sort the filenames alphabetically
            sorted_filenames = sorted(files_in_directory, reverse=False)
                
            st.sidebar.subheader(f"{len(sorted_filenames)} Raw file(s)")
            with st.sidebar.expander("File list"):
                # Create a selection box in the sidebar
                selected_sorted_filenames = st.multiselect("Raw files", sorted_filenames, sorted_filenames)

                # Create a list of full file paths
                raw_file_path_list = [os.path.join(self.raw_file_path_input, file) for file in selected_sorted_filenames]

                if len(raw_file_path_list) > 1:
                        # Add Threads slider
                        st.title("Threads")
                        threads = st.slider("Number of threads", 1, os.cpu_count(), os.cpu_count())
                else:
                    threads = 1

        self.raw_file_path_list = raw_file_path_list
        self.threads = threads
