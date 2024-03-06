"""
massdash/loaders/access/GenericResultsAccess
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

from abc import ABC, abstractmethod
import pandas as pd
from typing import List, Optional

# Structs
from ...structs.TransitionGroupFeature import TransitionGroupFeature
# Utils
from ...util import LOGGER

class GenericResultsAccess(ABC):
    COLUMNS = ['leftBoundary', 'rightBoundary', 'areaIntensity', 'qvalue', 'consensusApex', 'consensusApexIntensity', 'precursor_charge', 'sequence', 'software']
    def __init__(self, filename: str, verbose: bool = False) -> None:
        LOGGER.name = __class__.__name__
        if verbose:
            LOGGER.setLevel("DEBUG")
        else:
            LOGGER.setLevel("INFO")

    @abstractmethod
    def getTransitionGroupFeatures(self, runname: str, pep: str, charge: int) -> TransitionGroupFeature:
        pass

    @abstractmethod
    def getTransitionGroupFeaturesDf(self, runname: str, pep: str, charge: int) -> pd.DataFrame:
        pass

    @abstractmethod
    def getTopTransitionGroupFeature(self, runname: str, pep: str, charge: int) -> TransitionGroupFeature:
        pass

    @abstractmethod
    def getRunNames(self) -> List[str]:
        pass

    '''
    @abstractmethod
    def getIdentifiedPrecursors(self, qvalue: float) -> set:
        pass

    @abstractmethod
    def getIdentifiedPrecursorsDf(self, qvalue: float, columns: Optional[List]=[]) -> pd.DataFrame:
        pass

    @abstractmethod
    def getIdentifiedProteins(self, qvalue: float) -> set:
        pass

    @abstractmethod
    def getIdentifiedProteinsDf(self, qvalue: float, columns: Optional[List]=[]) -> pd.DataFrame:
        pass
    '''

