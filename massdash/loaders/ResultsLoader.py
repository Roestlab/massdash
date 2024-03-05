"""
massdash/loaders/GenericLoader
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

from abc import ABC, abstractmethod
from os.path import basename
from typing import Dict, List, Union, Literal, Optional
import pandas as pd

# Loaders
from .SpectralLibraryLoader import SpectralLibraryLoader
from .access.OSWDataAccess import OSWDataAccess
from .access.ResultsTSVDataAccess import ResultsTSVDataAccess
# Structs
from ..structs import TransitionGroup, TransitionGroupFeatureCollection, TopTransitionGroupFeatureCollection
# Utils
from ..util import LOGGER

class ResultsLoader:
    ''' 
    Class for loading Chromatograms and peak features
    Classes which inherit from this should contain one results file and one transition file
    '''
    def __init__(self, 
                 rsltsFile: Union[str, List[str]], 
                 libraryFile: str = None,
                 verbose: bool=False, 
                 mode: Literal['module', 'gui'] = 'module'):

        LOGGER.name = __class__.__name__
        if verbose:
            LOGGER.setLevel("DEBUG")
        else:
            LOGGER.setLevel("INFO")

        ## store the file names
        self.libraryFile_str = libraryFile
 
        # Make rsltsFile iterable if it is not already
        if isinstance(rsltsFile, str):
            self.rsltsFile_str = [rsltsFile]
        else:
            self.rsltsFile_str = rsltsFile

        ### set the results file depending on the file ending
        self.rsltsAccess = []
        for f in self.rsltsFile_str:
            if f.endswith('.osw'):
                self.rsltsAccess = OSWDataAccess(f, verbose=verbose, mode=mode)
            elif f.endswith('.tsv'):
                self.rsltsAccess = ResultsTSVDataAccess(f, verbose=verbose)
            else:
                raise Exception(f"Error: Unsupported file type {f} or unsupported rsltsFileType {f}")
        
        if self.libraryFile_str is None:
            for f in self.rsltsFile_str:
                if f.endswith('.osw'): 
                    self.libraryFile = SpectralLibraryLoader(f)
                    self.libraryFile.load()
            else:
                LOGGER.warn("Library not specified, comparisons to library will not be possible")
        else:
            self.libraryFile = SpectralLibraryLoader(self.libraryFile_str)
            self.libraryFile.load()
 

    @abstractmethod
    def loadTransitionGroupFeaturesDf(self, pep_id: str, charge: int) -> pd.DataFrame:
        '''
        Loads a pandas dataframe of TransitionGroupFeatures across all runsPeakFeature object from the results file

        Args:
            pep_id (str): Peptide ID
            charge (int): Charge

        Returns:
            DataFrame: DataFrame containing TransitionGroupObject information across all runs 
        '''
        pass

    def loadTransitionGroupFeatures(self, pep_id: str, charge: int) -> TransitionGroupFeatureCollection:
        '''
        Loads a PeakFeature object from the results file
        Args:
            pep_id (str): Peptide ID
            charge (int): Charge
        Returns:
            PeakFeature: PeakFeature object containing peak boundaries, intensity and confidence
        '''
        out = TransitionGroupFeatureCollection()
        for t in self.dataFiles_str:
            runname = basename(t).split('.')[0]
            out[t] = self.rsltsAccess.getTransitionGroupFeatures(runname, pep_id, charge)
        return out
    

    def loadTopTransitionGroupFeature(self, pep_id: str, charge: int) -> TopTransitionGroupFeatureCollection:
        '''
        Loads a PeakFeature object from the results file
        Args:
            pep_id (str): Peptide ID
            charge (int): Charge
        Returns:
            TransitionGroup: TransitionGroup object containing peak boundaries, intensity and confidence
        '''
        out = {}
        for t in self.dataFiles_str:
            runname = basename(t).split('.')[0]
            out[t] = self.rsltsAccess.getTopTransitionGroupFeature(runname, pep_id, charge)
        return out
    
    #@abstractmethod
    def loadTopTransitionGroupFeatureDf(self, pep_id: str, charge: int) -> pd.DataFrame:
        '''
        Loads a pandas dataframe of TransitionGroupFeatures across all runsPeakFeature object from the results file
        Args:
            pep_id (str): Peptide ID
            charge (int): Charge
        Returns:
            DataFrame: DataFrame containing TransitionGroupObject information across all runs 
        '''
        pass


    def __str__(self):
        return f"{__class__.__name__}: rsltsFile={self.rsltsFile_str}, dataFiles={self.dataFiles_str}"

    def __repr__(self):
        return f"{__class__.__name__}: rsltsFile={self.rsltsFile_str}, dataFiles={self.dataFiles_str}"
