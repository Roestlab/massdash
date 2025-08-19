"""
massdash/loaders/OpenSwathXICParquetLoader
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""


from typing import List, Dict, Union
from os.path import basename
from pandas.core.api import DataFrame as DataFrame
import pandas as pd

# Loaders
from .GenericChromatogramLoader import GenericChromatogramLoader
from .ResultsLoader import ResultsLoader
from .access import OpenSwathXICParquetAccess
# Structs
from ..structs import TransitionGroup, TransitionGroupCollection
# Utils
from massdash.util import LOGGER

class OpenSwathXICParquetLoader(GenericChromatogramLoader):

    ''' 
    Class for loading Chromatograms and peak features from SqMass files and OSW files
    Inherits from GenericChromatogramLoader
    '''

    def __init__(self, **kwargs):
        super().__init__(**kwargs) 
        self.dataAccess = [OpenSwathXICParquetAccess(f) for f in self.dataFiles]
        
    @ResultsLoader.cache_results
    def loadTransitionGroupsDf(self, pep_id: str, charge: int) -> pd.DataFrame:
        columns=['run_name', 'rt', 'intensity', 'annotation']
        out = {}
        for t in self.dataAccess:

            df =  t.getChromatogramDfFromSequenceAndCharge(pep_id, charge)
            # only add if there is data
            if not df.empty:
                out[t.runName] = df
            else:
                print(f"Warning: no data found for peptide in transition file {t.filename}")

        if out == {}:
            return pd.DataFrame(columns=columns)
        else:
            return pd.concat(out).reset_index().drop('level_1', axis=1).rename(columns=dict(level_0='run'))

    @ResultsLoader.cache_results
    def loadTransitionGroups(self, pep_id: str, charge: int, runNames: Union[None, str, List[str]] =None) -> Dict[str, TransitionGroupCollection]:
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
        
        def _assembleTransitionGroup(t):
            chroms = t.getChromatogramsFromSequenceAndCharge(pep_id, charge)
            precursorChroms = [i for i in chroms if 'precursor' in  i.label.lower()]
            transitionChroms = [i for i in chroms if 'precursor' not in  i.label.lower()]
            t.getTransitionGroupFeaturesFromSequenceAndCharge(pep_id, charge)
            return TransitionGroup(precursorChroms, transitionChroms, pep_id, charge)

        if runNames is None:
            for t in self.dataAccess:
                out[t.runName] = _assembleTransitionGroup(t) 
        elif isinstance(runNames, str):
            t = self.dataAccess[self.runNames.index(runNames)]
            out[runNames] = _assembleTransitionGroup(t)
        elif isinstance(runNames, list):
            out = TransitionGroupCollection()
            for r in runNames:
                for t in self.dataAccess:
                    if t.runName == r:
                        out[t.runName] = _assembleTransitionGroup(t) 
        else:
            raise ValueError("runName must be none, a string or list of strings")

        return out