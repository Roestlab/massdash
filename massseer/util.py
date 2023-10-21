import os
import glob
import base64

# streamlit components
import streamlit as st

# Type hinting
from typing import List, Tuple

# Common environment variables
# TODO: Should we use this projects directory or the current working directory to connect data_library, data_dia and data_dda directories?
PROJECT_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
WORKING_FOLDER = os.getcwd()
PARAM_FOLDER = os.path.abspath(os.path.join(PROJECT_FOLDER, "params"))
DATA_RAW_FOLDER = os.path.join(WORKING_FOLDER, "data_raw")
DATA_DIA_FOLDER = os.path.join(WORKING_FOLDER, "data_dia")
MASSPEC_FILE_FORMATS = ["mzML", "mzXML", "raw", "wiff", "d"]

# Common methods
def get_data_folder():
    return os.path.join(PROJECT_FOLDER, "data")

def get_input_folder():
    return os.path.join(get_data_folder(), "input")

def get_output_folder():
    return os.path.join(get_data_folder(), "output")

# @st.cache_data()
def get_base64_of_bin_file(png_file):
    """Convert a binary file to the corresponding base64 representation"""
    with open(png_file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

def list_files(path):
    """List files in the data folder"""
    files = []
    for filename in os.listdir(path):
        if os.path.isfile(os.path.join(path, filename)) and filename.split(".")[1] in MASSPEC_FILE_FORMATS:
            files.append(filename)
        elif os.path.isdir(os.path.join(path, filename)) and filename.endswith(".d"):
            files.append(filename + "/")
    return files

# UI methods
class FileObject:
    def __init__(self, path):
        self.name = path

def file_selector(folder_path='.', label='Select a file', key='select_file', file_pattern='*', **kwargs):
    patterns = file_pattern.split('|')
    filenames = []
    for pattern in patterns:
        filenames.extend(glob.glob(os.path.join(folder_path, pattern)))
    filenames = [os.path.basename(filename) for filename in filenames]
    selected_filename = st.selectbox(label, filenames, key=key, **kwargs)
    return FileObject(selected_filename)

def directory_selector(folder_path='.', label='Select a directory', key='select_directory', **kwargs):
    directories = []
    
    def get_directories(path):
        with os.scandir(path) as entries:
            for entry in entries:
                if entry.is_dir() and not entry.name.startswith('.'):
                    directories.append(entry.path)
                    get_directories(entry.path)
    
    get_directories(folder_path)
    directories = [os.path.relpath(directory, folder_path) for directory in directories]
    selected_directory = st.selectbox(label, directories, key=key, **kwargs)
    return os.path.join(folder_path, selected_directory)



