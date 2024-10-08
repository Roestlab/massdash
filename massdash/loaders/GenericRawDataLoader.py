"""
massdash/loaders/GenericRawDataLoader
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

from abc import ABC, abstractmethod, ABCMeta
from typing import Dict, List, Union, Literal, Optional
from pathlib import Path

# Loaders
from .ResultsLoader import ResultsLoader
# Structs
from ..structs import TransitionGroup, TransitionGroupFeature
from .access.OSWDataAccess import OSWDataAccess
from .SpectralLibraryLoader import SpectralLibraryLoader
from ..util import LOGGER

from scipy.signal import savgol_filter, convolve
from scipy.signal.windows import gaussian
import pandas as pd

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
                        transitionGroupFeatures: Optional[List[TransitionGroupFeature]],
                        include_ms1: bool = False, 
                        smooth: bool = True, 
                        sgolay_polynomial_order: int = 3, 
                        sgolay_frame_length: int = 11, 
                        width=800,
                        **kwargs) -> 'bokeh.plotting.figure.Figure':
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

        from bokeh.plotting import output_notebook
       
        # Initiate Plotting in Jupyter Notebook
        output_notebook()

        # Extract chromatogram data from the transitionGroup
        precursorChroms, transitionChroms = transitionGroup.toPandasDf(separate=True)
        if include_ms1:
            to_plot = pd.concat([precursorChroms, transitionChroms])
        else:
            to_plot = transitionChroms

        # format transitionGroupFeatures for plotting with pyopenms_viz
        if transitionGroupFeatures is not None:
            transitionGroupFeatures.rename(columns={'leftBoundary':'leftWidth', 'rightBoundary':'rightWidth', 'consensusApexIntensity':'apexIntensity'}, inplace=True)

            # Determine the labels for the legend, this is dependent on software tool
            # if multiple software tools used, label by software
            labelBySoftware = transitionGroupFeatures['software'].nunique() > 1
            if transitionGroupFeatures.software is not None and labelBySoftware:
                feature_legend_labels = transitionGroupFeatures['software']
            else:
                feature_legend_labels = [ f"Feature {i+1}" for i in  range(len(transitionGroupFeatures)) ]
        else:
            feature_legend_labels = None

        def apply_smoothing(group):
            if smooth:
                group['intensity'] = savgol_filter(group['intensity'], window_length=sgolay_frame_length, polyorder=sgolay_polynomial_order)

            #elif pc.smoothing_dict['type'] == 'gauss':
            #    window = gaussian(pc.smoothing_dict['gaussian_window'], std=pc.smoothing_dict['gaussian_sigma'])
            #    intensity = convolve(intensity, window, mode='same') / window.sum()
            return group


        to_plot = to_plot.groupby('annotation').apply(apply_smoothing).reset_index(drop=True)

        fig = to_plot.plot(x='rt', y='intensity', kind='chromatogram', by='annotation', backend='ms_bokeh', annotation_data=transitionGroupFeatures, width=800, **kwargs) 
        return fig