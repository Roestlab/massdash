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

    def __init__(self, dataFiles: Union[str, List[str]], rsltsFile: str):
        super().__init__(rsltsFile, dataFiles, 'OpenSWATH')
        self.dataFiles = [SqMassDataAccess(f) for f in self.dataFiles_str]
        self.rsltsFile = OSWDataAccess(self.rsltsFile_str)

    def loadTransitionGroupsDf(self, pep_id: str, charge: int) -> pd.DataFrame:
        transitionMetaInfo = self.rsltsFile.getTransitionIDAnnotationFromSequence(pep_id, charge)
        precursor_id = self.rsltsFile.getPrecursorIDFromPeptideAndCharge(pep_id, charge)
        columns=['run_name', 'rt', 'intensity', 'annotation']
        if transitionMetaInfo.empty:
            return pd.DataFrame(columns=columns)
        out = {}
        for t in self.dataFiles:

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
                print(f"Warning: no data found for peptide in transition file {self.dataFiles}")

        return pd.concat(out).reset_index().drop('level_1', axis=1).rename(columns=dict(level_0='run'))

    def loadTransitionGroups(self, pep_id: str, charge: int) -> TransitionGroupCollection:
        '''
        Loads the transition group for a given peptide ID and charge across all files
        Args:
            pep_id (str): Peptide ID
            charge (int): Charge
        Returns:
            Dict[str, TransitionGroup]: Dictionary of TransitionGroups, with keys as sqMass filenames
        '''

        transitionMetaInfo = self.rsltsFile.getTransitionIDAnnotationFromSequence(pep_id, charge)
        precursor_id = self.rsltsFile.getPrecursorIDFromPeptideAndCharge(pep_id, charge)
 
        if transitionMetaInfo.empty:
            return None
        out = TransitionGroupCollection()
        for t in self.dataFiles:
            ### Get Transition chromatogram IDs

            transition_chroms = t.getDataForChromatogramsFromNativeIds(transitionMetaInfo['TRANSITION_ID'], transitionMetaInfo['ANNOTATION'])

            ### Get Precursor chromatogram IDs
            prec_chrom_ids = t.getPrecursorChromIDs(precursor_id)
            precursor_chroms = t.getDataForChromatograms(prec_chrom_ids['chrom_ids'], prec_chrom_ids['native_ids'])

            out[t.runName] = TransitionGroup(precursor_chroms, transition_chroms, pep_id, charge)
        return out

    def loadTransitionGroupFeaturesDf(self, pep_id: str, charge: int, full_meta: bool = False) -> pd.DataFrame:
        '''
        Loads a TransitionGroupFeature object from the results file to a pandas dataframe
        '''
        out = {}
        for t in self.dataFiles_str:
            runname = basename(t).split('.')[0]
            features = self.rsltsFile.getTransitionGroupFeaturesDf(runname, pep_id, charge)
            features = features.rename(columns={'ms2_mscore':'qvalue', 'RT':'consensusApex', 'Intensity':'consensusApexIntensity', 'leftWidth':'leftBoundary', 'rightWidth':'rightBoundary'})
            if not full_meta:
                features = features[['leftBoundary', 'rightBoundary', 'areaIntensity', 'qvalue', 'consensusApex', 'consensusApexIntensity']]
            out[runname] = features
        
        return pd.concat(out).reset_index().drop(columns='level_1').rename(columns=dict(level_0='run'))

    def loadTopTransitionGroupFeatureDf(self, pep_id: str, charge: int) -> pd.DataFrame:
        '''
        Loads a TransitionGroupFeature object from the results file to a pandas dataframe
        '''
        out = {}
        for t in self.dataFiles_str:
            runname = basename(t).split('.')[0]
            features = self.rsltsFile.getTopTransitionGroupFeatureDf(runname, pep_id, charge)
            features = features.rename(columns={'ms2_mscore':'qvalue', 'RT':'consensusApex', 'Intensity':'consensusApexIntensity', 'leftWidth':'leftBoundary', 'rightWidth':'rightBoundary'})
            features = features[['leftBoundary', 'rightBoundary', 'areaIntensity', 'qvalue', 'consensusApex', 'consensusApexIntensity']]
            out[t] = features
        
        return pd.concat(out).reset_index().drop(columns='level_1').rename(columns=dict(level_0='filename'))


    def __str__(self):
        return f"SqMassLoader(rsltsFile={self.rsltsFile_str}, dataFiles={self.dataFiles_str}"

    def __repr__(self):
        return f"SqMassLoader(rsltsFile={self.rsltsFile_str}, dataFiles={self.dataFiles_str}"