'''
massdash/loaders/GenericSpectrumLoader
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is an abstract class for loading spectra from a file.
'''

from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict, List, Union, Literal, Optional

# Loader
from .GenericLoader import GenericLoader
# Structs
from ..structs import TransitionGroup, TargetedDIAConfig, FeatureMap

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
    def loadTransitionGroups(self, pep_id: str, charge: int, config: TargetedDIAConfig) -> Dict[str, TransitionGroup]:
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
    def loadTransitionGroupsDf(self, pep_id: str, charge: int, config: TargetedDIAConfig) -> Dict[str, pd.DataFrame]:
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
    def loadFeatureMaps(self, pep_id: str, charge: int, config=TargetedDIAConfig) -> Dict[str, FeatureMap]:
        '''
        Loads a dictionary of FeatureMaps (where the keys are the filenames) from the results file

        Args:
            pep_id (str): Peptide ID
            charge (int): Charge
        Returns:
            FeatureMap: FeatureMap object containing peak boundaries, intensity and confidence
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

        ## TODO allow plotting of multiple chromatograms
        if len(self.dataFiles_str) > 1:
            raise NotImplementedError("Only one transition file is supported")
 
        # specify extraction paramaters
        extraction_parameters = TargetedDIAConfig()
        extraction_parameters.mz_tol = mz_tol
        extraction_parameters.rt_window = rt_window
        extraction_parameters.im_window = im_window

        # load the transitionGroup for plotting
        transitionGroup = list(self.loadTransitionGroups(seq, charge, extraction_parameters).values())[0]
        if includeBoundaries:
            transitionGroupFeatures = list(self.loadTransitionGroupFeatures(seq, charge).values())[0]
        else:
            transitionGroupFeatures = []

        return super().plotChromatogram(transitionGroup, transitionGroupFeatures, include_ms1=include_ms1, smooth=smooth, sgolay_polynomial_order=sgolay_polynomial_order, sgolay_frame_length=sgolay_frame_length, scale_intensity=scale_intensity)