from massseer.structs.Chromatogram import Chromatogram
from typing import List, Tuple, Optional
import pyopenms as po
import numpy as np


class TransitionGroup:
    '''
    Class for Storing a transition group
    '''
    def __init__(self, precursorChroms: List[Chromatogram], transitionChroms: List[Chromatogram]):
        self.precursorChroms = precursorChroms
        self.transitionChroms = transitionChroms

    def to_pyopenms(self, includePrecursors=False):
        '''
        Converts the TransitionGroup to an OpenMS TransitionGroup
        '''
        transitionGroup = po.MRMTransitionGroupCP()
        for i in range(len(self.transitionChroms)):
            transition = po.ReactionMonitoringTransition()
            transition.setNativeID(str(i))
            chrom = self.transitionChroms[i].topyopenms(label=str(i))
            transitionGroup.addChromatogram(chrom, chrom.getNativeID())
            transitionGroup.addTransition(transition, transition.getNativeID())

        if includePrecursors:
            for i in range(len(self.precursorChroms)):
                precursor = po.ReactionMonitoringTransition()
                precursor.setNativeID('p' + str(i))
                chrom = self.precursorChroms[i].topyopenms(label='p' + str(i))
                transitionGroup.addChromatogram(chrom, chrom.getNativeID())
                transitionGroup.addTransition(transition, transition.getNativeID())
        return transitionGroup
    
    def max(self, boundary: Tuple(float, float), level: Optional(str) = 'ms1ms2') -> float:
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
            intens = c.max(boundary)
            if intens > highest_intensity:
                highest_intensity = intens

        return highest_intensity
    

    def _resolveLevel(self, level):
        if level=='ms1':
            return self.precursorChroms
        elif level=='ms2':
            return self.transitionChroms
        elif level=='ms1ms2':
            return self.precursorChroms + self.transitionChroms
        else:
            raise ValueError("Level must be one of ['ms1', 'ms2', 'ms1ms2']")

    def sum(self, boundary: Tuple(float, float), level: str = 'ms2') -> float:
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
    
    def flatten(self, level: str = 'ms2') -> Chromatogram:
        '''
        Flatten the TransitionGroup into a single Chromatogram
        '''
        chroms = self._resolveLevel(level)
        rt = []
        intensity = []
        for c in chroms:
            rt.extend(c.rt)
            intensity.extend(c.intensity)
        return Chromatogram(rt, intensity)

    def median(self, boundary: Optional(Tuple(float, float)) = None, level: str = 'ms2') -> float:
        """
        Calculate the median intensity of a given boundary in the chromatogram data.

        Args:
            chrom_data (list): A list of tuples containing the retention time and intensity values of a chromatogram.
            boundary (tuple): A tuple containing the left and right boundaries of the region of interest.

        Returns:
            float: The median intensity value of the data points within the given boundary.
        """

        chroms = self._resolveLevel(level)
        
        if boundary is not None:
            chroms =  chroms.filterChromatogram(boundary).median()

        chroms.flatten.median()