"""
massdash/loaders/ResultsLoader
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

        # Attributes (set further down)
        self.rsltsAccess = []
        self.libraryAccess = None
        self.runNames = None
        self.verbose = verbose
        self.libraryFile = libraryFile

        if isinstance(rsltsFile, str):
            self.rsltsFile = [rsltsFile]

        LOGGER.name = __class__.__name__
        if self.verbose:
            LOGGER.setLevel("DEBUG")
        else:
            LOGGER.setLevel("INFO")

        # Make rsltsFile iterable if it is not already
        ### set the results file depending on the file ending
        for f in self.rsltsFile:
            if f.endswith('.osw'):
                self.rsltsAccess.append(OSWDataAccess(f, verbose=verbose, mode=mode))
            elif f.endswith('.tsv'):
                self.rsltsAccess.append(ResultsTSVDataAccess(f, verbose=verbose))
            else:
                raise Exception(f"Error: Unsupported file type {f} or unsupported rsltsFileType {f}")
              
        # If called as a Results loader, infer the run names since no raw data will be used.
        self.runNames = self._inferRunNames()

        if self.libraryFile is not None:
            self.libraryAccess = SpectralLibraryLoader(self.libraryFile)
            self.libraryAccess.load()


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
        for d in self.runNames:
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
        for t in self.runNames:
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
        for d in self.runNames:
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
        for t in self.runNames:
            runname = basename(t).split('.')[0]
            feats = []
            for r in self.rsltsAccess:
                feats.append(r.getTopTransitionGroupFeature(runname, pep_id, charge))
            out[t] = feats
        return out
   
    def __str__(self):
        return f"{__class__.__name__}: rsltsFile={self.rsltsFile}"

    def __repr__(self):
        return f"{__class__.__name__}: rsltsFile={self.rsltsFile}"
