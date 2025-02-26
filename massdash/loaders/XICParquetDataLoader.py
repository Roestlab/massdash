"""
massdash/loaders/XICParquetDataLoader
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""


from typing import List, Union
from pandas.core.api import DataFrame as DataFrame
import pandas as pd

# Loaders
from .GenericChromatogramLoader import GenericChromatogramLoader
from .ResultsLoader import ResultsLoader
from .access import XICParquetDataAccess
# Structs
from ..structs import TransitionGroupCollection
# Utils
from massdash.util import LOGGER

class XICParquetDataLoader(GenericChromatogramLoader):

    ''' 
    Class for loading Chromatograms and peak features from DIA-NNs results and XIC parquet files
    Inherits from GenericChromatogramLoader
    '''

    def __init__(self, **kwargs):
        super().__init__(**kwargs) 
        self.dataAccess = [XICParquetDataAccess(f) for f in self.dataFiles]
        
    @ResultsLoader.cache_results
    def loadTransitionGroupsDf(self, pep_id: str, charge: int) -> pd.DataFrame:
        precursor = pep_id + str(charge)

        columns=['run_name', 'rt', 'intensity', 'annotation']
        out = {}
        for t in self.dataAccess:

            ### Get Transition chromatogram IDs
            chroms = t.getTransitionDataDf(precursor)

            # only add if there is data
            if not chroms.empty:
                out[t.runName] = chroms
            else:
                print(f"Warning: no data found for peptide in transition file {t.filename}")

        if len(out) == 0:
            return pd.DataFrame(columns=columns)
        else:
            return pd.concat(out).reset_index().drop('level_1', axis=1).rename(columns=dict(level_0='run'))

    @ResultsLoader.cache_results
    def loadTransitionGroups(self, pep_id: str, charge: int, runNames: Union[None, str, List[str]] =None) -> TransitionGroupCollection:
        '''
        Loads the transition group for a given peptide ID and charge across all files
        Args:
            pep_id (str): Peptide ID
            charge (int): Charge
            runNames (None | str | List[str]): Name of the run to extract the transition group from. If None, all runs are extracted. If str, only the specified run is extracted. If List[str], only the specified runs are extracted.
        Returns:
            Dict[str, TransitionGroup]: Dictionary of TransitionGroups, with keys as sqMass filenames
        '''

        out = TransitionGroupCollection()

        if runNames is None:
            for t in self.dataAccess:
                out[t.runName] = t.getTransitionData(pep_id, charge)
        elif isinstance(runNames, str):
            t = self.dataAccess[self.runNames.index(runNames)]
            out[runNames] = t.getTransitionData(pep_id, charge)
        elif isinstance(runNames, list):
            for r in runNames:
                for t in self.dataAccess:
                    if t.runName == r:
                        out[t.runName] = t.getTransitionData(pep_id, charge)
        else:
            raise ValueError("runName must be none, a string or list of strings")

        return out

   