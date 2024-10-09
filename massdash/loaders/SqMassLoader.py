"""
massdash/loaders/SqMassLoader
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""


from typing import List, Dict, Union
from os.path import basename
from pandas.core.api import DataFrame as DataFrame
import pandas as pd

# Loaders
from .GenericChromatogramLoader import GenericChromatogramLoader
from .access.SqMassDataAccess import SqMassDataAccess
from .access.OSWDataAccess import OSWDataAccess
# Structs
from ..structs import TransitionGroup, TransitionGroupCollection
# Utils
from massdash.util import LOGGER

class SqMassLoader(GenericChromatogramLoader):

    ''' 
    Class for loading Chromatograms and peak features from SqMass files and OSW files
    Inherits from GenericLoader
    '''

    def __init__(self, **kwargs):
        super().__init__(**kwargs) 
        self.dataAccess = [SqMassDataAccess(f) for f in self.dataFiles]
        
        ## Check for OSW file in the list of results files, OSW file is required for parsing sqMass files
        ## Currently only 
        self.oswAccess = self.getOSWAccessPtr()
        if self.oswAccess is None:
            raise ValueError("No OSW file found in SqMassLoader, OSW file required for parsing sqMass files")
                
    def loadTransitionGroupsDf(self, pep_id: str, charge: int) -> pd.DataFrame:
        transitionMetaInfo = self.oswAccess.getTransitionIDAnnotationFromSequence(pep_id, charge)
        precursor_id = self.oswAccess.getPrecursorIDFromPeptideAndCharge(pep_id, charge)
        columns=['run_name', 'rt', 'intensity', 'annotation']
        if transitionMetaInfo.empty:
            return pd.DataFrame(columns=columns)
        out = {}
        for t in self.dataAccess:

            ### Get Transition chromatogram IDs
            transition_chroms = t.getDataForChromatogramsFromNativeIdsDf(transitionMetaInfo['TRANSITION_ID'], transitionMetaInfo['ANNOTATION'])

            ### Get Precursor chromatogram IDs
            prec_chrom_ids = t.getPrecursorChromIDs(precursor_id) 
            precursor_chroms = t.getDataForChromatogramsDf(prec_chrom_ids['chrom_ids'], prec_chrom_ids['native_ids'])

            # only add if there is data
            if not transition_chroms.empty or precursor_chroms.empty:
                out[t.runName] = pd.concat([precursor_chroms, transition_chroms])
            elif transition_chroms.empty:
                out[t.runName] = precursor_chroms
            elif precursor_chroms.empty:
                out[t.runName] = transition_chroms
            else:
                print(f"Warning: no data found for peptide in transition file {t.filename}")

        return pd.concat(out).reset_index().drop('level_1', axis=1).rename(columns=dict(level_0='run'))

    def loadTransitionGroups(self, pep_id: str, charge: int, runNames: None | str | List[str] =None) -> Dict[str, TransitionGroupCollection]:
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
        transitionMetaInfo = self.oswAccess.getTransitionIDAnnotationFromSequence(pep_id, charge)
        precursor_id = self.oswAccess.getPrecursorIDFromPeptideAndCharge(pep_id, charge)
 
        if transitionMetaInfo.empty:
            return None
        
        def _loadTransitionGroup(dataAccess):
            '''
            Helper function to load TransitionGroup
            '''
            transition_chroms = dataAccess.getDataForChromatogramsFromNativeIds(transitionMetaInfo['TRANSITION_ID'], transitionMetaInfo['ANNOTATION'])
            prec_chrom_ids = dataAccess.getPrecursorChromIDs(precursor_id)
            precursor_chroms = dataAccess.getDataForChromatograms(prec_chrom_ids['chrom_ids'], prec_chrom_ids['native_ids'])
            return TransitionGroup(precursor_chroms, transition_chroms, pep_id, charge)

        if runNames is None:
            for t in self.dataAccess:
                out[t.runName] = _loadTransitionGroup(t)
        elif isinstance(runNames, str):
            t = self.dataAccess[self.runNames.index(runNames)]
            out[runNames] = _loadTransitionGroup(t)
        elif isinstance(runNames, list):
            out = TransitionGroupCollection()
            for r in runNames:
                for t in self.dataAccess:
                    if t.runName == r:
                        out[t.runName] = _loadTransitionGroup(t)
        else:
            raise ValueError("runName must be none, a string or list of strings")

        return out