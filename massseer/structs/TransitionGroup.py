from massseer.structs.Chromatogram import Chromatogram
from typing import List, Tuple, Optional, Union
import pyopenms as po
from massseer.structs.Mobilogram import Mobilogram
from massseer.structs.Spectrum import Spectrum
from massseer.structs.FeatureMap import FeatureMap

class TransitionGroup:
    '''
    Class for Storing a transition group
    '''
    def __init__(self, precursorData: Union[List[Chromatogram], List[Mobilogram], List[Spectrum]],
                 transitionData: Union[List[Chromatogram], List[Mobilogram], List[Spectrum]]):
        self.precursorData = precursorData
        self.transitionData = transitionData
        if len(transitionData) > 0:
            self.dataType = type(transitionData[0])
        elif len(precursorData) > 0:
            self.dataType = type(precursorData[0])
        else: 
            raise ValueError("Precursor and transition data cannot both be empty")
        if len(precursorData) > 0 and len(transitionData) > 0:
            assert (self.dataType == type(transitionData[0]), "Precursor and transition data must be of the same type")
  

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
        if self.dataType == FeatureMap:
            raise NotImplementedError("Flattening FeatureMaps is not yet implemented")
        else:
            data1D = self._resolveLevel(level)
            data = []
            intensity = []
            for c in data1D:
                data.extend(c.data)
                intensity.extend(c.intensity)
            return self.dataType(data, intensity)
    

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
        return f"{'-'*8} TransitionGroup {'-'*8}\nprecursor chromatograms: {len(self.precursorData)}\ntransition chromatograms: {len(self.transitionData)}\nprecursor mobilograms: {len(self.precursorMobilos)}\ntransition mobilograms: {len(self.transitionMobilos)}\nprecursor spectra: {len(self.precursorSpectra)}\ntransition spectra: {len(self.transitionSpectra)}"

    def empty(self) -> bool:
        """
        Check if the TransitionGroup is empty.

        Returns:
            bool: True if all of the chromatograms, mobilograms, and spectra are empty, False otherwise.
        """
        return not any(chrom.empty() for chrom in self.precursorData) and any(chrom.empty() for chrom in self.transitionData) and any(mobil.empty() for mobil in self.precursorMobilos) and any(mobil.empty() for mobil in self.transitionMobilos) and any(spec.empty() for spec in self.precursorSpectra) and any(spec.empty() for spec in self.transitionSpectra)