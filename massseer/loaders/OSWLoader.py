import pandas as pd
from typing import List, Dict, Union

# Structs
from massseer.structs.TransitionGroupFeature import TransitionGroupFeature
# Loaders
from massseer.loaders.OSWDataAccess import OSWDataAccess
from massseer.loaders.mzMLLoader import mzMLLoader
# Utils
from massseer.util import LOGGER, file_basename_without_extension

class OSWLoader:
    """
    OSWLoader class for loading OSW files.
    
    Attributes:
        rsltsFile: (str) The path to the OSW results file.
        dataFiles: (List[str]) A list of paths to the mzML files.
        report: (OSWDataAccess) The OSW report file.
        
    Methods:
        load_report: Loads the OSW report file.
        load_report_for_precursor: Loads the OSW report file for a given peptide and charge.
    """
    def __init__(self, rsltsFile: str, dataFiles: List[str], verbose: bool=False):
        self.report = OSWDataAccess(rsltsFile)
        self.dataFiles = [mzMLLoader(f, 'ondisk') for f in dataFiles]
        self.report.search_data: pd.DataFrame = pd.DataFrame()
        self.report.chromatogram_peak_feature = TransitionGroupFeature(None, None)
        self.report.mobilogram_peak_feature = TransitionGroupFeature(None, None)
        self.report.precursor_search_data = {}
        
        LOGGER.name = "OSWLoader"
        if verbose:
            LOGGER.setLevel("DEBUG")
        else:
            LOGGER.setLevel("INFO")
        
    def __str__(self):
        return f"{self.report.chromatogram_peak_feature},\n{self.report.mobilogram_peak_feature}"
        
    def load_report(self) -> None:
        """
        Loads the OSW report file.
        """
        self.report.search_data = self.report.get_top_rank_precursor_features_across_runs()
        
    def load_report_for_precursor(self, peptide: str, charge: int) -> None:
        """
        Loads the OSW report file for a given peptide and charge.
        
        Args:
            peptide: (str) The peptide sequence to search for
            charge: (int) The charge state to search for
        """
        precursor_search_results = self.report.get_top_rank_precursor_feature(peptide, charge)
        out = {}
        if precursor_search_results.shape[0] != 0:
            for file in self.dataFiles:
                file_precursor_feature = precursor_search_results.loc[precursor_search_results['filename'].apply(file_basename_without_extension) == file_basename_without_extension(file.filename)]

                if file_precursor_feature.shape[0] == 0:
                    LOGGER.warning(f"Warning: No precursor search results found for {peptide} with charge {charge} in {file.filename}.")
                    continue
                chromatogram_peak_feature = TransitionGroupFeature(consensusApex=file_precursor_feature['RT'].iloc[0],  leftBoundary=file_precursor_feature['leftWidth'].iloc[0], rightBoundary=file_precursor_feature['rightWidth'].iloc[0], areaIntensity=file_precursor_feature['Intensity'].iloc[0], qvalue=file_precursor_feature['Qvalue'].iloc[0])

                # Save the mobilogram peak feature from the report using cols 'IM'
                mobilogram_peak_feature = TransitionGroupFeature(leftBoundary=None, rightBoundary=None,consensusApex=file_precursor_feature['IM'].iloc[0])
                
                out[file] = {'chromatogram_peak_feature': chromatogram_peak_feature, 'mobilogram_peak_feature': mobilogram_peak_feature}
            self.report.precursor_search_data = out
            return self
        
        elif precursor_search_results.shape[0] == 0:
            print(f"Warning: No precursor search results found for {peptide} with charge {charge}.")
            return self