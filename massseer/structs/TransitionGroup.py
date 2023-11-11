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
    def __init__(self, precursorChroms: List[Chromatogram], transitionChroms: List[Chromatogram], precursorMobilos: Optional[List[Mobilogram]], transitionMobilos: Optional[List[Mobilogram]], precursorSpectra: Optional[List[Spectrum]], transitionSpectra: Optional[List[Spectrum]], targeted_transition_list: Optional[pd.DataFrame] = None):
        self.precursorChroms = precursorChroms
        self.transitionChroms = transitionChroms
        self.precursorMobilos = precursorMobilos
        self.transitionMobilos = transitionMobilos
        self.precursorSpectra = precursorSpectra
        self.transitionSpectra = transitionSpectra
        self.targeted_transition_list = targeted_transition_list

    def __str__(self) -> str:
        '''
        Returns a string representation of the transition group.

        Returns:
            str: A string representation of the transition group.
        '''

        return f"{'-'*8} TransitionGroup {'-'*8}\nprecursor chromatograms: {len(self.precursorChroms)}\ntransition chromatograms: {len(self.transitionChroms)}\nprecursor mobilograms: {len(self.precursorMobilos)}\ntransition mobilograms: {len(self.transitionMobilos)}\nprecursor spectra: {len(self.precursorSpectra)}\ntransition spectra: {len(self.transitionSpectra)}"

    def empty(self) -> bool:
        """
        Check if the TransitionGroup is empty.

        Returns:
            bool: True if all of the chromatograms, mobilograms, and spectra are empty, False otherwise.
        """
        return not any(chrom.empty() for chrom in self.precursorChroms) or any(chrom.empty() for chrom in self.transitionChroms) or any(mobil.empty() for mobil in self.precursorMobilos) or any(mobil.empty() for mobil in self.transitionMobilos) or any(spec.empty() for spec in self.precursorSpectra) or any(spec.empty() for spec in self.transitionSpectra)

    @classmethod
    def from_feature_map(cls, feature_map: FeatureMap, targeted_transition_list: Optional[pd.DataFrame] = None):
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
            precursorMobilos = [Mobilogram([], [], 'precursor mobilogram')]
            transitionMobilos = [Mobilogram([], [], 'transition mobilogram')]
        precursorSpectra = feature_map.get_precursor_spectra()
        transitionSpectra = feature_map.get_transition_spectra()
        return cls(precursorChroms, transitionChroms, precursorMobilos, transitionMobilos, precursorSpectra, transitionSpectra, targeted_transition_list)


