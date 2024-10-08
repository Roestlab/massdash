"""
massdash/loaders/GenericRawDataLoader
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

from abc import ABC, abstractmethod, ABCMeta
from typing import Dict, List, Union, Literal, Optional
from pathlib import Path
import pandas as pd

# Loaders
from .ResultsLoader import ResultsLoader
# Structs
from ..structs import TransitionGroup, TransitionGroupFeature
from .access.OSWDataAccess import OSWDataAccess
from .SpectralLibraryLoader import SpectralLibraryLoader
from ..util import LOGGER

class GenericRawDataLoader(ResultsLoader, metaclass=ABCMeta):
    ''' 
    Abstract class for loading Chromatograms and peak features
    Classes which inherit from this should contain one results file and one transition file
    '''
    @abstractmethod
    def __init__(self, dataFiles: Union[str, List[str]], **kwargs):
        super().__init__(**kwargs)
        self.dataAccess = None # set by child class

        # convert dataFiles to a list if it is not already. Will be set by the child class
        if isinstance(dataFiles, str):
            self.dataFiles = [dataFiles]
        else:
            self.dataFiles = dataFiles

        if self.libraryFile is None:
            for a in self.rsltsAccess:
                if isinstance(a, OSWDataAccess): 
                    self.libraryAccess = SpectralLibraryLoader(a.filename)
                    self.libraryAccess.load()
        # I think the comment below was previously added, by mistake if not necessary then remove
        #else:
        #    self.libraryAccess = SpectralLibraryLoader(self.libraryAccess)
        #    self.libraryAccess.load()

        ## overwrite run names since we are specifying data files
        self.runNames = [Path(f).stem for f in self.dataFiles]
        
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

    def plotChromatogram(self,
                        transitionGroup: TransitionGroup,
                        transitionGroupFeatures: pd.DataFrame,
                        include_ms1: bool = False, 
                        smooth: bool = True, 
                        sgolay_polynomial_order: int = 3, 
                        sgolay_frame_length: int = 11,
                        **kwargs) -> 'bokeh.plotting.figure.Figure':
        '''
        Plots a chromatogram for a transitionGroup and transitionGroupFeatures given peptide sequence and charge state for a given run, will plot with plotly backend

        Args:
            transitionGroup (TransitionGroup): TransitionGroup object
            transitionGroupFeatures (List[TransitionGroupFeature]): List of TransitionGroupFeature objects, plots peak boundaries if not None
            include_ms1 (bool, optional): Whether to include MS1 data. Defaults to False.
            smooth (bool, optional): Whether to smooth the chromatogram. Defaults to True.
            sgolay_polynomial_order (int, optional): Order of the polynomial to use for smoothing. Defaults to 3.
            sgolay_frame_length (int, optional): Frame length to use for smoothing. Defaults to 11.
            **kwargs - kwargs to pyopenms_viz plotting

        Returns: 
            bokeh.plotting.figure.Figure: Bokeh figure object
        '''

        from ..plotting import InteractivePlotter, PlotConfig

        # Create an instance of the InteractivePlotter class and set appropriate config
        pc = PlotConfig()
        pc.include_ms1 = include_ms1
        if smooth:
            pc.smoothing_dict = {'type': 'sgolay', 'sgolay_polynomial_order': sgolay_polynomial_order, 'sgolay_frame_length': sgolay_frame_length}
        else:
            pc.smoothing_dict = {'type': 'none'}

        plotter = InteractivePlotter(pc)

        print(transitionGroupFeatures)
        # make a pyopenms_viz transitionGroupFeature
        transitionGroupFeatures.rename(columns={'leftBoundary':'leftWidth', 'rightBoundary':'rightWidth', 'consensusApexIntensity':'apexIntensity'}, inplace=True)

        # Plot the chromatogram data
        if len(transitionGroupFeatures) > 0:
            # if multiple software tools used, label by software
            labelBySoftware = transitionGroupFeatures['software'].nunique() > 1
            if transitionGroupFeatures.software is not None and labelBySoftware:
                feature_legend_labels = transitionGroupFeatures['software']
            else:
                feature_legend_labels = [ f"Feature {i+1}" for i in  range(len(transitionGroupFeatures)) ]
        else:
            feature_legend_labels = []

        fig = plotter.plot(transitionGroup, transitionGroupFeatures, feature_legend_labels=feature_legend_labels, **kwargs)
        return fig