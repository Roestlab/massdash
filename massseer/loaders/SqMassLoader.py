
from abc import ABC, abstractmethod
from massseer.structs.TransitionGroup import TransitionGroup
from massseer.structs.TransitionGroupFeature import TransitionGroupFeature
from massseer.loaders.GenericLoader import GenericLoader
from massseer.loaders.SqMassDataAccess import SqMassDataAccess
from massseer.loaders.OSWDataAccess import OSWDataAccess
from typing import List, Dict
from os.path import basename
import pandas as pd

class SqMassLoader(GenericLoader):

    ''' 
    Class for loading Chromatograms and peak features from SqMass files and OSW files
    Inherits from GenericLoader
    '''

    def __init__(self, transitionFiles: List[str], rsltsFile: str):
        self.transitionFiles = [SqMassDataAccess(f) for f in transitionFiles]
        self.rsltsFile = OSWDataAccess(rsltsFile)

        self.transitionFiles_str = transitionFiles
        self.rsltsFile_str = rsltsFile


    def loadTransitionGroupsDf(self, pep_id: str, charge: int) -> pd.DataFrame:
        metaInfo = self.rsltsFile.getPeptideTransitionInfoShort(pep_id, charge)
        columns=['run_name', 'rt', 'intensity', 'annotation']
        if metaInfo.empty:
            return pd.DataFrame(columns=columns)
        out = {}
        for t in self.transitionFiles:
            ### Get Transition chromatogram IDs

            transition_chroms = t.getDataForChromatogramsFromNativeIdsDf(metaInfo['TRANSITION_ID'], metaInfo['ANNOTATION'])

            ### Get Precursor chromatogram IDs

            prec_chrom_ids = t.getPrecursorChromIDs(metaInfo['PRECURSOR_ID'])
            precursor_chroms = t.getDataForChromatogramsDf(prec_chrom_ids['chrom_ids'], prec_chrom_ids['native_ids'])

            # only add if there is data
            if not transition_chroms.empty or precursor_chroms.empty:
                out[t.filename] = pd.concat([precursor_chroms, transition_chroms])
            elif transition_chroms.empty:
                out[t.filename] = precursor_chroms
            elif precursor_chroms.empty:
                out[t.filename] = transition_chroms
            else:
                print(f"Warning: no data found for peptide in transition file {self.transitionFiles}")

        return pd.concat(out).reset_index().drop('level_1', axis=1).rename(columns=dict(level_0='filename'))

    def loadTransitionGroups(self, pep_id: str, charge: int) -> Dict[str, TransitionGroup]:
        '''
        Loads the transition group for a given peptide ID and charge across all files
        Args:
            pep_id (str): Peptide ID
            charge (int): Charge
        Returns:
            Dict[str, TransitionGroup]: Dictionary of TransitionGroups, with keys as sqMass filenames
        '''

        metaInfo = self.rsltsFile.getPeptideTransitionInfoShort(pep_id, charge)
        if metaInfo.empty:
            return None
        out = {}
        for t in self.transitionFiles:
            ### Get Transition chromatogram IDs

            transition_chroms = t.getDataForChromatogramsFromNativeIds(metaInfo['TRANSITION_ID'], metaInfo['ANNOTATION'])

            ### Get Precursor chromatogram IDs
            prec_chrom_ids = t.getPrecursorChromIDs(metaInfo['PRECURSOR_ID'])
            precursor_chroms = t.getDataForChromatograms(prec_chrom_ids['chrom_ids'], prec_chrom_ids['native_ids'])

            out[t] = TransitionGroup(precursor_chroms, transition_chroms, [], [], [], [])
        return out

    def loadTransitionGroupFeature(self, pep_id: str, charge: int) -> List[TransitionGroupFeature]:
        '''
        Loads a PeakFeature object from the results file
        Args:
            pep_id (str): Peptide ID
            charge (int): Charge
        Returns:
            PeakFeature: PeakFeature object containing peak boundaries, intensity and confidence
        '''
        out = {}
        for t in self.transitionFiles_str:
            runname = basename(t).split('.')[0]
            features = self.rsltsFile.getRunPrecursorPeakBoundaries(runname, pep_id, charge)
            tmp = []
            for _, i in features.iterrows():
                tmp.append(TransitionGroupFeature(i['leftWidth'], i['rightWidth'], areaIntensity=i['Intensity'], qvalue= i['ipf_mscore'] if 'ipf_mscore' in i else i['ms2_mscore'] )) 
                
                out[t] = tmp
        return out

    def loadTransitionGroupFeaturesDf(self, pep_id: str, charge: int) -> pd.DataFrame:
        '''
        Loads a TransitionGroupFeature object from the results file to a pandas dataframe
        '''
        out = {}
        for t in self.transitionFiles_str:
            runname = basename(t).split('.')[0]
            features = self.rsltsFile.getRunPrecursorPeakBoundaries(runname, pep_id, charge)
            features = features.rename(columns={'ms2_mscore':'qvalue', 'RT':'consensusApex', 'Intensity':'consensusApexIntensity', 'leftWidth':'leftBoundary', 'rightWidth':'rightBoundary'})
            features = features[['leftBoundary', 'rightBoundary', 'areaIntensity', 'qvalue', 'consensusApex', 'consensusApexIntensity']]
            out[t] = features

        return pd.concat(out).reset_index().drop(columns=['PRECURSOR_ID', 'RUN_ID']).rename(columns=dict(level_0='filename'))

    def __str__(self):
        return f"SqMassLoader(rsltsFile={self.rsltsFile_str}, transitionFiles={self.transitionFiles_str}"

    def __repr__(self):
        return f"SqMassLoader(rsltsFile={self.rsltsFile_str}, transitionFiles={self.transitionFiles_str}"
