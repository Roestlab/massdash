from typing import List

# Loaders
from massseer.loaders.access.SearchResultsTSVAccess import SearchResultsTSVAccess
# Utils
from massseer.util import LOGGER


class DiaNNLoader:
    ''' 
    Class to load a Dia-NN report file
    
    Attributes:
        results_file_path: (str) The path to the results file
        dataFiles: (List[str]) A list of paths to the mzML files.
        report: (SearchResultsTSVAccess) The SearchResultsTSVAccess object
        
    Methods:
        loadTransitionGroups: Load transition groups from the given targeted transition list
        loadTransitionGroupFeature: Load transition group features from the given targeted transition list
        load_report: Load the report file
        load_report_for_precursor: Load the report file for a precursor
    '''

    def __init__(self, results_file_path: str, dataFiles: List[str], verbose: bool=False) -> None:
        self.report = SearchResultsTSVAccess(results_file_path, dataFiles, verbose)
        
        LOGGER.name = "DiaNNLoader"
        if verbose:
            LOGGER.setLevel("DEBUG")
        else:
            LOGGER.setLevel("INFO")

    def __repr__(self) -> str:
        return f"DiaNNLoader(results_file_path={self.results_file_path}, verbose={self.verbose})"

    def load_report(self) -> None:
        '''
        Load the report file
        '''
        self.report.load_report()
        # rename columns
        self.report.search_data = self.search_data.rename(columns={'Protein.Ids': 'ProteinId', 'Stripped.Sequence': 'PeptideSequence', 'Modified.Sequence': 'ModifiedPeptideSequence', 'Q.Value': 'Qvalue', 'Precursor.Mz': 'PrecursorMz', 'Precursor.Charge': 'PrecursorCharge'})
        # Assign dummy Decoy column all 0
        self.report.search_data['Decoy'] = 0
    
    def load_report_for_precursor(self, peptide: str, charge: int) -> SearchResultsTSVAccess:
        '''
        Load the report file for a precursor
        
        Args:
            peptide: (str) The peptide sequence to search for
            charge: (int) The charge state to search for
            
        Returns:
            self: (SearchResultsTSVAccess) The SearchResultsTSVAccess object
        '''
        return self.report.load_report_for_precursor(peptide, charge)
