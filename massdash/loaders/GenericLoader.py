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
from ..structs import TransitionGroup, TransitionGroupFeature, TransitionGroupFeatureCollection, TopTransitionGroupFeatureCollection
# Utils
from ..util import LOGGER

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
        elif rsltsFile.endswith('.tsv') and rsltsFileType in ['DIA-NN', 'OpenSWATH', 'DreamDIA']:
            self.rsltsFile = ResultsTSVDataAccess(self.rsltsFile_str, results_type = rsltsFileType, verbose=verbose)
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

    @abstractmethod
    def loadTransitionGroups(self, pep_id: str, charge: int) -> Dict[str, TransitionGroup]:
        '''
        Loads the transition group for a given peptide ID and charge across all files
        Args:
            pep_id (str): Peptide ID
            charge (int): Charge
        Returns:
            dict[str, TransitionGroup]: Dictionary of TransitionGroups, with keys as filenames
        '''
        pass

    def loadTransitionGroupFeatures(self, pep_id: str, charge: int) -> TransitionGroupFeatureCollection:
        """
        Load TransitionGroupFeature objects from the results file for the given peptide precursor

        Args:
            pep_id (str): Peptide Sequence
            charge (int): Charge of the peptide precursor to fetch

        Returns:
            TransitionGroupFeatureCollection: TransitionGroupFeatureCollection object containing peak boundaries, intensity and confidence for the specified peptide precursor
        """
        out = TransitionGroupFeatureCollection()
        for t in self.dataFiles_str:
            runname = basename(t).split('.')[0]
            out[runname] = self.rsltsFile.getTransitionGroupFeatures(runname, pep_id, charge)
        return out
    

    def loadTopTransitionGroupFeature(self, pep_id: str, charge: int) -> TopTransitionGroupFeatureCollection:
        """
        Load the top TransitionGroupFeature object from the results file for the given peptide precursor

        Args:
            pep_id (str): Peptide Sequence 
            charge (int): Charge of the peptide precursor to fetch

        Returns:
            TopTransitionGroupFeatureCollection: TopTransitionGroupFeatureCollection object containing peak boundaries, intensity and confidence for the top feature of the specified peptide precursor
        """
        out = {}
        for t in self.dataFiles_str:
            runname = basename(t).split('.')[0]
            out[runname] = self.rsltsFile.getTopTransitionGroupFeature(runname, pep_id, charge)
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

    def plotChromatogram(self,
                        transitionGroup: TransitionGroup,
                        transitionGroupFeatures: Optional[List[TransitionGroupFeature]],
                        include_ms1: bool = False, 
                        smooth: bool = True, 
                        sgolay_polynomial_order: int = 3, 
                        sgolay_frame_length: int = 11, 
                        scale_intensity: bool = False) -> 'bokeh.plotting.figure.Figure':
        '''
        Plots a chromatogram for a transitionGroup and transitionGroupFeatures given peptide sequence and charge state for a given run

        Args:
            transitionGroup (TransitionGroup): TransitionGroup object
            transitionGroupFeatures (List[TransitionGroupFeature]): List of TransitionGroupFeature objects, plots peak boundaries if not None
            include_ms1 (bool, optional): Whether to include MS1 data. Defaults to False.
            smooth (bool, optional): Whether to smooth the chromatogram. Defaults to True.
            sgolay_polynomial_order (int, optional): Order of the polynomial to use for smoothing. Defaults to 3.
            sgolay_frame_length (int, optional): Frame length to use for smoothing. Defaults to 11.
            scale_intensity (bool, optional): Whether to scale the intensity of the chromatogram such that all chromatograms are individually normalized to 1. Defaults to False.

        Returns: 
            bokeh.plotting.figure.Figure: Bokeh figure object
        '''

        from bokeh.plotting import output_notebook, show
        from ..plotting import InteractivePlotter, PlotConfig
       
        # Initiate Plotting in Jupyter Notebook
        output_notebook()

        # Create an instance of the InteractivePlotter class and set appropriate config
        pc = PlotConfig()
        pc.include_ms1 = include_ms1
        if smooth:
            pc.smoothing_dict = {'type': 'sgolay', 'sgolay_polynomial_order': sgolay_polynomial_order, 'sgolay_frame_length': sgolay_frame_length}
        else:
            pc.smoothing_dict = {'type': 'none'}
        pc.scale_intensity = scale_intensity

        plotter = InteractivePlotter(pc)

        # Plot the chromatogram data
        fig = plotter.plot(transitionGroup, transitionGroupFeatures)

        show(fig)

        return fig

    def __str__(self):
        return f"{__class__.__name__}: rsltsFile={self.rsltsFile_str}, dataFiles={self.dataFiles_str}"

    def __repr__(self):
        return f"{__class__.__name__}: rsltsFile={self.rsltsFile_str}, dataFiles={self.dataFiles_str}"
