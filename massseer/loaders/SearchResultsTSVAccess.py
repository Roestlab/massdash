
from typing import List
import pandas as pd

# Structs
from massseer.structs.TransitionGroupFeature import TransitionGroupFeature
# Loaders
from massseer.loaders.mzMLDataAccess import mzMLDataAccess
# Utils
from massseer.util import LOGGER

class SearchResultsTSVAccess:
    '''
    Class to load a TSV based searchs results report file
    
    Attributes:
        filename: (str) The path to the report file
        search_data: (pd.DataFrame) The search data from the report file
        chromatogram_peak_feature: (TransitionGroupFeature) The chromatogram peak feature from the report file
        mobilogram_peak_feature: (TransitionGroupFeature) The mobilogram peak feature from the report file
        
    Methods:
        get_row_indices_for_peptide: Get the row indices in the report for a peptide and charge state
        load_report_for_precursor: Load the report file for a precursor
        load_report: Load the report file
    '''
    def __init__(self, filename: str, dataFiles: List[str], verbose: bool=False) -> None:
        self.filename = filename
        self.dataFiles = [mzMLDataAccess(f, 'ondisk') for f in dataFiles]
        self.search_data: pd.DataFrame = pd.DataFrame()
        self.chromatogram_peak_feature = TransitionGroupFeature(None, None)
        self.mobilogram_peak_feature = TransitionGroupFeature(None, None)
        self.precursor_search_data = {}
        
        LOGGER.name = "SearchResultsTSVAccess"
        if verbose:
            LOGGER.setLevel("DEBUG")
        else:
            LOGGER.setLevel("INFO")
            
    def __str__(self):
        return f"{self.chromatogram_peak_feature},\n{self.mobilogram_peak_feature}"
    
    def __repr__(self) -> str:
        return f"SearchResultsTSVAccess(filename={self.filename})"

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
        peptide_charge_data = pd.read_csv(self.filename, sep='\t', usecols=['Modified.Sequence', 'Precursor.Charge'])
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
            self: (SearchResultsTSVAccess) The SearchResultsTSVAccess object
        '''
        # remove any periods from the peptide sequence i.e. for N terminal modifications
        # i.e. Convert .(UniMod:1)SEGDSVGESVHGKPSVVYR to (UniMod:1)SEGDSVGESVHGKPSVVYR
        peptide_tmp = peptide.replace('.', '')
        LOGGER.debug(f"Loading report for {peptide_tmp} {charge} from {self.filename}")
        # Get the row indices for the peptide and charge
        row_indices = [0] + self.get_row_indices_for_peptide(peptide_tmp, charge)
        out = {}
        if len(row_indices)-1 !=0:
            for file in self.dataFiles:
                # Load the report file for the peptide and charge
                precursor_search_results = pd.read_csv(self.filename, sep='\t', skiprows=lambda x: x not in row_indices)
                
                LOGGER.debug(f"Found {precursor_search_results.shape[0]} rows from {self.filename} for feature data")

                # Save the chromatogram peak feature from the report using cols 'RT', 'RT.Start', 'RT.Stop', 'Precursor.Quantity', 'Q.Value'
                # Multiply RT by 60 to convert from minutes to seconds
                self.chromatogram_peak_feature = TransitionGroupFeature(consensusApex=precursor_search_results['RT'].iloc[0] * 60,  leftBoundary=precursor_search_results['RT.Start'].iloc[0] * 60, rightBoundary=precursor_search_results['RT.Stop'].iloc[0] * 60, areaIntensity=precursor_search_results['Precursor.Quantity'].iloc[0], qvalue=precursor_search_results['Q.Value'].iloc[0])

                # Save the mobilogram peak feature from the report using cols 'IM'
                self.mobilogram_peak_feature = TransitionGroupFeature(leftBoundary=None, rightBoundary=None,consensusApex=precursor_search_results['IM'].iloc[0])
                
                out[file] = {'chromatogram_peak_feature': self.chromatogram_peak_feature, 'mobilogram_peak_feature': self.mobilogram_peak_feature}
                self.precursor_search_data = out           
            return self

        elif len(row_indices)-1==0:
            LOGGER.debug(f"Error: No feature results found for {peptide_tmp} {charge} in {self.filename}")
            self.precursor_search_data = {f.filename : {'chromatogram_peak_feature': TransitionGroupFeature(None, None), 'mobilogram_peak_feature': TransitionGroupFeature(None, None)} for f in self.dataFiles} 

            return self

    def load_report(self) -> None:
        '''
        Load the report file
        '''
        self.search_data = pd.read_csv(self.filename, sep='\t')
        # rename columns
        self.search_data = self.search_data.rename(columns={'Protein.Ids': 'ProteinId', 'Stripped.Sequence': 'PeptideSequence', 'Modified.Sequence': 'ModifiedPeptideSequence', 'Q.Value': 'Qvalue', 'Precursor.Mz': 'PrecursorMz', 'Precursor.Charge': 'PrecursorCharge'})
        # Assign dummy Decoy column all 0
        self.search_data['Decoy'] = 0
