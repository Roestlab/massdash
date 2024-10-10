"""
massdash/loaders/access/GenericResultsAccess
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

from abc import ABC, abstractmethod
import pandas as pd
from typing import List, Optional, Callable, Union, Dict

# Structs
from ...structs.TransitionGroupFeature import TransitionGroupFeature
# Utils
from ...util import LOGGER

class GenericResultsAccess(ABC):
    COLUMNS = ['leftBoundary', 'rightBoundary', 'areaIntensity', 'qvalue', 'consensusApex', 'consensusApexIntensity', 'precursor_charge', 'sequence', 'software']
    def __init__(self, filename: str, verbose: bool = False) -> None:

        self.filename = filename
        LOGGER.name = __class__.__name__
        if verbose:
            LOGGER.setLevel("DEBUG")
        else:
            LOGGER.setLevel("INFO")

    @abstractmethod
    @property
    def has_im(self) -> bool:
        pass

    @property
    def columns(self) -> List[str]:
        if self.has_im:
            return self.COLUMNS.insert(7, 'consensusApexIM')
        else:
            return self.COLUMNS

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

    @abstractmethod
    def getIdentifiedPrecursors(self, qvalue: float = 0.01, run: Optional[str] = None, precursorLevel: bool = False) -> Union[set, Dict[str, set]]:
        '''
        Get the identified precursors at a certain q-value.

        Args:
            qvalue: (float) The q-value threshold for identification
            run: (str) The run name for which to get the identified precursors, if None, get for all runs
            precursorLevel: (bool) If True, return the precursor level identification, else return the peptide level identification
        Returns:
           The identified precursors across all runs (Dict[str, set]) or for a single run (set)
        '''
        pass

    @abstractmethod
    def getIdentifiedPrecursorIntensities(self, **kwargs) -> pd.DataFrame:
        '''
        Get the identified precursor intensities at a certain q-value.

        Args:
            **kwargs (dict): Additional arguments to be passed to the getIdentifiedPrecursor function
        Returns:
            The identified precursor intensities across all runs (DataFrame with columns: Precursor, runName, Intensity) or for a single run (DataFrame with columns: Precursor, Intensity)
        '''
        pass

    @abstractmethod
    def getIdentifiedProteins(self, qvalue: float, run: Optional[str] = None) -> Union[set, Dict[str, set]]:
        '''
        Get the identified proteins at a certain q-value.

        Args:
            qvalue: (float) The q-value threshold for identification
            run: (str) The run name for which to get the identified proteins, if None, get for all runs
        Returns:
            The identified proteins across all runs (Dict[str, set]) or for a single run (set)
        '''
        pass
    
    @abstractmethod
    def getIdentifiedPeptides(self, runname: str, qvalue: float, run: Optional[str] = None) -> Union[set, Dict[str, set]]:
        '''
        Get the identified peptides at a certain q-value.

        Args:
            qvalue: (float) The q-value threshold for identification
            run: (str) The run name for which to get the identified peptides, if None, get for all runs
        Returns:
            The identified peptides across all runs (Dict[str, set]) or for a single run (set)
        '''
        pass

    @abstractmethod
    def getSoftware(self) -> str:
        pass

    def getNumIdentifiedPeptides(self, qvalue: float = 0.01, run: Optional[str] = None) -> Union[int, Dict[str, int]]:
        '''
        Get the number of identified peptides at a certain q-value.

        Args:
            qvalue: (float) The q-value threshold for identification
            run: (str) The run name for which to get the identified peptides, if None, get for all runs
        Returns:
            The number of identified peptides across all runs (Dict[str, int]) or for a single run (int)
        '''
        return self._getNumIdentifiedHelper(self.getIdentifiedPeptides, run=run, qvalue=qvalue)
    
    def getNumIdentifiedProteins(self, qvalue: float = 0.01, run: Optional[str] = None) -> Union[int, Dict[str, int]]:
        '''
        Get the number of identified proteins at a certain q-value.

        Args:
            qvalue: (float) The q-value threshold for identification
            run: (str) The run name for which to get the identified proteins, if None, get for all runs

        Returns:
            The number of identified proteins across all runs (Dict[str, int]) or for a single run (int)
        '''
        return self._getNumIdentifiedHelper(self.getIdentifiedProteins, run=run, qvalue=qvalue)
    
    def getNumIdentifiedPrecursors(self, qvalue: float = 0.01, run: Optional[str] = None, precursorLevel=True) -> Union[int, Dict[str, int]]:
        '''
        Get the number of identified precursors at a certain q-value.

        Args:
            qvalue: (float) The q-value threshold for identification
            run: (str) The run name for which to get the identified precursors, if None, get for all runs
            precursorLevel: (bool) If True, only check precursors qvalue, else check qvalue at precursor/peptide/protein level
        '''
        return self._getNumIdentifiedHelper(self.getIdentifiedPrecursors, run=run, qvalue=qvalue, precursorLevel=precursorLevel)
    
    def _getNumIdentifiedHelper(self, function: Callable, run: Optional[str] = None, **kwargs) -> Union[int, Dict[str, int]]:
        '''
        Helper Function for getting the counts of identified precursors/peptides/proteins
        '''
        if isinstance(run, str):
            return len(function(run=run, **kwargs))
        else: # get for all runs
            tmp =  function(**kwargs)
            return { k: len(v) for k, v in tmp.items()}
        
    def getPrecursorCVs(self, **kwargs) -> pd.DataFrame:
        """
        Returns a DataFrame with the coefficient of variation for each precursor.

        Args:
            **kwargs (dict): Additional arguments to be passed to the getIdentifiedPrecursors function
        """
        intensity_per_run = self.getIdentifiedPrecursorIntensities(**kwargs)
        # Calculate mean and standard deviation for each group
        df_out = intensity_per_run.groupby("Precursor").agg(
            mean_intensity=pd.NamedAgg(column="Intensity", aggfunc="mean"),
            std_intensity=pd.NamedAgg(column="Intensity", aggfunc="std")
        ).reset_index()

        # Calculate coefficient of variation
        df_out["CV"] = df_out["std_intensity"] / df_out["mean_intensity"] * 100

        return df_out
    
    def getExperimentSummary(self) -> pd.DataFrame:
        '''
        Get a summary of the experiment

        Returns:
            DataFrame: DataFrame containing the experiment summary. Each row is a run and the columns are the run metadata (# Precursors, # Pepitdes, # Proteins, Software)'
        '''
        numPrecursors = self.getNumIdentifiedPrecursors()
        numPeptides = self.getNumIdentifiedPeptides()
        numProteins = self.getNumIdentifiedProteins()

        index = list(zip(('numPrecursors', 'numPeptides', 'numProteins'), (self.getSoftware(),)*3))

        df = pd.DataFrame([numPrecursors, numPeptides, numProteins], index=index).T
        df.columns = pd.MultiIndex.from_tuples(df.columns, names=['metric', 'software'])
        return df

