"""
massdash/ui/FileInputUISettings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import os
import fnmatch
from typing import Literal

import streamlit as st

# UI
from .FileInputXICDataUISettings import FileInputXICDataUISettings
from .FileInputRawDataUISettings import FileInputRawDataUISettings

class FileInputUISettings(FileInputXICDataUISettings, FileInputRawDataUISettings):
    def __init__(self, workflow: str=Literal["xic_data", "raw_data"]) -> None:
        """
        Initializes the FileInputUISettings class.

        Args:
            workflow (str): The workflow type. Can be either "xic_data" or "raw_data".
        """
        if workflow == "xic_data":
            super(FileInputXICDataUISettings, self).__init__()
        elif workflow == "raw_data":
            super(FileInputRawDataUISettings, self).__init__()



