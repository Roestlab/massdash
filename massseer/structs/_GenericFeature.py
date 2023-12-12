from abc import ABC, abstractmethod
from typing import Tuple, Optional

class GenericFeature(ABC):
    """ This is a generic peak picker class which should serve as an abstract class which future peak pickers can easily be added """

    @abstractmethod
    def __init__(self, leftBoundary: float, rightBoundary: float, areaIntensity: Optional[float] = None):
        self.leftBoundary = leftBoundary
        self.rightBoundary = rightBoundary
        self.areaIntensity = areaIntensity

    @abstractmethod
    def getBoundaries(self) -> Tuple[float, float]:
        """ Returns the boundaries of the feature """
        return (self.leftBoundary, self.rightBoundary)

