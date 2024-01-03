import pandas as pd 

from massseer.loaders.GenericLoader import GenericLoader
from massseer.structs import TransitionGroup
from abc import ABC, abstractmethod
from typing import List, Union, Literal

class GenericChromatogramLoader(GenericLoader):
    '''
    Abstract class for loading raw chromatogram data
    
    Attributes:
        rsltsFile: (str) The path to the report file (DIANN-TSV or OSW)
        dataFiles: (str/List[str]) The path to the mzML file(s)
        rsltsFileType: (str) The type of results file (OpenSWATH or DIA-NN)
        verbose: (bool) Whether to print debug messages
        mode: (str) Whether to run in module or GUI mode
    '''

    def __init__(self, 
                 rsltsFile: str, 
                 dataFiles: Union[str, List[str]], 
                 rsltsFileType: Literal['OpenSWATH', 'DIA-NN'] = 'DIA-NN', 
                 verbose: bool=False, 
                 mode: Literal['module', 'gui'] = 'module'):
        super().__init__(rsltsFile, dataFiles, None, rsltsFileType, verbose, mode)
    
    @abstractmethod
    def loadTransitionGroups(self, pep_id: str, charge: int) -> dict[str, TransitionGroup]:
        '''
        Loads the transition group for a given peptide ID and charge across all files
        Args:
            pep_id (str): Peptide ID
            charge (int): Charge
        Returns:
            dict[str, TransitionGroup]: Dictionary of TransitionGroups, with keys as filenames
        '''
        pass

    @abstractmethod
    def loadTransitionGroupsDf(self, pep_id: str, charge: int) -> pd.DataFrame:
        '''
        Loads the transition group for a given peptide ID and charge across all files into a pandas DataFrame
        
        Args:
            pep_id (str): Peptide ID
            charge (int): Charge
        Returns:
            pd.DataFrame: DataFrame containing TransitionGroup information across all runs
        '''
        pass