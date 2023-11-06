
from abc import ABC, abstractmethod
from massseer.structs.TransitionGroup import TransitionGroup
from massseer.structs.PeakFeature import PeakFeature
from massseer.loaders.GenericLoader import GenericLoader
from massseer.loaders.SqMassDataAccess import SqlDataAccess

class SqMassLoader(GenericLoader):
    ''' 
    Class for loading Chromatograms and peak features
    Classes which inherit from this should contain one results file and one transition file
    '''

    def loadTransitionGroup(pep_id: str, charge: int) -> TransitionGroup:
        pass

    def loadPeakFeature(pep_id: str, charge: int) -> PeakFeature:
        pass