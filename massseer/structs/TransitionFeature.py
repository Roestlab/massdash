from massseer.structs.GenericFeature import GenericFeature
from typing import Optional, Tuple

class TransitionFeature(GenericFeature):
    def __init__(self, leftWidth: Optional(float) = None, rightWidth: Optional[float] = None, areaIntensity: Optional[float] = None, peakApex: Optional[float] = None, apexIntensity: Optional[float] = None):
        super().__init__(leftWidth, rightWidth, areaIntensity)
        self.peakApex = peakApex
        self.apexIntensity = apexIntensity

    def getBoundaries(self) -> Tuple[float, float]:
        return super().getBoundaries()