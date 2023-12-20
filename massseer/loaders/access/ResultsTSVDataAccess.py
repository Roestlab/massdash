import pandas as pd
from typing import List
from massseer.loaders.access.GenericResultsAccess import GenericResultsAccess
from massseer.structs.TransitionGroupFeature import TransitionGroupFeature

class ResultsTSVDataAccess(GenericResultsAccess): 
    ''' Class for generic access to TSV file containing the results, currently only supports DIA-NN tsv files'''
    def init(self, filename: str) -> None:
        self.filename = filename
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


    def getTransitionGroupFeatures(self, runname: str, pep_id: str, charge: int) -> pd.DataFrame:
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
            results = self.df[(self.df['filename'] == runname_exact) & (self.df['ModifiedPeptideSequence'] == pep_id) & (self.df['PrecursorCharge'] == charge)]
            return ResultsTSVDataAccess.convertDfToTransitionGroupFeatures(results)
        
    def getTransitionGroupFeaturesDf(self, runname: str, pep_id: str, charge: int) -> pd.DataFrame:
        '''
        Loads a TransitionGroupFeature object from the results file to a pandas dataframe
        '''
        columns = ['filename', 'leftBoundary', 'rightBoundary', 'areaIntensity', 'qvalue', 'consensusApex', 'consensusApexIntensity']
        runname_exact = self.getExactRunName(runname)
        if runname_exact is None:
            return pd.DataFrame(columns=columns)
        else:
            # TODO renaming or filtering columns needed?
            return self.df[(self.df['filename'] == runname_exact) & (self.df['ModifiedPeptideSequence'] == pep_id) & (self.df['PrecursorCharge'] == charge)]

    @staticmethod
    def convertDfToTransitionGroupFeatures(df: pd.DataFrame) -> List[TransitionGroupFeature]:
        out = []
        for _, row in df.iterrows():
            out.append(TransitionGroupFeature(consensusApex=row['RT'] * 60,  leftBoundary=row['RT.Start'] * 60, rightBoundary=row['RT.Stop'] * 60, areaIntensity=row['Precursor.Quantity'], qvalue=row['Q.Value']))


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