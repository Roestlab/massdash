from massseer.structs.Chromatogram import Chromatogram
from massseer.structs.Mobilogram import Mobilogram
from massseer.structs.Spectrum import Spectrum
from massseer.structs.FeatureMap import FeatureMap
from typing import List, Optional
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


