from abc import ABC, abstractmethod
from typing import List

# Structs
from massdash.structs.TransitionGroupFeature import TransitionGroupFeature
from massdash.structs.TransitionGroup import TransitionGroup

class GenericPeakPicker(ABC):
    """ This is a generic peak picker class which should serve as an abstract class which future peak pickers can easily be added """

    @abstractmethod
    def pick(self, transitionGroup: TransitionGroup) -> List[TransitionGroupFeature]:
        """ Performs Peak Picking, Should return a PeakFeatureList object """
        pass