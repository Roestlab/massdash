
from abc import ABC, abstractmethod
from massseer.structs.TransitionGroup import TransitionGroup
from massseer.structs.PeakFeature import PeakFeature
from massseer.loaders.GenericLoader import GenericLoader
from massseer.loaders.SqMassDataAccess import SqMassDataAccess
from massseer.loaders.OSWDataAccess import OSWDataAccess
from typing import List, Dict
from os.path import basename

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

    def loadTransitionGroups(self, pep_id: str, charge: int) -> Dict[str, TransitionGroup]:
        '''
        Loads the transition group for a given peptide ID and charge across all files
        Args:
            pep_id (str): Peptide ID
            charge (int): Charge
        Returns:
            Dict[str, TransitionGroup]: Dictionary of TransitionGroups, with keys as sqMass filenames
        '''

        metaInfo = self.rsltsFile.getPeptideTransitionInfo(pep_id, charge)
        if metaInfo.empty:
            return None
        out = {}
        for t in self.transitionFiles:
            ### Get Transition chromatogram IDs
            transition_chroms = t.getDataForChromatograms(metaInfo['TRANSITION_ID'], metaInfo['PRODUCT_ANNOTATION'])

            ### Get Precursor chromatogram IDs
            prec_chrom_ids = t.getPrecursorChromIDs(metaInfo['PRECURSOR_ID'].iloc[0])
            precursor_chroms = t.getDataForChromatograms(prec_chrom_ids['chrom_ids'], prec_chrom_ids['native_ids'])

            out[t] = TransitionGroup(precursorChroms = precursor_chroms, transitionChroms=transition_chroms)
        return out

    def loadPeakFeature(self, pep_id: str, charge: int) -> List[PeakFeature]:
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
                tmp.append(PeakFeature(area_intensity=i['Intensity'], leftWidth=i['leftWidth'], rightWidth=i['rightWidth'], qvalue=i['ms2_mscore'])) 
                out[t] = tmp
        return out

    def __str__(self):
        return f"SqMassLoader(rsltsFile={self.rsltsFile_str}, transitionFiles={self.transitionFiles_str}"

    def __repr__(self):
        return f"SqMassLoader(rsltsFile={self.rsltsFile_str}, transitionFiles={self.transitionFiles_str}"
