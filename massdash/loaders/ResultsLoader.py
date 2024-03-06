"""
massdash/loaders/GenericLoader
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

from abc import ABC, abstractmethod
from os.path import basename
from typing import Dict, List, Union, Literal, Optional
import pandas as pd
from pathlib import Path 

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
                self.rsltsAccess.append(OSWDataAccess(f, verbose=verbose, mode=mode))
            elif f.endswith('.tsv'):
                self.rsltsAccess.append(ResultsTSVDataAccess(f, verbose=verbose))
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
        
        # If called as a Results loader, infer the run names since no raw data will be used.
        if isinstance(self, ResultsLoader):
            self.dataFiles_str = self._inferRunNames()


    def _inferRunNames(self):
        '''
        Infer the run names from the results file
        '''
        runNames = set()
        for f in self.rsltsAccess:
            runNames = runNames.union(set(f.getRunNames()))
        return list(runNames)

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

    def loadTransitionGroupFeaturesDf(self, pep_id: str, charge: int) -> pd.DataFrame:
        '''
        Loads a TransitionGroupFeature object from the results file to a pandas dataframe

        Args:
            pep_id (str): Peptide ID
            charge (int): Charge
        
        Returns:
            DataFrame: DataFrame containing TransitionGroupObject information across all runs
        '''
        out = {}
        for d in self.dataFiles_str:
            for r in self.rsltsAccess:
                features = r.getTransitionGroupFeaturesDf(d, pep_id, charge)
                out[d] = features
        
        return pd.concat(out).reset_index().drop(columns='level_1').rename(columns=dict(level_0='runname'))

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
            feats = []
            for r in self.rsltsAccess:
                feats += r.getTransitionGroupFeatures(runname, pep_id, charge)
            out[t] = feats
        return out
    
    def loadTopTransitionGroupFeatureDf(self, pep_id: str, charge: int) -> pd.DataFrame:
        '''
        Loads a pandas dataframe of TransitionGroupFeatures across all runsPeakFeature object from the results file
        Args:
            pep_id (str): Peptide ID
            charge (int): Charge
        Returns:
            DataFrame: DataFrame containing TransitionGroupObject information across all runs 
        '''
        out = {}
        for d in self.dataFiles_str:
            for r in self.rsltsAccess:
                features = r.getTopTransitionGroupFeatureDf(d, pep_id, charge)
                out[d] = features
        
        return pd.concat(out).reset_index().drop(columns='level_1').rename(columns=dict(level_0='filename'))

    def loadTopTransitionGroupFeature(self, pep_id: str, charge: int) -> TransitionGroupFeatureCollection:
        '''
        Loads a PeakFeature object from the results file
        Args:
            pep_id (str): Peptide ID
            charge (int): Charge
        Returns:
            TransitionGroup: TransitionGroup object containing peak boundaries, intensity and confidence
        '''
        out = TransitionGroupFeatureCollection()
        for t in self.dataFiles_str:
            runname = basename(t).split('.')[0]
            feats = []
            for r in self.rsltsAccess:
                feats.append(r.getTopTransitionGroupFeature(runname, pep_id, charge))
            out[t] = feats
        return out
   
    def __str__(self):
        return f"{__class__.__name__}: rsltsFile={self.rsltsFile_str}, dataFiles={self.dataFiles_str}"

    def __repr__(self):
        return f"{__class__.__name__}: rsltsFile={self.rsltsFile_str}, dataFiles={self.dataFiles_str}"
