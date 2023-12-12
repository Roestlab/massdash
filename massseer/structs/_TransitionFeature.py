from typing import Optional, Tuple, List
import pandas as pd
import numpy as np


from ._GenericFeature import GenericFeature

class TransitionFeature(GenericFeature):
    def __init__(self, 
                 leftBoundary: Optional[float] = None, 
                 rightBoundary: Optional[float] = None, 
                 areaIntensity: Optional[float] = None, 
                 peakApex: Optional[float] = None,
                 apexIntensity: Optional[float] = None):
        super().__init__(leftBoundary, rightBoundary, areaIntensity)
        self.peakApex = peakApex
        self.apexIntensity = apexIntensity

    def getBoundaries(self) -> Tuple[float, float]:
        return super().getBoundaries()

    @staticmethod
    def toPandasDf(transitionFeatureLst: List["TransitionFeature"]) -> pd.DataFrame:
        '''
        Convert a list of TransitionFeature objects to a pandas dataframe
        '''
        leftBoundaries = [i.leftBoundary for i in transitionFeatureLst ]
        rightBoundaries = [i.rightBoundary for i in transitionFeatureLst ]
        areaIntensities = [i.areaIntensity for i in transitionFeatureLst ]
        peakApexes = [i.peakApex for i in transitionFeatureLst ]
        apexIntensities = [i.apexIntensity for i in transitionFeatureLst ]

        return pd.DataFrame(np.column_stack([leftBoundaries, rightBoundaries, areaIntensities, peakApexes, apexIntensities]), 
                            columns=['leftBoundary', 'rightBoundary', 'areaIntensity', 'peakApex', 'apexIntensity'])
