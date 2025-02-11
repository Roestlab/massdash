"""
massdash/loaders/access/ResultsParquetDataAccess
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import pandas as pd
import numpy as np
from typing import Literal, List, Optional, Dict, Union
from pathlib import Path
from functools import wraps

# Loaders
from .GenericResultsAccess import GenericResultsAccess
# Structs
from ...structs.TransitionGroupFeature import TransitionGroupFeature
# Utils
from ...util import LOGGER

# Note currently only OpenSwath Results are supported
class ResultsParquetDataAccess(GenericResultsAccess): 
    ''' Class for generic access to .parquet file containing the results, currently only supports OSW parquet files'''

    # static variable
    columnMapping = {
        'OpenSwath':{
                    'PROTEIN.PROTEIN_ACCESSION':'ProteinId',
                    'PEPTIDE.UNMODIFIED_SEQUENCE':'PeptideSequence',
                    'PEPTIDE.MODIFIED_SEQUENCE':'ModifiedPeptideSequence',
                    'SCORE_MS2.QVALUE':'Qvalue',
                    'PRECURSOR.PRECURSOR_MZ':'PrecursorMz',
                    'PRECURSOR.CHARGE':'PrecursorCharge',
                    'FEATURE.LEFT_WIDTH':'leftBoundary',
                    'FEATURE.RIGHT_WIDTH':'rightBoundary',
                    'FEATURE.EXP_RT':'consensusApex',
                    'FEATURE_MS2.EXP_IM':'consensusApexIM',
                    'RUN.FILENAME':'runName',
                    'FEATURE_MS2.AREA_INTENSITY':'Intensity',
                    'TRANSITION_ID':'TRANSITION_ID',
                    'TRANSITION_ANNOTATION':'ANNOTATION',
                    'PRECURSOR_ID':'PrecursorId'
                    },
        #'DIA-NN':{'Protein.Ids': 'ProteinId', 'Stripped.Sequence': 'PeptideSequence', 'Modified.Sequence': 'ModifiedPeptideSequence', 'Q.Value': 'Qvalue', 'Precursor.Mz': 'PrecursorMz', 'Precursor.Charge': 'PrecursorCharge', 'Precursor.Quantity': 'Intensity', 'Run':'runName', 'RT.Start':'leftBoundary', 'RT.Stop':'rightBoundary', 'IM':'consensusApexIM', 'RT':'consensusApex' },
    }

    def __init__(self, filename: str, verbose: bool = False) -> None:
        super().__init__(filename, verbose)
        self.filename = filename
        self.results_type = "OpenSwath"
        self.df = None # will be set by loadData()
        self.loadData()   # set self.df 
        self.runs = self.df['runName'].drop_duplicates().dropna()
    
    @property
    def has_im(self) -> bool:
        return 'consensusApexIM' in self.df.columns

    def requiredColumns(*required_columns):
        def decorator(func):
            @wraps(func)
            def wrapper(self, *args, **kwargs):
                for col in required_columns:
                    if col not in self.columnMapping[self.results_type].values():
                        raise ValueError(f"Specified column '{col}' is not available in this results file")
                missing_columns = [col for col in required_columns if col not in self.df.columns]
                if missing_columns:
                    self.appendColumns(missing_columns)
                return func(self, *args, **kwargs)
            return wrapper
        return decorator

    def loadData(self):
        if self.results_type == 'OpenSwath':
            self.df = pd.read_parquet(self.filename, columns=['PRECURSOR_ID', 'RUN.FILENAME'])
        else:
            raise ValueError(f"Results type {self.results_type} not supported")

        self.df = self.df.rename(columns=ResultsParquetDataAccess.columnMapping[self.results_type])
        self.df['software'] = self.results_type

    def appendColumns(self, columns) -> pd.DataFrame:
        '''
        This method loads specific columns from the parquet and appends them to the pandas dataframe 
        In this implementation columns are only loaded when they are required
        '''
        #just read first row to detect the file type
        
        # read all required columns and set new names
        
        # get the reverse map so can get the native column names in the file
        reverseMap = {v: k for k, v in ResultsParquetDataAccess.columnMapping[self.results_type].items()}
        columns_to_load = [reverseMap[col] for col in columns]
        
        new_columns = pd.read_parquet(self.filename, columns=columns_to_load)
        self.df = pd.concat([self.df, new_columns], axis=1)
        self.df = self.df.rename(columns=ResultsParquetDataAccess.columnMapping[self.results_type])
        
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

    @requiredColumns('consensusApex', 'leftBoundary', 'rightBoundary', 'Intensity', 'Qvalue', 'consensusApexIM', 'ModifiedPeptideSequence', 'PrecursorCharge')
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
            features = self.df[(self.df['runName'] == runname_exact) & (self.df['ModifiedPeptideSequence'] == peptide) & (self.df['PrecursorCharge'] == charge)]

                # Multiply RT by 60 to convert from minutes to seconds
            if len(features) >= 1:
                out = []
                for _, row in features.iterrows():
                    out.append(TransitionGroupFeature(consensusApex=row['consensusApex'] * self.rt_multiplier,
                                                      leftBoundary=row['leftBoundary'] * self.rt_multiplier,
                                                      rightBoundary=row['rightBoundary'] * self.rt_multiplier,
                                                      areaIntensity=row['Intensity'],
                                                      qvalue=row['Qvalue'],
                                                      consensusApexIM=row['consensusApexIM'] if self.has_im else None,
                                                      sequence=row['ModifiedPeptideSequence'],
                                                      precursor_charge=row['PrecursorCharge'],
                                                      software=self.results_type))
                return out 
            else: # len(row_indices)-1==0:
                LOGGER.debug(f"Error: No feature results found for {peptide} {charge} in {self.filename}")
                return []


    @requiredColumns('consensusApex', 'leftBoundary', 'rightBoundary', 'Intensity', 'Qvalue', 'consensusApexIM', 'ModifiedPeptideSequence', 'PrecursorCharge')
    def getTransitionGroupFeaturesDf(self, runname: str, pep_id: str, charge: int) -> pd.DataFrame:
        '''
        Loads a TransitionGroupFeature object from the results file to a pandas dataframe. Since there is only one feature this is the same as getTopTransitionGroupFeatureDf()
        '''
        runname_exact = self.getExactRunName(runname)
        if runname_exact is None:
            return pd.DataFrame(columns=self.columns)
        else:
            return self.df[(self.df['runName'] == runname_exact) & (self.df['ModifiedPeptideSequence'] == pep_id) & (self.df['PrecursorCharge'] == charge)].copy()


    @requiredColumns('consensusApex', 'leftBoundary', 'rightBoundary', 'Intensity', 'Qvalue', 'consensusApexIM', 'ModifiedPeptideSequence', 'PrecursorCharge')
    def getTopTransitionGroupFeatureDf(self, runname: str, pep_id: str, charge: int) -> pd.DataFrame:
        '''
        Get a pandas dataframe with the top TransitionGroupFeatures found in the results file. Since there is only one feature this is the same as getTransitionGroupFeaturesDf
        
        Args:
            pep_id (str): Peptide ID
            charge (int): Charge
        
        Returns:
            pd.DataFrame: Dataframe with the TransitionGroupFeatures
        '''
        candidates = self.getTransitionGroupFeaturesDf(runname, pep_id, charge)
        return candidates.sort_values(by='Qvalue').head(1)

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
        raise NotImplementedError("This method is not implemented for this class")
    
    def getIdentifiedPrecursorIntensities(self, qvalue: float = 0.01, run: Optional[str] = None, precursorLevel = False) -> pd.DataFrame:
        '''
        Get a dataframe of identified precursors and their intensities from the results file
        Args:
            qvalue (float): Qvalue threshold
            run (str): Run name
            precursorLevel (bool): If True, do not filter by protein Q.Value (only on precursor level) - "False" Only supported for DIA-NN results type will automatically be True otherwise
        '''
        raise NotImplementedError("This method is not implemented for this class")


    def getIdentifiedProteins(self, qvalue: float = 0.01, run:Optional[str] = None) -> Union[set, Dict[str, set]]:
        raise NotImplementedError("This method is not implemented for this class")

    def getIdentifiedPeptides(self, qvalue: float = 0.01, run:Optional[str] = None) -> Union[set, Dict[str, set]]:
        raise NotImplementedError("This method is not implemented for this class")
    
    def getSoftware(self) -> str:
        return self.results_type
    


    ############### Accessors for transition level data ################
    @requiredColumns('PrecursorId', 'ModifiedPeptideSequence', 'PrecursorCharge', 'TRANSITION_ID', 'ANNOTATION')
    def getTransitionIDAnnotationFromSequence(self, fullpeptidename, charge):
        """
        Retrieves transition information for a given peptide and charge.

        Args:
            fullpeptidename (str): The full modified sequence of the peptide.
            charge (int): The precursor charge.

        Returns:
            pandas.DataFrame: The transition information.
        """
        transitionInfo = self.df[(self.df['ModifiedPeptideSequence'] == fullpeptidename) & (self.df['PrecursorCharge'] == charge)][['TRANSITION_ID', 'ANNOTATION']].drop_duplicates().copy()
        if not transitionInfo.empty:
            return pd.concat( [ transitionInfo[col].str.split(';').explode() for col in transitionInfo.columns ], axis=1)
        else:
            return pd.DataFrame(columns=['TRANSITION_ID', 'ANNOTATION'])
    
    @requiredColumns('PrecursorId')
    def getPrecursorIDFromPeptideAndCharge(self, pep_id, charge):
        return self.df[(self.df['ModifiedPeptideSequence'] == pep_id) & (self.df['PrecursorCharge'] == charge)]['PrecursorId'].iloc[0]