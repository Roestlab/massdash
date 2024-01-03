from abc import ABC, abstractmethod
from massseer.structs.TransitionGroup import TransitionGroup
from massseer.structs.TransitionGroupFeature import TransitionGroupFeature
from massseer.loaders.SpectralLibraryLoader import SpectralLibraryLoader
from massseer.loaders.access.OSWDataAccess import OSWDataAccess
from massseer.loaders.access.ResultsTSVDataAccess import ResultsTSVDataAccess
from typing import List, Union, Literal, Optional
from os.path import basename
from massseer.util import LOGGER
import pandas as pd

class GenericLoader(ABC):
    ''' 
    Abstract class for loading Chromatograms and peak features
    Classes which inherit from this should contain one results file and one transition file
    '''
    def __init__(self, 
                 rsltsFile: str, 
                 dataFiles: Union[str, List[str]], 
                 libraryFile: str = None, 
                 rsltsFileType: Literal['OpenSWATH', 'DIA-NN'] = 'DIA-NN', 
                 verbose: bool=False, 
                 mode: Literal['module', 'gui'] = 'module'):
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
            self.rsltsFile = OSWDataAccess(self.rsltsFile_str, mode=mode)
        elif rsltsFile.endswith('.tsv') and rsltsFileType == 'DIA-NN':
            self.rsltsFile = ResultsTSVDataAccess(self.rsltsFile_str)
        else:
            raise Exception(f"Error: Unsupported file type {rsltsFile} or unsupported rsltsFileType {rsltsFileType}")
        
        
        if self.libraryFile_str is None:
            if self.rsltsFile_str.endswith('.osw'): 
                self.libraryFile = SpectralLibraryLoader(self.rsltsFile_str)
                self.libraryFile.load()
            else:
                raise ValueError("Error: Library file must be specified for .tsv results files")
        else:
            self.libraryFile = SpectralLibraryLoader(self.libraryFile_str)
            self.libraryFile.load()
 

 
        LOGGER.name = __class__.__name__
        if verbose:
            LOGGER.setLevel("DEBUG")
        else:
            LOGGER.setLevel("INFO")

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

    @abstractmethod
    def plotChromatogram(self,
                        seq: str, 
                        charge: int, 
                        includeBoundaries: bool = True, 
                        include_ms1: bool = False, 
                        smooth: bool = True, 
                        sgolay_polynomial_order: int = 3, 
                        sgolay_frame_length: int = 11, 
                        scale_intensity: bool = False,
                        mz_tol: float = 20,
                        rt_window: float = 50,
                        im_window: Optional[float] = None) -> 'bokeh.plotting.figure.Figure':
        '''
        Plots a chromatogram for a given peptide sequence and charge state for a given run

        Args:
            seq (str): Peptide sequence
            charge (int): Charge state
            includeBoundaries (bool, optional): Whether to include peak boundaries. Defaults to True.
            include_ms1 (bool, optional): Whether to include MS1 data. Defaults to False.
            smooth (bool, optional): Whether to smooth the chromatogram. Defaults to True.
            sgolay_polynomial_order (int, optional): Order of the polynomial to use for smoothing. Defaults to 3.
            sgolay_frame_length (int, optional): Frame length to use for smoothing. Defaults to 11.
            scale_intensity (bool, optional): Whether to scale the intensity of the chromatogram such that all chromatograms are individually normalized to 1. Defaults to False.
            mz_tol (float, optional): m/z tolerance for extraction (in ppm). Defaults to 20.
            rt_tol (float, optional): RT tolerance for extraction (in seconds). Defaults to 50.
            im_tol (float, optional): IM tolerance for extraction (in 1/k0). Defaults to None.

        Returns: 
            bokeh.plotting.figure.Figure: Bokeh figure object
        '''
        pass

    def __str__(self):
        return f"{__class__.__name__}: rsltsFile={self.rsltsFile_str}, dataFiles={self.dataFiles_str}"

    def __repr__(self):
        return f"{__class__.__name__}: rsltsFile={self.rsltsFile_str}, dataFiles={self.dataFiles_str}"
