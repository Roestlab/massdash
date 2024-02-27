"""
massdash/structs/TransitionGroupFeature
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

from typing import Optional, Tuple, List
import pandas as pd
import numpy as np

# Structs
from .GenericFeature import GenericFeature

class TransitionGroupFeature(GenericFeature):
    '''
    This is a Transition group level feature object PeakFeature Object. All Peak Picking algorithms should output an object of this class 

    Attributes:
        leftBoundary (float): The left boundary of the feature
        rightBoundary (float): The right boundary of the feature
        areaIntensity (float): The area intensity of the feature
        qvalue (float): The qvalue of the feature
        consensusApex (float): The consensus apex of the feature
        consensusApexIntensity (float): The consensus apex intensity of the feature
        consensusApexIM (float): The consensus apex IM of the feature
        precursor_mz (float): The precursor mz of the feature
        precursor_charge (int): The precursor charge of the feature
        product_annotations (List[str]): The product annotations of the feature
        product_mz (List[float]): The product mz of the feature
        sequence (str): The sequence of the feature
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
                 product_annotations: Optional[List[str]]=None,
                 product_mz: Optional[List[float]]=None,
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
    def toPandasDf(transitionGroupFeatureLst: List["TransitionGroupFeature"]) -> pd.DataFrame:
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