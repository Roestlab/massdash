
from typing import List
import pandas as pd

# Structs
from massseer.structs.TransitionGroup import TransitionGroup
from massseer.structs.TransitionGroupFeature import TransitionGroupFeature
# Loaders
from massseer.loaders.GenericLoader import GenericLoader
# Utils
from massseer.util import LOGGER

class reportLoader:
    '''
    Class to load a Dia-NN report file
    
    Attributes:
        report_file_path: (str) The path to the report file
        search_data: (pd.DataFrame) The search data from the report file
        chromatogram_peak_feature: (TransitionGroupFeature) The chromatogram peak feature from the report file
        mobilogram_peak_feature: (TransitionGroupFeature) The mobilogram peak feature from the report file
        
    Methods:
        get_row_indices_for_peptide: Get the row indices in the report for a peptide and charge state
        load_report_for_precursor: Load the report file for a precursor
        load_report: Load the report file
    '''
    def __init__(self, report_file_path: str) -> None:
        self.report_file_path = report_file_path
        self.search_data: pd.DataFrame = pd.DataFrame()
        self.chromatogram_peak_feature = TransitionGroupFeature(None, None)
        self.mobilogram_peak_feature = TransitionGroupFeature(None, None)
        
    def __str__(self):
        return f"{self.chromatogram_peak_feature},\n{self.mobilogram_peak_feature}"

    def get_row_indices_for_peptide(self, peptide: str, charge: int) -> List[int]:   
        '''
        Get the row indices in the report for a peptide and charge state.
        This will be used to selectively only load the rows for a peptide and charge state from the report file.
        This will search for peptide in Modified.Sequence column and charge in the Precursor.Charge
        
        Args:
            peptide: (str) The peptide sequence to search for
            charge: (int) The charge state to search for
            
        Returns:
            row_indices: (List[int]) A list of row indices for the peptide and charge state
        '''
        # First read in the two columns we need from the report file
        peptide_charge_data = pd.read_csv(self.report_file_path, sep='\t', usecols=['Modified.Sequence', 'Precursor.Charge'])
        # Filter the rows to only those which match the peptide and charge
        peptide_charge_data = peptide_charge_data[(peptide_charge_data['Modified.Sequence'] == peptide) & (peptide_charge_data['Precursor.Charge'] == charge)]
        # return the row indices and add 1 to each index to account for the header row
        return [idx + 1 for idx in peptide_charge_data.index.tolist()]
        
    def load_report_for_precursor(self, peptide: str, charge: int) -> None:
        '''
        Load the report file for a precursor
        
        Args:
            peptide: (str) The peptide sequence to search for
            charge: (int) The charge state to search for
        
        Returns:
            self: (reportLoader) The reportLoader object
        '''
        # remove any periods from the peptide sequence i.e. for N terminal modifications
        # i.e. Convert .(UniMod:1)SEGDSVGESVHGKPSVVYR to (UniMod:1)SEGDSVGESVHGKPSVVYR
        peptide_tmp = peptide.replace('.', '')
        LOGGER.debug(f"Loading report for {peptide_tmp} {charge} from {self.report_file_path}")
        # Get the row indices for the peptide and charge
        row_indices = [0] + self.get_row_indices_for_peptide(peptide_tmp, charge)

        if len(row_indices)-1 !=0:
            # Load the report file for the peptide and charge
            precursor_search_results = pd.read_csv(self.report_file_path, sep='\t', skiprows=lambda x: x not in row_indices)
            
            LOGGER.debug(f"Found {precursor_search_results.shape[0]} rows from {self.report_file_path} for feature data")

            # Save the chromatogram peak feature from the report using cols 'RT', 'RT.Start', 'RT.Stop', 'Precursor.Quantity', 'Q.Value'
            # Multiply RT by 60 to convert from minutes to seconds
            self.chromatogram_peak_feature = TransitionGroupFeature(consensusApex=precursor_search_results['RT'].iloc[0] * 60,  leftBoundary=precursor_search_results['RT.Start'].iloc[0] * 60, rightBoundary=precursor_search_results['RT.Stop'].iloc[0] * 60, areaIntensity=precursor_search_results['Precursor.Quantity'].iloc[0], qvalue=precursor_search_results['Q.Value'].iloc[0])

            # Save the mobilogram peak feature from the report using cols 'IM'
            self.mobilogram_peak_feature = TransitionGroupFeature(leftBoundary=None, rightBoundary=None,consensusApex=precursor_search_results['IM'].iloc[0])

            return self

        elif len(row_indices)-1==0:
            LOGGER.debug(f"Error: No feature results found for {peptide_tmp} {charge} in {self.report_file_path}")

            return self

    def load_report(self) -> None:
        '''
        Load the report file
        '''
        self.search_data = pd.read_csv(self.report_file_path, sep='\t')
        # rename columns
        self.search_data = self.search_data.rename(columns={'Protein.Ids': 'ProteinId', 'Stripped.Sequence': 'PeptideSequence', 'Modified.Sequence': 'ModifiedPeptideSequence', 'Q.Value': 'Qvalue', 'Precursor.Mz': 'PrecursorMz', 'Precursor.Charge': 'PrecursorCharge'})
        # Assign dummy Decoy column all 0
        self.search_data['Decoy'] = 0

class DiaNNLoader(GenericLoader):
    ''' 
    Class for loading Chromatograms and peak features
    Classes which inherit from this should contain one results file and one transition file
    
    Attributes:
        results_file_path: (str) The path to the results file
        transition_file_path: (str) The path to the transition file
        report: (reportLoader) The reportLoader object
        
    Methods:
        loadTransitionGroups: Load transition groups from the given targeted transition list
        loadTransitionGroupFeature: Load transition group features from the given targeted transition list
        load_report: Load the report file
        load_report_for_precursor: Load the report file for a precursor
    '''

    def __init__(self, results_file_path: str, verbose: bool=False) -> None:
        super().__init__(results_file_path, None)
        self.report = reportLoader(results_file_path)
        
        LOGGER.name = "DiaNNLoader"
        if verbose:
            LOGGER.setLevel("DEBUG")
        else:
            LOGGER.setLevel("INFO")

    def loadTransitionGroups(pep_id: str, charge: int) -> TransitionGroup:
        pass

    def loadTransitionGroupFeature(pep_id: str, charge: int) -> TransitionGroupFeature:
        pass

    def load_report(self) -> None:
        '''
        Load the report file
        '''
        self.report.load_report()
    
    def load_report_for_precursor(self, peptide: str, charge: int) -> reportLoader:
        '''
        Load the report file for a precursor
        
        Args:
            peptide: (str) The peptide sequence to search for
            charge: (int) The charge state to search for
            
        Returns:
            self: (reportLoader) The reportLoader object
        '''
        return self.report.load_report_for_precursor(peptide, charge)
