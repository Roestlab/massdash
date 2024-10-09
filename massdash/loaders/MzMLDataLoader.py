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
from .GenericSpectrumLoader import GenericSpectrumLoader
# Structs
from ..structs import TransitionGroup, FeatureMap, TargetedDIAConfig, FeatureMapCollection, TopTransitionGroupFeatureCollection, TransitionGroupCollection
# Utils
from ..util import LOGGER


class MzMLDataLoader(GenericSpectrumLoader):
    '''
    Class to load data from MzMLFiles using a .osw output file or .tsv report file
    
    Attributes:
        rsltsFile: (str) The path to the report file (DIANN-TSV or OSW)
        dataFiles: (str/List[str]) The path to the mzML file(s)
        libraryFile: (str) The path to the library file (.tsv or .pqp)
        
    '''
    def __init__(self, **kwargs):
        super().__init__(**kwargs) 
        self.dataAccess = [MzMLDataAccess(f, 'ondisk', verbose=self.verbose) for f in self.dataFiles]
        self.has_im = np.all([d.has_im for d in self.dataAccess])
        if self.libraryAccess is None:
            raise ValueError("If .osw file is not supplied, library file is required for MzMLDataLoader to perform targeted extraction")
                   
    def loadTransitionGroups(self, pep_id: str, charge: int, config: TargetedDIAConfig, runNames: None | str |List[str]=None) -> Dict[str, TransitionGroup]:
        '''
        Loads the transition group for a given peptide ID and charge across all files

        Args:
            pep_id (str): Peptide ID
            charge (int): Charge
            config (TargetedDIAConfig): Configuration object containing the extraction parameters
            runNames (None | str | List[str]): Name of the run to extract the transition group from. If None, all runs are extracted. If str, only the specified run is extracted. If List[str], only the specified runs are extracted.
        Return:
            dict[str, TransitionGroup]: Dictionary of TransitionGroups, with keys as filenames
        '''
        out_feature_map = self.loadFeatureMaps(pep_id, charge, config, runNames=runNames)

        return TransitionGroupCollection({ run: data.to_chromatograms() for run, data in out_feature_map.items() })
    
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

        out_df =  pd.concat(out_transitions).reset_index().drop(columns='level_1').rename(columns=dict(level_0='run'))
        
        # Drop duplicate columns
        out_df = out_df.loc[:,~out_df.columns.duplicated()]
        return out_df

    def loadFeatureMaps(self, pep_id: str, charge: int, config=TargetedDIAConfig, runNames: None | str | List[str] = None) -> FeatureMapCollection:
        '''
        Loads a dictionary of FeatureMaps (where the keys are the filenames) from the results file

        Args:
            pep_id (str): Peptide ID
            charge (int): Charge
            runNames (None | str | List[str]): Name of the run to extract the feature map from. If None, all runs are extracted. If str, only the specified run is extracted. If List[str], only the specified runs are extracted.
        Returns:
            FeatureMapCollection: FeatureMapCollection containing FeatureMap objects for each file
        '''
        out = FeatureMapCollection()
        # use the first results file to get the feature location
        top_features = [ self.rsltsAccess[0].getTopTransitionGroupFeature(basename(splitext(d.filename)[0]), pep_id, charge) for d in self.dataAccess]
        self.libraryAccess.populateTransitionGroupFeatures(top_features)
        
        def _loadFeatureMap(dataAccess, top_feature):
            if top_feature is None:
                LOGGER.debug(f"No feature found for {pep_id} {charge} in {dataAccess.runName}")
                return FeatureMap()
            return dataAccess.reduce_spectra(top_feature, config)

        if runNames is None:
            for d, t in zip(self.dataAccess, top_features):
                out[d.runName] = _loadFeatureMap(d, t)
            return out
        elif isinstance(runNames, str):
            data_access = self.dataAccess[self.runNames.index(runNames)]
            top_feature = top_features[self.runNames.index(runNames)]
            out[runNames] = _loadFeatureMap(data_access, top_feature)
        elif isinstance(runNames, list):
            for r in runNames:
                for data_access, top_feature in zip(self.dataAccess, top_features):
                    if data_access.runName == r:
                        out[r] = _loadFeatureMap(data_access, top_feature)
        else:
            raise ValueError("runName must be none, a string or list of strings")

        return out