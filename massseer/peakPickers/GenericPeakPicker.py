from abc import ABC, abstractmethod
from typing import List
from massseer.structs.PeakFeature import PeakFeature

class GenericPeakPicker(ABC):
    """ This is a generic peak picker class which should serve as an abstract class which future peak pickers can easily be added """

    @abstractmethod
    def pick(self) -> List[PeakFeature]:
        """ Performs Peak Picking, Should return a PeakFeatureList object """
        pass