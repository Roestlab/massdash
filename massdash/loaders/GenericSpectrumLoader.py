'''
This is an abstract class for loading spectra from a file.
'''

import pandas as pd

from ..loaders import GenericLoader
from abc import ABC, abstractmethod
from ..structs import TransitionGroup, TargetedDIAConfig, FeatureMap
from typing import List, Union, Literal

class GenericSpectrumLoader(GenericLoader):
    '''
    Abstract class for loading raw spectrum data

    Attributes:
        rsltsFile: (str) The path to the report file (DIANN-TSV or OSW)
        dataFiles: (str/List[str]) The path to the mzML file(s)
        libraryFile: (str) The path to the library file (.tsv or .pqp)
    '''
    
    def __init__(self, rsltsFile: str, dataFiles: Union[str, List[str]], libraryFile: str = None, rsltsFileType: Literal['OpenSWATH', 'DIA-NN'] = 'DIA-NN', verbose: bool=False, mode: Literal['module', 'gui'] = 'module'):
        super().__init__(rsltsFile=rsltsFile, dataFiles=dataFiles, libraryFile=libraryFile, rsltsFileType=rsltsFileType, verbose=verbose, mode=mode)

    @abstractmethod
    def loadTransitionGroups(self, pep_id: str, charge: int, config: TargetedDIAConfig) -> dict[str, TransitionGroup]:
        '''
        Loads the transition group for a given peptide ID and charge across all files

        Args:
            pep_id (str): Peptide ID
            charge (int): Charge
            config (TargetedDIAConfig): Configuration object containing the extraction parameters
        Return:
            dict[str, TransitionGroup]: Dictionary of TransitionGroups, with keys as filenames
        '''
        pass
    
    @abstractmethod
    def loadTransitionGroupsDf(self, pep_id: str, charge: int, config: TargetedDIAConfig) -> dict[str, pd.DataFrame]:
        '''
        Loads the transition group for a given peptide ID and charge across all files into a pandas DataFrame
        
        Args:
            pep_id (str): Peptide ID
            charge (int): Charge
            config (TargetedDIAConfig): Configuration object containing the extraction parameters
        
        Return:
            dict[str, pd.DataFrame]: Dictionary of TransitionGroups, with keys as filenames
        '''
        pass 

    @abstractmethod
    def loadFeatureMaps(self, pep_id: str, charge: int, config=TargetedDIAConfig) -> dict[str, FeatureMap]:
        '''
        Loads a dictionary of FeatureMaps (where the keys are the filenames) from the results file

        Args:
            pep_id (str): Peptide ID
            charge (int): Charge
        Returns:
            FeatureMap: FeatureMap object containing peak boundaries, intensity and confidence
        '''
        pass