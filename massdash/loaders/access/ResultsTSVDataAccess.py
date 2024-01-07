"""
massdash/loaders/access/ResultsTSVDataAccess
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import pandas as pd
import numpy as np
import re
from typing import List

# Loaders
from massdash.loaders.access.GenericResultsAccess import GenericResultsAccess
# Structs
from massdash.structs.TransitionGroupFeature import TransitionGroupFeature
# Utils
from massdash.util import LOGGER

class ResultsTSVDataAccess(GenericResultsAccess): 
    ''' Class for generic access to TSV file containing the results, currently only supports DIA-NN tsv files'''
    def __init__(self, filename: str, verbose: bool = False) -> None:
        super().__init__(filename, verbose)
        self.filename = filename
        self.peptideHash = self._initializePeptideHashTable()
        self.df = self.loadData() 
        self.runs = self.df['Run'].drop_duplicates()
        self.has_im = 'IM' in self.df.columns
    
    def loadData(self) -> pd.DataFrame:
        '''
        This method loads the data from self.filename into a pandas dataframe
        '''
        df = pd.read_csv(self.filename, sep='\t')

        # rename columns, assuming this is a DIA-NN file
        df = df.rename(columns={'Protein.Ids': 'ProteinId', 'Stripped.Sequence': 'PeptideSequence', 'Modified.Sequence': 'ModifiedPeptideSequence', 'Q.Value': 'Qvalue', 'Precursor.Mz': 'PrecursorMz', 'Precursor.Charge': 'PrecursorCharge'})
        # Assign dummy Decoy column all 0
        df['Decoy'] = 0
        return df

    def _initializePeptideHashTable(self) -> pd.DataFrame:   
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
        print(runname_exact)

        if runname_exact is None:
            LOGGER.debug(f"Error: No matching runs found for {runname}")
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
                    out.append(TransitionGroupFeature(consensusApex=row['RT'] * 60,
                                                      leftBoundary=row['RT.Start'] * 60,
                                                      rightBoundary=row['RT.Stop'] * 60,
                                                      areaIntensity=row['Precursor.Quantity'],
                                                      qvalue=row['Q.Value'],
                                                      consensusApexIM=row['IM'] if self.has_im else None,
                                                      sequence=row['Modified.Sequence'],
                                                      precursor_charge=row['Precursor.Charge']))
                return out 
            else: # len(row_indices)-1==0:
                LOGGER.debug(f"Error: No feature results found for {peptide_tmp} {charge} in {self.filename}")
                return []

    def getTransitionGroupFeaturesDf(self, runname: str, pep_id: str, charge: int) -> pd.DataFrame:
        '''
        Loads a TransitionGroupFeature object from the results file to a pandas dataframe. Since there is only one feature this is the same as getTopTransitionGroupFeatureDf()
        '''
        return self.getTopTransitionGroupFeatureDf(runname, pep_id, charge)

    def getTopTransitionGroupFeatureDf(self, runname: str, pep_id: str, charge: int) -> pd.DataFrame:
        '''
        Get a pandas dataframe with the top TransitionGroupFeatures found in the results file. Since there is only one feature this is the same as getTransitionGroupFeaturesDf
        
        Args:
            pep_id (str): Peptide ID
            charge (int): Charge
        
        Returns:
            pd.DataFrame: Dataframe with the TransitionGroupFeatures
        '''
        columns = ['Run', 'leftBoundary', 'rightBoundary', 'areaIntensity', 'qvalue', 'consensusApex', 'consensusApexIntensity', 'precursor_charge', 'sequence']
        if self.has_im:
            columns.append('consensusApexIM')
        runname_exact = self.getExactRunName(runname)
        if runname_exact is None:
            return pd.DataFrame(columns=columns)
        else:
            df = self.df[(self.df['Run'] == runname_exact) & (self.df['ModifiedPeptideSequence'] == pep_id) & (self.df['PrecursorCharge'] == charge)]

            df = df.rename(columns={'RT.Start': 'leftBoundary', 
                                    'RT.Stop': 'rightBoundary', 
                                    'Precursor.Quantity': 'areaIntensity', 
                                    'RT': 'consensusApex', 
                                    'Qvalue' : 'qvalue',
                                    'PrecursorCharge': 'precursor_charge',
                                    'ModifiedPeptideSequence': 'sequence',
                                    'PrecursorMz': 'precursor_mz'})
            
            if self.has_im:
                df = df.rename(columns={'IM': 'consensusApexIM'})

            df['consensusApex'] = df['consensusApex'] * 60
            df['leftBoundary'] = df['leftBoundary'] * 60
            df['rightBoundary'] = df['rightBoundary'] * 60
            df['consensusApexIntensity'] = np.nan
            return df[columns]

    def getExactRunName(self, run_basename_wo_ext: str) -> str:
        '''
        Returns the run name from the filename
        '''
        matching_runs = self.runs[self.runs.str.contains(run_basename_wo_ext)]
        if len(matching_runs) == 0:
            print("Error: No matching runs found for {run_basename_wo_ext}")
            return None
        elif len(matching_runs) == 1:
            return matching_runs.iloc[0]
        else: ## greater than 1
            print("Warning: More than one run found for {run_basename_wo_ext}, this can lead to unpredicted behaviour")
            return matching_runs.iloc[0]