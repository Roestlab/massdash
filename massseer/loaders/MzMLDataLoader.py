from os.path import basename, splitext
from typing import List, Union, Literal
import numpy as np
import pandas as pd

# Loaders
from massseer.loaders.access.MzMLDataAccess import MzMLDataAccess
from massseer.loaders.GenericLoader import GenericLoader
from massseer.loaders.access.OSWDataAccess import OSWDataAccess
from massseer.loaders.access.ResultsTSVDataAccess import ResultsTSVDataAccess
from massseer.loaders.SpectralLibraryLoader import SpectralLibraryLoader
# Structs
from massseer.structs.TransitionGroup import TransitionGroup
from massseer.structs.FeatureMap import FeatureMap
from massseer.structs.TargetedDIAConfig import TargetedDIAConfig
# Utils
from massseer.util import LOGGER


class MzMLDataLoader(GenericLoader):
    '''
    Class to load data from MzMLFiles using a .osw output file or .tsv report file
    
    Attributes:
        rsltsFile: (str) The path to the report file (DIANN-TSV or OSW)
        dataFiles: (str/List[str]) The path to the mzML file(s)
        libraryFile: (str) The path to the library file (.tsv or .pqp)
        
    Methods:
        get_row_indices_for_peptide: Get the row indices in the report for a peptide and charge state
        load_report_for_precursor: Load the report file for a precursor
        load_report: Load the report file
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
        
    def loadTransitionGroups(self, pep_id: str, charge: int) -> dict[str, TransitionGroup]:
        '''
        Loads the transition group for a given peptide ID and charge across all files
        Args:
            pep_id (str): Peptide ID
            charge (int): Charge
        Return:
            dict[str, TransitionGroup]: Dictionary of TransitionGroups, with keys as filenames
        '''
        out_feature_map = self.loadFeatureMaps(pep_id, charge)

        return { run: data.to_chromatograms() for run, data in out_feature_map.items() }

    def loadFeatureMaps(self, pep_id: str, charge: int, config=TargetedDIAConfig) -> dict[str, FeatureMap]:
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
