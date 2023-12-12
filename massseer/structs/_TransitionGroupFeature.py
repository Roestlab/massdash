from typing import Optional, Tuple, List
import pandas as pd
import numpy as np

#Internal imports
from ._GenericFeature import GenericFeature

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
        return f"{'-'*8} TransitionGroupFeature {'-'*8}\nApex: {self.consensusApex}\nLeftWidth: {self.leftBoundary}\nRightWidth: {self.rightBoundary}\nArea: {self.areaIntensity}\nQvalue: {self.qvalue}"

    def __repr__(self):
        return f"TransitionGroupFeature Apex: {self.consensusApex} LeftWidth: {self.leftBoundary} RightWidth: {self.rightBoundary} Area: {self.areaIntensity} Qvalue: {self.qvalue}"
    
    def getBoundaries(self) -> Tuple[float, float]:
        return super().getBoundaries()

    @staticmethod
    def toPanadsDf(transitionGroupFeatureLst: List["TransitionGroupFeature"]) -> pd.DataFrame:
        '''
        Convert a list of TransitionGroupFeature objects to a pandas dataframe
        '''
        leftBoundaries = [i.leftBoundary for i in transitionGroupFeatureLst ]
        rightBoundaries = [i.rightBoundary for i in transitionGroupFeatureLst ]
        areaIntensities = [i.areaIntensity for i in transitionGroupFeatureLst ]
        qvalues = [i.qvalue for i in transitionGroupFeatureLst ]
        consensusApexes = [i.consensusApex for i in transitionGroupFeatureLst ]
        consensusApexIntensities = [i.consensusApexIntensity for i in transitionGroupFeatureLst ]

        return pd.DataFrame(np.column_stack([leftBoundaries, rightBoundaries, areaIntensities, qvalues, consensusApexes, consensusApexIntensities]),
                            columns=['leftBoundary', 'rightBoundary', 'areaIntensity', 'qvalue', 'consensusApex', 'consensusApexIntensity'])