"""
massdash/loaders/TrafoXMLLoader
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

from typing import List, Dict, Union

# Access
from .access.TrafoXMLAccess import TrafoXMLAccess

class TrafoXMLLoader:
    def __init__(self, dataFiles: Union[str, List[str]], libraryFile: Union[str, List[str]] = None):
        ## store the file names
        if isinstance(dataFiles, str):
            self.dataFiles_str = [dataFiles]
        else:
            self.dataFiles_str = dataFiles
            
        if isinstance(libraryFile, str):
            self.libraryFile_str = [libraryFile]
        else:
            self.libraryFile_str = libraryFile
        print(f"len libraryFile: {len(self.libraryFile_str)}")
    
        if self.libraryFile_str is not None and len(self.libraryFile_str) > 1:
            self.dataFiles = [TrafoXMLAccess(f, l) for f, l in zip(self.dataFiles_str, self.libraryFile_str)]
        elif self.libraryFile_str is not None and len(self.libraryFile_str) == 1:
            self.dataFiles = [TrafoXMLAccess(f, self.libraryFile_str[0]) for f in self.dataFiles_str]
    
    def __str__(self):
        return f"TrafoXMLLoader(dataFiles={self.dataFiles_str}, libraryFile={self.libraryFile_str}"

    def __repr__(self):
        return f"TrafoXMLLoader(dataFiles={self.dataFiles_str}, libraryFile={self.libraryFile_str}"
    
    