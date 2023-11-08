from massseer.structs.GenericFeature import GenericFeature
from typing import Optional, Tuple

class TransitionGroupFeature(GenericFeature):
    '''
    This is a Transition group level feature object PeakFeature Object. All Peak Picking algorithms should output an object of this class 
    '''

    def __init__(self, leftBoundary, rightBoundary, areaIntensity: Optional[float] =None, qvalue: Optional[float]=None, consensusApex: Optional[float]=None, consensusApexIntensity: Optional[float]=None):
        super().__init__(leftBoundary, rightBoundary, areaIntensity=areaIntensity)
        self.consensusApex = consensusApex
        self.consensusApexIntensity = consensusApexIntensity
        self.qvalue = qvalue

    def __str__(self):
        return f"{'-'*8} PeakFeature {'-'*8}\nApex: {self.consensusApex}\nLeftWidth: {self.leftBoundary}\nRightWidth: {self.rightBoundary}\nArea: {self.areaIntensity}\nQvalue: {self.qvalue}"

    def __repr__(self):
        return f"PeakFeature Apex: {self.consensusApex} LeftWidth: {self.leftBoundary} RightWidth: {self.rightBoundary} Area: {self.areaIntensity} Qvalue: {self.qvalue}"
    
    def getBoundaries(self) -> Tuple[float, float]:
        return super().getBoundaries()