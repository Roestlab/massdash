"""
massdash/structs/TransitionGroup
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

from typing import List, Tuple, Optional, Union, Literal
import pyopenms as po
import pandas as pd

# Structs
from .Chromatogram import Chromatogram
from .Mobilogram import Mobilogram
from .Spectrum import Spectrum
from .TransitionGroupFeature import TransitionGroupFeature

class TransitionGroup:
    '''
    Class for Storing a transition group
    '''
    def __init__(self, precursorData: Union[List[Chromatogram], List[Mobilogram], List[Spectrum]],
                 transitionData: Union[List[Chromatogram], List[Mobilogram], List[Spectrum]]):
        self.precursorData = precursorData
        self.transitionData = transitionData
        self.type = type(precursorData[0])
        if len(transitionData) > 0:
            self.dataType = type(transitionData[0])
        elif len(precursorData) > 0:
            self.dataType = type(precursorData[0])
        else: 
            raise ValueError("Precursor and transition data cannot both be empty")
        if len(precursorData) > 0 and len(transitionData) > 0:
            assert(self.dataType == type(transitionData[0])) 
  

    def to_pyopenms(self, includePrecursors=True):
        '''
        Converts the TransitionGroup to an OpenMS TransitionGroup
        '''
        transitionGroup = po.MRMTransitionGroupCP()
        for i in range(len(self.transitionData)):
            transition = po.ReactionMonitoringTransition()
            transition.setNativeID(str(i))
            chrom = self.transitionData[i].to_pyopenms(id=str(i))
            transitionGroup.addChromatogram(chrom, chrom.getNativeID())
            transitionGroup.addTransition(transition, transition.getNativeID())

        if includePrecursors:
            for i in range(len(self.precursorData)):
                precursor = po.ReactionMonitoringTransition()
                precursor.setNativeID('p' + str(i))
                chrom = self.precursorData[i].to_pyopenms(id='p' + str(i))
                transitionGroup.addPrecursorChromatogram(chrom, chrom.getNativeID())
        return transitionGroup
    
    def max(self, boundary: Tuple[float, float], level: Optional[str] = 'ms1ms2') -> float:
        """
        Calculate the highest intensity within a given boundary.

        Args:
            boundary (tuple): A tuple containing the left and right boundaries.

        Returns:
            float: The highest intensity within the given boundary.
        """
        chroms = self._resolveLevel(level)

        highest_intensity = 0.0  # Initialize with a default value
        for c in chroms:
            intens = c.max(boundary)[1]
            if intens > highest_intensity:
                highest_intensity = intens

        return highest_intensity
    

    def _resolveLevel(self, level):
        if level=='ms1':
            return self.precursorData
        elif level=='ms2':
            return self.transitionData
        elif level=='ms1ms2':
            return self.precursorData + self.transitionData
        else:
            raise ValueError("Level must be one of ['ms1', 'ms2', 'ms1ms2']")

    def sum(self, boundary: Tuple[float, float], level: str = 'ms2') -> float:
        """
        Calculates the integrated intensity of a chromatogram within a given boundary.

        Args:
            boundary (tuple): A tuple containing the left and right boundaries of the integration range.

        Returns:
            float: The integrated intensity of the chromatogram within the given boundary.
        """
        chroms = self._resolveLevel(level)
        integrated_intensity = 0.0
        for c in chroms:
            integrated_intensity += c.sum(boundary)

        return integrated_intensity
    
    def flatten(self, level: str = 'ms2'):
        '''
        Flatten the TransitionGroup into a single Data1D object
        '''
        data1D = self._resolveLevel(level)
        data = []
        intensity = []
        for c in data1D:
            data.extend(c.data)
            intensity.extend(c.intensity)
        sorted = pd.DataFrame({'data': data, 'intensity': intensity}).sort_values(by='data')
        return self.dataType(sorted['data'], sorted['intensity'])

    def median(self, boundary: Optional[Tuple[float, float]] = None, level: Optional[str] = 'ms2') -> float:
        """
        Calculate the median intensity of a given boundary in the 1D data.

        Args:
            chrom_data (list): A list of tuples containing the retention time and intensity values of a chromatogram.
            boundary (tuple): A tuple containing the left and right boundaries of the region of interest.

        Returns:
            float: The median intensity value of the data points within the given boundary.
        """

        data_flattened = self.flatten(level)
        if boundary is not None:
            data_flattened = data_flattened.filter(boundary)

        return data_flattened.median()

    def __str__(self) -> str:
        '''
        Returns a string representation of the transition group.

        Returns:
            str: A string representation of the transition group.
        '''
        return f"{'-'*8} TransitionGroup {'-'*8}\nprecursor data: {len(self.precursorData)}\ntransition data: {len(self.transitionData)}\ndata type: {self.dataType.__name__}"

    def empty(self) -> bool:
        """
        Check if the TransitionGroup is empty.

        Returns:
            bool: True if all of the chromatograms, mobilograms, and spectra are empty, False otherwise.
        """
        return not any(p.empty() for p in self.precursorData) and any(t.empty() for t in self.transitionData)
    
    def plot(self, 
             transitionGroupFeatures: Optional[List[TransitionGroupFeature]] = None, 
             smoothing: Optional[Literal['none', 'sgolay']] = 'none',
             sgolay_polynomial_order: int = 3,
             sgolay_frame_length: int = 11) -> None:
        '''
        Plot the 1D data, meant for jupyter notebook context
        '''
        from plotting.GenericPlotter import PlotConfig
        from plotting.InteractivePlotter import InteractivePlotter

        config = PlotConfig()
        if self.type == Chromatogram:
            config.plot_type = "chromatogram"
        elif self.type == Mobilogram:
            config.plot_type = "mobilogram"
        elif self.type == Spectrum:
            config.plot_type = "spectrum"
        else:
            raise ValueError("Unknown type of 1D data")

        config.smoothing_dict = {'type': smoothing, 'sgolay_polynomial_order': sgolay_polynomial_order, 'sgolay_frame_length': sgolay_frame_length}

        plotter = InteractivePlotter(config)

        plotter.plot(self)

        if transitionGroupFeatures is not None:
            if self.type == Chromatogram:
                plotter.add_peak_boundaries(plotter.fig, transitionGroupFeatures)
            else:
                raise NotImplementedError("Peak boundaries are only implemented for chromatograms")

        plotter.show()