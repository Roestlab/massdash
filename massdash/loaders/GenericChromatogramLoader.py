import pandas as pd 

from .GenericLoader import GenericLoader
from ..structs import TransitionGroup
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

    def plotChromatogram(self,
                        seq: str, 
                        charge: int, 
                        includeBoundaries: bool = True, 
                        include_ms1: bool = False, 
                        smooth: bool = True, 
                        sgolay_polynomial_order: int = 3, 
                        sgolay_frame_length: int = 11, 
                        scale_intensity: bool = False) -> 'bokeh.plotting.figure.Figure':
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

        Returns: 
            bokeh.plotting.figure.Figure: Bokeh figure object
        '''

        print("here")
        ## TODO allow plotting of multiple chromatograms
        if len(self.dataFiles_str) > 1:
            raise NotImplementedError("Only one transition file is supported")
 
        # load the transitionGroup for plotting
        transitionGroup = list(self.loadTransitionGroups(seq, charge).values())[0]
        print(transitionGroup)
        if includeBoundaries:
            transitionGroupFeatures = list(self.loadTransitionGroupFeatures(seq, charge).values())[0]
        else:
            transitionGroupFeatures = []

        return super().plotChromatogram(transitionGroup, transitionGroupFeatures, include_ms1=include_ms1, smooth=smooth, sgolay_polynomial_order=sgolay_polynomial_order, sgolay_frame_length=sgolay_frame_length, scale_intensity=scale_intensity)