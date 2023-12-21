import pandas as pd
from typing import List
from massseer.loaders.access.GenericResultsAccess import GenericResultsAccess
from massseer.structs.TransitionGroupFeature import TransitionGroupFeature

from massseer.util import LOGGER

class ResultsTSVDataAccess(GenericResultsAccess): 
    ''' Class for generic access to TSV file containing the results, currently only supports DIA-NN tsv files'''
    def init(self, filename: str, verbose: bool = False) -> None:
        super().__init__(filename, verbose)
        self.filename = filename
        self.peptideHash = self._initializePeptideHashTable()
        self.df = self.loadData()
        self.runs = self.df['filename'].drop_duplicates()
    
    def loadData(self) -> pd.DataFrame:
        '''
        This method loads the data from self.filename into a pandas dataframe
        '''
        df = pd.read_csv(self.filename, sep='\t')

        # rename columns, assuming this is a DIA-NN file
        df = df.rename(columns={'Protein.Ids': 'ProteinId', 'Stripped.Sequence': 'PeptideSequence', 'Modified.Sequence': 'ModifiedPeptideSequence', 'Q.Value': 'Qvalue', 'Precursor.Mz': 'PrecursorMz', 'Precursor.Charge': 'PrecursorCharge'})
        # Assign dummy Decoy column all 0
        df['Decoy'] = 0

        self.df = df

    def _initializePeptideHashTable(self, ) -> List[int]:   
        '''
        Load Peptide and Charge for easy access
        '''
        return pd.read_csv(self.filename, sep='\t', usecols=['Modified.Sequence', 'Precursor.Charge', 'Run'])


    def getTopTransitionGroupFeature(self, runname: str, pep: str, charge: int) -> TransitionGroupFeature:
        '''
        Loads the top TransitionGroupFeature from the results file
        Args:
            pep_id (str): Peptide ID
            charge (int): Charge
        Returns:
            TransitionGroupFeature: TransitionGroupFeature object containing peak boundaries, intensity and confidence
        '''
        tg = self.getTransitionGroupFeatures(runname, pep, charge)

        if len(tg) == 0:
            return None
        elif len(tg) == 1:
            return tg[0]
        else:
            LOGGER.debug(f"Warning: More than one feature found for {pep} {charge} in {self.filename}, returning the first feature, this can lead to unexcepted behaviour")
            return tg[0]

    def getTransitionGroupFeatures(self, runname: str, peptide:str, charge: int):
        '''
        Loads a PeakFeature object from the results file
        Args:
            pep_id (str): Peptide ID
            charge (int): Charge
        Returns:
            TransitionGroupFeature: TransitionGroupFeature object containing peak boundaries, intensity and confidence
        '''
        runname_exact = self.getExactRunName(runname)

        if runname_exact is None:
            return []
        else:
            targetPeptide = self.peptideHash[(self.peptideHash['Run'] == runname_exact) & (self.peptideHash['Modified.Sequence'] == peptide) & (self.peptideHash['Precursor.Charge'] == charge)]

            # return the row indices and add 1 to each index to account for the header row
            rows_to_load = [0] + [idx + 1 for idx in targetPeptide.index.tolist()]

            # remove any periods from the peptide sequence i.e. for N terminal modifications
            # i.e. Convert .(UniMod:1)SEGDSVGESVHGKPSVVYR to (UniMod:1)SEGDSVGESVHGKPSVVYR
            peptide_tmp = peptide.replace('.', '')
            LOGGER.debug(f"Loading report for {peptide_tmp} {charge} from {self.filename}")

            if len(rows_to_load)-1 !=0:
                feature_data = pd.read_csv(self.filename, sep='\t', skiprows=lambda x: x not in rows_to_load)
                LOGGER.debug(f"Found {feature_data.shape[0]} rows from {self.filename} for feature data")

                # Save the chromatogram peak feature from the report using cols 'RT', 'RT.Start', 'RT.Stop', 'Precursor.Quantity', 'Q.Value'
                # Multiply RT by 60 to convert from minutes to seconds
                out = []
                for _, row in feature_data.iterrows():
                    out.append(TransitionGroupFeature(consensusApex=row['RT'] * 60,  leftBoundary=row['RT.Start'] * 60, rightBoundary=row['RT.Stop'] * 60, areaIntensity=row['Precursor.Quantity'], qvalue=row['Q.Value']))
                return out 
            else: # len(row_indices)-1==0:
                LOGGER.debug(f"Error: No feature results found for {peptide_tmp} {charge} in {self.filename}")
                return []

    def getTransitionGroupFeaturesDf(self, runname: str, pep_id: str, charge: int) -> pd.DataFrame:
        '''
        Loads a TransitionGroupFeature object from the results file to a pandas dataframe
        '''
        pass
        '''
        columns = ['filename', 'leftBoundary', 'rightBoundary', 'areaIntensity', 'qvalue', 'consensusApex', 'consensusApexIntensity']
        runname_exact = self.getExactRunName(runname)
        if runname_exact is None:
            return pd.DataFrame(columns=columns)
        else:
            # TODO renaming or filtering columns needed?
            return self.df[(self.df['Run'] == runname_exact) & (self.df['ModifiedPeptideSequence'] == pep_id) & (self.df['PrecursorCharge'] == charge)]
        '''

    def getExactRunName(self, runname: str) -> str:
        '''
        Returns the run name from the filename
        '''
        matching_runs = self.run[self.run['filename'].str.contains(runname)]
        if len(matching_runs) == 0:
            print("Error: No matching runs found for {runname}")
            return None
        elif len(matching_runs) == 1:
            return matching_runs['filename'].iloc[0]
        else: ## greater than 1
            print("Warning: More than one run found for {runname}, this can lead to unpredicted behaviour")
            return matching_runs['filename'].iloc[0]