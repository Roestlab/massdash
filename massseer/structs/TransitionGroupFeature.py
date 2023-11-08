from massseer.structs.GenericFeature import GenericFeature
from typing import Optional

class TransitionGroupFeature(GenericFeature):
    '''
    This is a Transition group level feature object PeakFeature Object. All Peak Picking algorithms should output an object of this class 
    '''

    def __init__(self, leftBoundary, rightBoundary, area_intensity: Optional(float) =None, qvalue: Optional(float)=None, consensusApex: Optional(float)=None, consensusApexIntensity: Optional(float)=None):
        super.__init__(leftBoundary, rightBoundary, area_intensity=area_intensity)
        self.consensusApex = consensusApex
        self.consensusApexIntensity = consensusApexIntensity
        self.qvalue = qvalue

    def __str__(self):
        return f"{'-'*8} PeakFeature {'-'*8}\nApex: {self.apex}\nLeftWidth: {self.leftBoundary}\nRightWidth: {self.rightBoundary}\nArea: {self.area_intensity}\nQvalue: {self.qvalue}"

    def __repr__(self):
        return f"PeakFeature Apex: {self.apex} LeftWidth: {self.leftBoundary} RightWidth: {self.rightBoundary} Area: {self.area_intensity} Qvalue: {self.qvalue}"