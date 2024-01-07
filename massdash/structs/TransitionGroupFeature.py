from massseer.structs.GenericFeature import GenericFeature
from typing import Optional, Tuple, List
import pandas as pd
import numpy as np

class TransitionGroupFeature(GenericFeature):
    '''
    This is a Transition group level feature object PeakFeature Object. All Peak Picking algorithms should output an object of this class 
    '''

    def __init__(self,
                 leftBoundary: float,
                 rightBoundary: float,
                 areaIntensity: Optional[float] =None, 
                 qvalue: Optional[float]=None,
                 consensusApex: Optional[float]=None, 
                 consensusApexIntensity: Optional[float]=None,
                 consensusApexIM: Optional[float]=None,
                 precursor_mz: Optional[float]=None,
                 precursor_charge: Optional[int]=None,
                 product_annotations: Optional[list[str]]=None,
                 product_mz: Optional[list[float]]=None,
                 sequence: Optional[str]=None,
                 ):
        super().__init__(leftBoundary, rightBoundary, areaIntensity=areaIntensity)
        self.consensusApex = consensusApex
        self.consensusApexIntensity = consensusApexIntensity
        self.qvalue = qvalue
        self.consensusApexIM = consensusApexIM
        self.precursor_mz = precursor_mz
        self.precursor_charge = int(precursor_charge) if precursor_charge is not None else None
        self.product_annotations = product_annotations
        self.product_mz = product_mz
        self.sequence = sequence

    def __str__(self):
        attribute_strings = [f"{key}: {getattr(self, key)}" for key in vars(self)]
        return f"{'-'*8} TransitionGroupFeature {'-'*8}\n" + "\n".join(attribute_strings)

    def __repr__(self):
        attribute_strings = [f"{key}: {getattr(self, key)}" for key in vars(self)]
        return f"{'-'*8} TransitionGroupFeature {'-'*8}\n" + "\n".join(attribute_strings)
    
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