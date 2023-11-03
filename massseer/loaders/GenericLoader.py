from abc import ABC, abstractmethod
from massseer.structs.TransitionGroup import TransitionGroup
from massseer.structs.PeakFeature import PeakFeature

class GenericLoader(ABC):
    ''' 
    Abstract class for loading Chromatograms and peak features
    Classes which inherit from this should contain one results file and one transition file
    '''
    def __init__(self, rsltsFile, transitionFile):
        self.rsltsFile = rsltsFile
        self.transitionFile = transitionFile

    @abstractmethod
    def loadTransitionGroup(pep_id: str, charge: int) -> TransitionGroup:
        pass
    @abstractmethod
    def loadPeakFeature(pep_id: str, charge: int) -> PeakFeature:
        pass