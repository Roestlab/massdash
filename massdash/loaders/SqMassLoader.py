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

class SqMassLoader(GenericChromatogramLoader):

    ''' 
    Class for loading Chromatograms and peak features from SqMass files and OSW files
    Inherits from GenericLoader
    '''

    def __init__(self, **kwargs):
        super().__init__(**kwargs) 
        self.dataAccess = [SqMassDataAccess(f) for f in self.dataFiles]
        oswAccessFound = False
        
        ## Check for OSW file in the list of results files, OSW file is required for parsing sqMass files
        ## Currently only 
        print(self.rsltsAccess)
        for i in self.rsltsAccess:
            if not oswAccessFound and isinstance(i, OSWDataAccess):
                oswAccessFound = True
                self.oswAccess = i
            elif oswAccessFound and isinstance(i, OSWDataAccess):
                raise Exception("Only one OSW file is allowed in SqMassLoader")
        if not oswAccessFound:
            raise Exception("No OSW file found in SqMassLoader, OSW file required for parsing sqMass files")
                
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
                out[t.filename] = pd.concat([precursor_chroms, transition_chroms])
            elif transition_chroms.empty:
                out[t.filename] = precursor_chroms
            elif precursor_chroms.empty:
                out[t.filename] = transition_chroms
            else:
                print(f"Warning: no data found for peptide in transition file {t.filename}")

        return pd.concat(out).reset_index().drop('level_1', axis=1).rename(columns=dict(level_0='filename'))

    def loadTransitionGroups(self, pep_id: str, charge: int) -> TransitionGroupCollection:
        '''
        Loads the transition group for a given peptide ID and charge across all files
        Args:
            pep_id (str): Peptide ID
            charge (int): Charge
        Returns:
            Dict[str, TransitionGroup]: Dictionary of TransitionGroups, with keys as sqMass filenames
        '''

        transitionMetaInfo = self.oswAccess.getTransitionIDAnnotationFromSequence(pep_id, charge)
        precursor_id = self.oswAccess.getPrecursorIDFromPeptideAndCharge(pep_id, charge)
 
        if transitionMetaInfo.empty:
            return None
        out = {}
        for t in self.dataAccess:
            ### Get Transition chromatogram IDs

            transition_chroms = t.getDataForChromatogramsFromNativeIds(transitionMetaInfo['TRANSITION_ID'], transitionMetaInfo['ANNOTATION'])

            ### Get Precursor chromatogram IDs
            prec_chrom_ids = t.getPrecursorChromIDs(precursor_id)
            precursor_chroms = t.getDataForChromatograms(prec_chrom_ids['chrom_ids'], prec_chrom_ids['native_ids'])

            out[t] = TransitionGroup(precursor_chroms, transition_chroms, pep_id, charge)
        return out