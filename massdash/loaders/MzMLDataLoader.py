"""
massdash/loaders/MzMLDataLoader
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

from os.path import basename, splitext
from typing import Dict, List, Union, Literal
import numpy as np
import pandas as pd

# Loaders
from .access.MzMLDataAccess import MzMLDataAccess
from .GenericLoader import GenericLoader
from .access.OSWDataAccess import OSWDataAccess
from .access.ResultsTSVDataAccess import ResultsTSVDataAccess
from .SpectralLibraryLoader import SpectralLibraryLoader
# Structs
from ..structs.TransitionGroup import TransitionGroup
from ..structs.FeatureMap import FeatureMap
from ..structs.TargetedDIAConfig import TargetedDIAConfig
# Utils
from ..util import LOGGER


class MzMLDataLoader(GenericLoader):
    '''
    Class to load data from MzMLFiles using a .osw output file or .tsv report file
    
    Attributes:
        rsltsFile: (str) The path to the report file (DIANN-TSV or OSW)
        dataFiles: (str/List[str]) The path to the mzML file(s)
        libraryFile: (str) The path to the library file (.tsv or .pqp)
        
    '''
    def __init__(self, rsltsFile: str, dataFiles: Union[str, List[str]], libraryFile: str = None, rsltsFileType: Literal['OpenSWATH', 'DIA-NN'] = 'OpenSWATH', verbose: bool=False, mode: Literal['module', 'gui'] = 'module') -> None:
        super().__init__(rsltsFile, dataFiles, libraryFile, rsltsFileType, verbose, mode)
        self.dataFiles = [MzMLDataAccess(f, 'ondisk', verbose=verbose) for f in self.dataFiles_str]
        self.has_im = np.all([d.has_im for d in self.dataFiles])
                   
    def loadTopTransitionGroupFeatureDf(self, pep_id: str, charge: int) -> pd.DataFrame:
        '''
        Loads a pandas dataframe of TransitionGroupFeatures across all runsPeakFeature object from the results file

        Args:
            pep_id (str): Peptide ID
            charge (int): Charge
        Returns:
            DataFrame: DataFrame containing TransitionGroupObject information across all runs 
        '''
        out = {}
        for t in self.dataFiles:
            runname = basename(t.filename).split('.')[0]
            out[t.filename] = self.rsltsFile.getTopTransitionGroupFeatureDf(runname, pep_id, charge)
        return pd.concat(out).reset_index().drop(columns='level_1').rename(columns=dict(level_0='filename'))
        
    def loadTransitionGroupFeaturesDf(self, pep_id: str, charge: int) -> pd.DataFrame:
        '''
        Loads a pandas dataframe of TransitionGroupFeatures across all runsPeakFeature object from the results file

        Args:
            pep_id (str): Peptide ID
            charge (int): Charge

        Returns:
            DataFrame: DataFrame containing TransitionGroupObject information across all runs 
        '''
        out = {}
        for t in self.dataFiles:
            runname = basename(t.filename).split('.')[0]
            out[t.filename] = self.rsltsFile.getTransitionGroupFeaturesDf(runname, pep_id, charge)
        return pd.concat(out).reset_index().drop(columns='level_1').rename(columns=dict(level_0='filename'))
        
    def loadTransitionGroups(self, pep_id: str, charge: int, config: TargetedDIAConfig) -> Dict[str, TransitionGroup]:
        '''
        Loads the transition group for a given peptide ID and charge across all files

        Args:
            pep_id (str): Peptide ID
            charge (int): Charge
            config (TargetedDIAConfig): Configuration object containing the extraction parameters
        Return:
            dict[str, TransitionGroup]: Dictionary of TransitionGroups, with keys as filenames
        '''
        out_feature_map = self.loadFeatureMaps(pep_id, charge, config)

        return { run: data.to_chromatograms() for run, data in out_feature_map.items() }
    
    def loadTransitionGroupsDf(self, pep_id: str, charge: int, config: TargetedDIAConfig) -> Dict[str, pd.DataFrame]:
        '''
        Loads the transition group for a given peptide ID and charge across all files into a pandas DataFrame
        
        Args:
            pep_id (str): Peptide ID
            charge (int): Charge
            config (TargetedDIAConfig): Configuration object containing the extraction parameters
        
        Return:
            dict[str, pd.DataFrame]: Dictionary of TransitionGroups, with keys as filenames
        '''
        out_feature_map = self.loadFeatureMaps(pep_id, charge, config)

        # for each run, groupby intensity and rt to get chromatogram
        out_transitions = { run:df.feature_df[['Annotation', 'int', 'rt']].groupby(['Annotation', 'rt']).sum().reset_index() for run, df in out_feature_map.items() }

        return pd.concat(out_transitions).reset_index().drop(columns='level_1').rename(columns=dict(level_0='filename'))

    def loadFeatureMaps(self, pep_id: str, charge: int, config=TargetedDIAConfig) -> Dict[str, FeatureMap]:
        '''
        Loads a dictionary of FeatureMaps (where the keys are the filenames) from the results file

        Args:
            pep_id (str): Peptide ID
            charge (int): Charge
        Returns:
            FeatureMap: FeatureMap object containing peak boundaries, intensity and confidence
        '''
        out = {}
        top_features = [ self.rsltsFile.getTopTransitionGroupFeature(basename(splitext(d.filename)[0]), pep_id, charge) for d in self.dataFiles]
        self.libraryFile.populateTransitionGroupFeatures(top_features)
        for d, t in zip(self.dataFiles, top_features):
            if t is None:
                LOGGER.debug(f"No feature found for {pep_id} {charge} in {d.filename}")
                return FeatureMap()
            else:
                out[d.filename] = d.reduce_spectra(t, config)
        return out
