from massseer.structs.Chromatogram import Chromatogram
from typing import List, Tuple, Optional
import pyopenms as po
from massseer.structs.Mobilogram import Mobilogram
from massseer.structs.Spectrum import Spectrum
from massseer.structs.FeatureMap import FeatureMap
import pandas as pd

class TransitionGroup:
    '''
    Class for Storing a transition group
    '''
    def __init__(self, precursorChroms: List[Chromatogram], transitionChroms: List[Chromatogram], precursorMobilos: Optional[List[Mobilogram]], transitionMobilos: Optional[List[Mobilogram]], precursorSpectra: Optional[List[Spectrum]], transitionSpectra: Optional[List[Spectrum]]):
        self.precursorChroms = precursorChroms
        self.transitionChroms = transitionChroms
        self.precursorMobilos = precursorMobilos
        self.transitionMobilos = transitionMobilos
        self.precursorSpectra = precursorSpectra
        self.transitionSpectra = transitionSpectra
        self._protein = None

    def to_pyopenms(self, includePrecursors=True):
        '''
        Converts the TransitionGroup to an OpenMS TransitionGroup
        '''
        transitionGroup = po.MRMTransitionGroupCP()
        for i in range(len(self.transitionChroms)):
            transition = po.ReactionMonitoringTransition()
            transition.setNativeID(str(i))
            chrom = self.transitionChroms[i].to_pyopenms(id=str(i))
            transitionGroup.addChromatogram(chrom, chrom.getNativeID())
            transitionGroup.addTransition(transition, transition.getNativeID())

        if includePrecursors:
            for i in range(len(self.precursorChroms)):
                precursor = po.ReactionMonitoringTransition()
                precursor.setNativeID('p' + str(i))
                chrom = self.precursorChroms[i].to_pyopenms(id='p' + str(i))
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

    def median(self, boundary: Optional[Tuple[float, float]] = None, level: Optional[str] = 'ms2') -> float:
        """
        Calculate the median intensity of a given boundary in the chromatogram data.

        Args:
            chrom_data (list): A list of tuples containing the retention time and intensity values of a chromatogram.
            boundary (tuple): A tuple containing the left and right boundaries of the region of interest.

        Returns:
            float: The median intensity value of the data points within the given boundary.
        """

        chrom_flattened = self.flatten(level)
        if boundary is not None:
            chrom_flattened = chrom_flattened.filterChromatogram(boundary)

        return chrom_flattened.median()
    def __str__(self) -> str:
        '''
        Returns a string representation of the transition group.

        Returns:
            str: A string representation of the transition group.
        '''
        return f"{'-'*8} TransitionGroup {'-'*8}\nprecursor chromatograms: {len(self.precursorChroms)}\ntransition chromatograms: {len(self.transitionChroms)}\nprecursor mobilograms: {len(self.precursorMobilos)}\ntransition mobilograms: {len(self.transitionMobilos)}\nprecursor spectra: {len(self.precursorSpectra)}\ntransition spectra: {len(self.transitionSpectra)}\n{self.protein}"

    @property
    def protein(self):
        """
        Returns the protein associated with this transition group.
        """
        return self._protein

    @protein.setter
    def protein(self, value):
        """
        Sets the protein associated with this transition group.
        """
        self._protein = value


    @classmethod
    def from_feature_map(cls, feature_map: FeatureMap):
        """
        Creates a TransitionGroup object from a pandas DataFrame containing feature information.

        Args:
            feature_map (FeatureMap): A FeatureMap containing mass spec feature information.

        Returns:
            cls: A TransitionGroup object.
        """
        precursorChroms = feature_map.get_precursor_chromatograms()
        transitionChroms = feature_map.get_transition_chromatograms()
        if feature_map.has_im:
            precursorMobilos = feature_map.get_precursor_mobilograms()
            transitionMobilos = feature_map.get_transition_mobilograms()
        else:
            precursorMobilos = None
            transitionMobilos = None
        precursorSpectra = feature_map.get_precursor_spectra()
        transitionSpectra = feature_map.get_transition_spectra()
        return cls(precursorChroms, transitionChroms, precursorMobilos, transitionMobilos, precursorSpectra, transitionSpectra)