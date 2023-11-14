
from abc import ABC, abstractmethod
from typing import List, Optional
from massseer.structs.TransitionGroupFeature import PeakFeature
from massseer.structs.TransitionGroup import TransitionGroup

class GenericPlotter(ABC):
    """ 
    This is a generic plotter class 
    """

    @abstractmethod
    def plot(self, transitionGroup: TransitionGroup, features: Optional[List[PeakFeature]] = None ):
        pass