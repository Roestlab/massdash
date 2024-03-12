"""
massdash/loaders/access/ResultsTSVDataAccess
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import pandas as pd
import numpy as np
import re
from typing import Literal, List, Optional, Dict, Union
from pathlib import Path

# Loaders
from .GenericResultsAccess import GenericResultsAccess
# Structs
from ...structs.TransitionGroupFeature import TransitionGroupFeature
# Utils
from ...util import LOGGER

class ResultsTSVDataAccess(GenericResultsAccess): 
    ''' Class for generic access to TSV file containing the results, currently only supports DIA-NN tsv files'''

    # static variable
    columnMapping = {
        'OpenSwath':{'ProteinName': 'ProteinId', 'Sequence': 'PeptideSequence', 'FullPeptideName': 'ModifiedPeptideSequence', 'm_score': 'Qvalue', 'mz': 'PrecursorMz', 'Charge': 'PrecursorCharge', 'leftWidth': 'RT.Start', 'rightWidth': 'RT.Stop'},
        'DIA-NN':{'Protein.Ids': 'ProteinId', 'Stripped.Sequence': 'PeptideSequence', 'Modified.Sequence': 'ModifiedPeptideSequence', 'Q.Value': 'Qvalue', 'Precursor.Mz': 'PrecursorMz', 'Precursor.Charge': 'PrecursorCharge', 'Precursor.Quantity': 'Intensity', 'Run':'filename', 'Precursor.Id':'Precursor'},
        'DreamDIA':{'protein_name': 'ProteinId', 'sequence': 'PeptideSequence', 'full_sequence': 'ModifiedPeptideSequence', 'qvalue': 'Qvalue', 'SCORE_MZ': 'PrecursorMz', 'SCORE_CHARGE': 'PrecursorCharge', 'filename': 'filename', 'quantification': 'Intensity'}

    }

    def __init__(self, filename: str, verbose: bool = False) -> None:
        super().__init__(filename, verbose)
        self.filename = filename
        self.results_type = None # will be set by detectResultsType()
        self.df = None # will be set by loadData()
        
        self.loadData()   # set self.df and self.results_type
        self.peptideHash = self._initializePeptideHashTable()
        self.runs = self.df['filename'].drop_duplicates()  
        self.has_im = 'IM' in self.df.columns
    
    def detectResultsType(self) -> Literal["OpenSWATH", "DIA-NN", "DreamDIA"]:
        '''
        Detects the type of results file by looking at the column names
        '''
        diann_dont_check = {'Precursor.Mz'} # Note: remove Precursor.Mz because not all DIA-NN files have this column
        for rsltType, colDict in ResultsTSVDataAccess.columnMapping.items():
            if set(colDict.keys()).difference(diann_dont_check).issubset(set(self.df.columns)): 
                return rsltType

        raise Exception(f"Error: Unsupported file type {self.filename}, could not detect results type")

    def loadData(self) -> pd.DataFrame:
        '''
        This method loads the data from self.filename into a pandas dataframe
        '''
        self.df = pd.read_csv(self.filename, sep='\t')

        self.results_type = self.detectResultsType()

        # rename column according to column mapping 
        self.df = self.df.rename(columns=ResultsTSVDataAccess.columnMapping[self.results_type])
        
        # TODO is this required?
        # Assign dummy Decoy column all 0
        self.df['Decoy'] = 0
        self.df['software'] = self.results_type

    def _initializePeptideHashTable(self) -> pd.DataFrame:   
        '''
        Load Peptide and Charge for easy access
        '''
        if self.results_type == "OpenSWATH":
            self.hash_table_columns = ['FullPeptideName', 'Charge', 'filename']
            self.rt_multiplier = 1
        elif self.results_type == "DIA-NN":
            self.hash_table_columns = ['Modified.Sequence', 'Precursor.Charge', 'Run']
            self.rt_multiplier = 60
        elif self.results_type == "DreamDIA":
            self.hash_table_columns = ['full_sequence', 'sequence', 'filename']
            self.rt_multiplier = 1
        else:
            raise ValueError(f"Results type {self.results_type} not supported")
            
        pepHash = pd.read_csv(self.filename, sep='\t', usecols=self.hash_table_columns)

        return pepHash.rename(columns=ResultsTSVDataAccess.columnMapping[self.results_type])
        
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
            LOGGER.debug(f"Error: No matching runs found for {runname}")
            return []
        else:
            targetPeptide = self.peptideHash[(self.peptideHash['filename'] == runname_exact) & (self.peptideHash['ModifiedPeptideSequence'] == peptide) & (self.peptideHash['PrecursorCharge'] == charge)]

            # return the row indices and add 1 to each index to account for the header row
            rows_to_load = [0] + [idx + 1 for idx in targetPeptide.index.tolist()]
                
            # remove any periods from the peptide sequence i.e. for N terminal modifications
            # i.e. Convert .(UniMod:1)SEGDSVGESVHGKPSVVYR to (UniMod:1)SEGDSVGESVHGKPSVVYR
            peptide_tmp = peptide.replace('.', '')
            LOGGER.debug(f"Loading report for {peptide_tmp} {charge} from {self.filename}")

            if len(rows_to_load)-1 !=0:
                feature_data = pd.read_csv(self.filename, sep='\t', skiprows=lambda x: x not in rows_to_load)
                feature_data = feature_data.rename(columns=ResultsTSVDataAccess.columnMapping[self.results_type])
                LOGGER.debug(f"Found {feature_data.shape[0]} rows from {self.filename} for feature data")

                # Save the chromatogram peak feature from the report using cols 'RT', 'RT.Start', 'RT.Stop', 'Precursor.Quantity', 'Q.Value'
                # Multiply RT by 60 to convert from minutes to seconds
                out = []
                for _, row in feature_data.iterrows():
                    out.append(TransitionGroupFeature(consensusApex=row['RT'] * 60,
                                                      leftBoundary=row['RT.Start'] * self.rt_multiplier,
                                                      rightBoundary=row['RT.Stop'] * self.rt_multiplier,
                                                      areaIntensity=row['Intensity'],
                                                      qvalue=row['Qvalue'],
                                                      consensusApexIM=row['IM'] if self.has_im else None,
                                                      sequence=row['ModifiedPeptideSequence'],
                                                      precursor_charge=row['PrecursorCharge']))
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
        runname_exact = self.getExactRunName(runname)
        if runname_exact is None:
            return pd.DataFrame(columns=self.COLUMNS)
        else:
            df = self.df[(self.df['filename'] == runname_exact) & (self.df['ModifiedPeptideSequence'] == pep_id) & (self.df['PrecursorCharge'] == charge)]

            df = df.rename(columns={'RT.Start': 'leftBoundary', 
                                    'RT.Stop': 'rightBoundary', 
                                    'Intensity': 'areaIntensity', 
                                    'RT': 'consensusApex', 
                                    'Qvalue' : 'qvalue',
                                    'PrecursorCharge': 'precursor_charge',
                                    'ModifiedPeptideSequence': 'sequence',
                                    'PrecursorMz': 'precursor_mz',
                                    'IM': 'consensusApexIM'})
            

            df['consensusApex'] = df['consensusApex'] * self.rt_multiplier
            df['leftBoundary'] = df['leftBoundary'] * self.rt_multiplier
            df['rightBoundary'] = df['rightBoundary'] * self.rt_multiplier
            df['consensusApexIntensity'] = np.nan
            return df[self.COLUMNS]

    def getExactRunName(self, run_basename_wo_ext: str) -> str:
        '''
        Returns the run name from the filename
        '''
        matching_runs = self.runs[self.runs.str.contains(run_basename_wo_ext)]
        if len(matching_runs) == 0:
            print(f"Error: No matching runs found for {run_basename_wo_ext}")
            return None
        elif len(matching_runs) == 1:
            return matching_runs.iloc[0]
        else: ## greater than 1
            print(f"Warning: More than one run found for {run_basename_wo_ext}, this can lead to unpredicted behaviour")
            return matching_runs.iloc[0]
    
    def getRunNames(self) -> List[str]:
        '''
        Get run names without the file extension

        Returns:
            list: List of run names
        '''
        return [ Path(r).stem for r in self.runs]
    
    def getIdentifiedPrecursors(self, qvalue: float = 0.01, run:Optional[str] = None, precursorLevel = False) -> Union[set, Dict[str, set]]:
        if precursorLevel:
            if isinstance(run, str):
                return set(self.df[(self.df['filename'] == run) & (self.df['Qvalue'] <= qvalue)]['Precursor'])
            else:
                return self.df[(self.df['Qvalue'] <= qvalue)].groupby('filename').apply(lambda x: set(x['Precursor'])).to_dict()
        else:
            if isinstance(run, str):
                return set(self.df[(self.df['filename'] == run) & (self.df['Qvalue'] <= qvalue) & (self.df['PG.Q.Value'] <= qvalue )]['Precursor'])
            else:
                return self.df[(self.df['Qvalue'] <= qvalue) & (self.df['PG.Q.Value']<= qvalue )].groupby('filename').apply(lambda x: set(x['Precursor'])).to_dict()
    
    def getIdentifiedPrecursorIntensities(self, qvalue: float = 0.01, run: Optional[str] = None) -> pd.DataFrame:
        if isinstance(run, str):
            return self.df[(self.df['filename'] == run) & (self.df['Qvalue'] <= qvalue)][['Precursor', 'Intensity']].copy()
        else:
            return self.df[(self.df['Qvalue'] <= qvalue)][['filename', 'Precursor', 'Intensity']].copy()

    def getIdentifiedProteins(self, qvalue: float = 0.01, run:Optional[str] = None) -> Union[set, Dict[str, set]]:
        if isinstance(run, str):
            return set(self.df[(self.df['filename'] == run) & (self.df['Qvalue'] <= qvalue)]['ProteinId'])
        else:
            return self.df[(self.df['Qvalue'] <= qvalue)][['ProteinId', 'filename']].groupby(['filename']).apply(lambda x: set(x['ProteinId'])).to_dict()

    def getIdentifiedPeptides(self, qvalue: float = 0.01, run:Optional[str] = None) -> Union[set, Dict[str, set]]:
        if isinstance(run, str):
            return set(self.df[(self.df['filename'] == run) & (self.df['Qvalue'] <= qvalue)]['ModifiedPeptideSequence'])
        else:
            return self.df[(self.df['Qvalue'] <= qvalue)][['filename', 'ModifiedPeptideSequence']].groupby('filename').apply(lambda x: set(x['ModifiedPeptideSequence'])).to_dict()
    
    def getSoftware(self) -> str:
        return self.results_type