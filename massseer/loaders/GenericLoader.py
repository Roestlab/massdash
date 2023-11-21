from abc import ABC, abstractmethod
from massseer.structs.TransitionGroup import TransitionGroup
from massseer.structs.TransitionGroupFeature import TransitionGroupFeature
from typing import List, Union

class GenericLoader(ABC):
    ''' 
    Abstract class for loading Chromatograms and peak features
    Classes which inherit from this should contain one results file and one transition file
    '''
    def __init__(self, rsltsFile: str, transitionFiles: Union[str, List[str]]):
        self.rsltsFile_str = rsltsFile
        if isinstance(transitionFiles, str):
            self.transitionFiles_str = [transitionFiles]
        else:
            self.transitionFiles_str = transitionFiles

        # These properties will be set by the child class
        self.rsltsFile = None
        self.tranisitonFiles = None

    @abstractmethod
    def loadTransitionGroups(pep_id: str, charge: int) -> dict[str, TransitionGroup]:
        '''
        Loads the transition group for a given peptide ID and charge across all files
        Args:
            pep_id (str): Peptide ID
            charge (int): Charge
        Returns:
            dict[str, TransitionGroup]: Dictionary of TransitionGroups, with keys as filenames
        '''
        pass
    @abstractmethod
    def loadTransitionGroupFeature(pep_id: str, charge: int) -> TransitionGroupFeature:
        '''
        Loads a PeakFeature object from the results file
        Args:
            pep_id (str): Peptide ID
            charge (int): Charge
        Returns:
            PeakFeature: PeakFeature object containing peak boundaries, intensity and confidence
        '''
        pass
