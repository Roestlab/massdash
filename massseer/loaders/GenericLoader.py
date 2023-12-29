from abc import ABC, abstractmethod
from massseer.structs.TransitionGroup import TransitionGroup
from massseer.structs.TransitionGroupFeature import TransitionGroupFeature
from massseer.loaders.SpectralLibraryLoader import SpectralLibraryLoader
from massseer.loaders.access.OSWDataAccess import OSWDataAccess
from massseer.loaders.access.ResultsTSVDataAccess import ResultsTSVDataAccess
from typing import List, Union, Literal
from os.path import basename
from massseer.util import LOGGER
import pandas as pd

class GenericLoader(ABC):
    ''' 
    Abstract class for loading Chromatograms and peak features
    Classes which inherit from this should contain one results file and one transition file
    '''
    def __init__(self, rsltsFile: str, dataFiles: Union[str, List[str]], libraryFile: str, rsltsFileType: Literal['OpenSWATH', 'DIA-NN', 'Spectronaut', 'DreamDIA'], verbose: bool=False):
        ## store the file names
        self.rsltsFile_str = rsltsFile
        self.libraryFile_str = libraryFile
        
        # convert dataFiles to a list if it is not already. Will be set by the child class
        if isinstance(dataFiles, str):
            self.dataFiles_str = [dataFiles]
        else:
            self.dataFiles_str = dataFiles

        ### set the results file depending on the file ending
        if self.rsltsFile_str.endswith('.osw') and rsltsFileType == 'OpenSWATH':
            self.rsltsFile = OSWDataAccess(self.rsltsFile_str)
        elif rsltsFile.endswith('.tsv') and rsltsFileType == 'DIA-NN':
            self.rsltsFile = ResultsTSVDataAccess(self.rsltsFile_str)
        else:
            raise Exception(f"Error: Unsupported file type {rsltsFile} or unsupported rsltsFileType {rsltsFileType}")
        
        self.libraryFile = SpectralLibraryLoader(self.libraryFile_str)
        self.libraryFile.load()
 
        LOGGER.name = __class__.__name__
        if verbose:
            LOGGER.setLevel("DEBUG")
        else:
            LOGGER.setLevel("INFO")



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

    def loadTransitionGroupFeatures(self, pep_id: str, charge: int) -> dict[str, List[TransitionGroupFeature]]:
        '''
        Loads a PeakFeature object from the results file
        Args:
            pep_id (str): Peptide ID
            charge (int): Charge
        Returns:
            PeakFeature: PeakFeature object containing peak boundaries, intensity and confidence
        '''
        out = {}
        for t in self.dataFiles_str:
            runname = basename(t).split('.')[0]
            out[t] = self.rsltsFile.getTransitionGroupFeatures(runname, pep_id, charge)
        return out
    

    def loadTopTransitionGroupFeature(self, pep_id: str, charge: int) -> dict[str, TransitionGroup]:
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
            out[t] = self.rsltsFile.getTopTransitionGroupFeature(runname, pep_id, charge)
        return out
    
    @abstractmethod
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
