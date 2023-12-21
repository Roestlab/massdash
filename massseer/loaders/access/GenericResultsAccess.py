from abc import ABC, abstractmethod
from massseer.structs.TransitionGroupFeature import TransitionGroupFeature
import pandas as pd

from massseer.util import LOGGER

class GenericResultsAccess(ABC):
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


