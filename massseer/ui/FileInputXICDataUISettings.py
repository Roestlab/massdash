import streamlit as st

import os
import fnmatch

from massseer.ui.BaseUISettings import BaseUISettings

class FileInputXICDataUISettings(BaseUISettings):
    def __init__(self) -> None:
        """
        Initializes the FileInputXICDataUISettings class.
        """
        super().__init__()
        self.osw_file_path = None
        self.sqmass_file_path_input = None
        self.sqmass_file_path_list = None 
        self.threads = None

    def create_ui(self, feature_file_path: str=None, xic_file_path: str=None):
        """
        Creates the sidebar for the input file paths.

        Parameters:
        feature_file_path (str): Path to the OpenSwathWorkflow output file (*.osw)
        xic_file_path (str): Path to the sqMass file (*.sqMass) or path to a directory containing sqMass files.
        """
        st.sidebar.subheader("Input OSW file")
        self.osw_file_path = st.sidebar.text_input("Enter file path", feature_file_path, key='osw_file_path_sidebar', help="Path to the OpenSwathWorkflow output file (*.osw)")
        st.sidebar.subheader("Input sqMass (file/directory)")
        self.sqmass_file_path_input = st.sidebar.text_input("Enter file path", xic_file_path, key='sqmass_file_path_input_sidebar', help="Path to the sqMass file (*.sqMass) or path to a directory containing sqMass files.")

    def get_sqmass_files(self, threads: int=1):
        """
        Given a path to a directory or a file, returns a list of full file paths to *.sqMass files in the directory or the file itself.
        If the input path is a directory, the function displays a selection box in the sidebar to select the *.sqMass files.
        If the input path is a file, the function returns a list containing only the input file path.
        The function also displays a slider to select the number of threads to use for processing the files.
        
        Parameters:
        sqmass_file_path_input (str): Path to a directory or a file
        
        Returns:
        sqmass_file_path_list (list): List of full file paths to *.sqMass files in the directory or the file itself.
        threads (int): Number of threads to use for processing the files.
        """
        
        if os.path.isfile(self.sqmass_file_path_input):
            sqmass_file_path_list = [self.sqmass_file_path_input]
        else:
            # Check to ensure directory exists otherwise throw error
            if not os.path.isdir(self.sqmass_file_path_input):
                raise ValueError(f"Error: Directory {self.sqmass_file_path_input} does not exist!")
            
            # 1. Get the list of files in the directory
            files_in_directory = os.listdir(self.sqmass_file_path_input)
            
            #2. Filter the files based on the *.sqMass file extension (case-insensitive)
            files_in_directory = [filename for filename in files_in_directory if fnmatch.fnmatch(filename.lower(), '*.sqmass')]

            # 3. Sort the filenames alphabetically
            sorted_filenames = sorted(files_in_directory, reverse=False)
            
            st.sidebar.subheader(f"{len(sorted_filenames)} sqMass file(s)")
            with st.sidebar.expander("Advanced Settings"):
                # Create a selection box in the sidebar
                selected_sorted_filenames = st.multiselect("sqMass files", sorted_filenames, sorted_filenames, help="Select the sqMass files to process")    

                # Create a list of full file paths
                sqmass_file_path_list = [os.path.join(self.sqmass_file_path_input, file) for file in selected_sorted_filenames]

                if len(sqmass_file_path_list) > 1:
                        # Add Threads slider
                        st.title("Threads")
                        threads = st.slider("Number of threads", 1, os.cpu_count(), os.cpu_count())
                else:
                    threads = 1

        self.sqmass_file_path_list = sqmass_file_path_list 
        self.threads = threads

            