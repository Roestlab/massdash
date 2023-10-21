import os
import glob
import base64

# streamlit components
import streamlit as st

# Type hinting
from typing import List, Tuple

# Common environment variables
PROJECT_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
WORKING_FOLDER = os.getcwd()
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




