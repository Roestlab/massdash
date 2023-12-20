from abc import ABC, abstractmethod
from massseer.structs.TransitionGroupFeature import TransitionGroupFeature

class GenericResultsAccess(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def getTransitionGroupFeatures(self, runname: str, pep: str, charge: int) -> TransitionGroupFeature:
        pass

    @abstractmethod
    def getTransitionGroupFeaturesDf(self, runname: str, pep: str, charge: int) -> pd.DataFrame:
        pass


