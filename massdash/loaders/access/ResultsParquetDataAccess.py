"""
massdash/loaders/access/ResultsParquetDataAccess
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import pandas as pd
import numpy as np
from typing import Literal, List, Optional, Dict, Union
from pathlib import Path
from functools import wraps
import pyarrow.parquet as pq

# Loaders
from .GenericResultsAccess import GenericResultsAccess
# Structs
from ...structs.TransitionGroupFeature import TransitionGroupFeature
# Utils
from ...util import LOGGER

# Note currently only OpenSwath Results are supported
class ResultsParquetDataAccess(GenericResultsAccess): 
    ''' Class for generic access to .parquet file containing the results, currently only supports OSW parquet files'''

    FEATURE_REQUIRED_COLUMNS = ['consensusApex', 'leftBoundary', 'rightBoundary', 'Intensity', 'Qvalue', 'ModifiedPeptideSequence', 'PrecursorCharge']
    FEATURE_OPTIONAL_COLUMNS = ['consensusApexIM']

    def __init__(self, 
                 filename: str, 
                 verbose: bool = False, 
                 peptide_protein_context: Union[ None, Literal['GLOBAL', 'RUNSPECIFIC', 'EXPERIMENTWIDE'] ] = 'EXPERIMENTWIDE') -> None:
        super().__init__(filename, verbose)
        self.filename = filename
        self.results_type = "OpenSwath"
        self.df = None # will be set by loadData(), this is a polars dataframe but using polars only for internal use
        self.peptide_protein_context = peptide_protein_context # can be "GLOBAL","RUN-SPECIFIC" OR "EXPERIMENT-WIDE"
        self.schema = [ c.name for c in pq.read_schema(filename) ]

        self.loadData()   # set self.df 
        self.runs = self.df['runName'].drop_duplicates().dropna()
   
    @property
    def columnMapping(self) -> dict:
        if self.results_type == 'OpenSwath':
            columns = {
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
                    'PRECURSOR_ID':'PrecursorId',
                    'SCORE_MS2.RANK':'Rank'
                    }
            if self.peptide_protein_context is not None:
                columns[f'SCORE_PEPTIDE.QVALUE_{self.peptide_protein_context}'] = 'Qvalue_peptide'
                columns[f'SCORE_PROTEIN.QVALUE_{self.peptide_protein_context}'] = 'Qvalue_protein'
        else:
            raise ValueError(f"{self.results_type} backend is not supported for parquet files")  
        return columns
    
    @property
    def rt_multiplier(self) -> int:
        if self.results_type == 'OpenSwath':
            return 1
        else:
            raise ValueError(f"Results type {self.results_type} not supported for parquet files")
    
    @property
    def reverseColumnMapping(self) -> dict:
        '''
        This maps native columns to be
        '''
        return {v: k for k, v in self.columnMapping.items()}
        
    
    @property
    def has_im(self) -> bool:
        return self.reverseColumnMapping['consensusApexIM'] in self.schema

    def requiredColumns(*required_columns):
        def decorator(func):
            @wraps(func)
            def wrapper(self, *args, **kwargs):
                for col in required_columns:
                    if col not in self.columnMapping.values():
                        raise ValueError(f"Specified column(s) '{col}' is not available in this results file")
                missing_columns = [col for col in required_columns if col not in self.df.columns]
                if missing_columns:
                    self.appendColumns(missing_columns)
                return func(self, *args, **kwargs)
            return wrapper
        return decorator

    def optionalColumns(*optional_columns):
        def decorator(func):
            @wraps(func)
            def wrapper(self, *args, **kwargs):
                missing_columns = [col for col in optional_columns if col not in self.df.columns and col in self.reverseColumnMapping[col] in self.schema]
                if len(missing_columns) > 0:
                    self.appendColumns(missing_columns)
                return func(self, *args, **kwargs)
            return wrapper
        return decorator

    def loadData(self):
        if self.results_type == 'OpenSwath':
            self.df = pd.read_parquet(self.filename, columns=['PRECURSOR_ID', 'RUN.FILENAME'])
        else:
            raise ValueError(f"Results type {self.results_type} not supported")

        self.df = self.df.rename(columns=self.columnMapping)
        self.df['software'] = self.results_type

    def appendColumns(self, columns) -> pd.DataFrame:
        '''
        This method loads specific columns from the parquet and appends them to the pandas dataframe 
        In this implementation columns are only loaded when they are required
        '''
        #just read first row to detect the file type
        
        # read all required columns and set new names
        
        # get the reverse map so can get the native column names in the file
        columns_to_load = [self.reverseColumnMapping[col] for col in columns]
        
        new_columns = pd.read_parquet(self.filename, columns=columns_to_load)
        self.df = pd.concat([self.df, new_columns], axis=1)
        self.df = self.df.rename(columns=self.columnMapping)

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

    @requiredColumns(*FEATURE_REQUIRED_COLUMNS)
    @optionalColumns(*FEATURE_OPTIONAL_COLUMNS)
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


    @requiredColumns(*FEATURE_REQUIRED_COLUMNS)
    @optionalColumns(*FEATURE_OPTIONAL_COLUMNS)
    def getTransitionGroupFeaturesDf(self, runname: str, pep_id: str, charge: int) -> pd.DataFrame:
        '''
        Loads a TransitionGroupFeature object from the results file to a pandas dataframe. Since there is only one feature this is the same as getTopTransitionGroupFeatureDf()
        '''

        columns = self.FEATURE_REQUIRED_COLUMNS if not self.has_im else self.FEATURE_REQUIRED_COLUMNS + self.FEATURE_OPTIONAL_COLUMNS
        runname_exact = self.getExactRunName(runname)
        if runname_exact is None:
            return pd.DataFrame(columns=columns)
        else:
            return self.df[(self.df['runName'] == runname_exact) & (self.df['ModifiedPeptideSequence'] == pep_id) & (self.df['PrecursorCharge'] == charge)].copy()[columns]


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
    
    @requiredColumns('PrecursorCharge', 'ModifiedPeptideSequence')
    def addPrecursorColumn(self):
        '''
        adds 'Precursor' column to self.df if it does not exist
        '''
        if 'Precursor' not in self.df.columns:
            self.df['Precursor'] = self.df['ModifiedPeptideSequence'] + self.df['PrecursorCharge'].astype(str)

    @requiredColumns('ModifiedPeptideSequence', 'PrecursorCharge', 'Qvalue', 'runName')
    def getIdentifiedPrecursors(self, qvalue: float = 0.01, run:Optional[str] = None, precursorLevel = False) -> Union[set, Dict[str, set]]:
        self.addPrecursorColumn()
        
        # NOTE: currently there is no check if the correct context is loaded for the experiment
        if precursorLevel:
            peptide_protein_q_filter = True
        else:
            if self.peptide_protein_context is None:
                raise ValueError("Peptide-Protein context is not set, please specify the context to compute peptide and protein level q value")
            if 'Qvalue_peptide' not in self.df.columns and 'Qvalue_protein' not in self.df.columns: # check if peptide and protein q values are present
                self.appendColumns(['Qvalue_peptide', 'Qvalue_protein'])
            peptide_protein_q_filter = (self.df['Qvalue_peptide'] <= qvalue) & (self.df['Qvalue_protein'] <= qvalue)

        # If specify a run or only 1 run then just get a set of the precursors
        if isinstance(run, str) or self.getRunNames == 1:
            return self.df[(self.df['runName'] == run) & (self.df['Qvalue'] <= qvalue) & (peptide_protein_q_filter)]['Precursor']
        else: # multiple runs, return dictionary with runNames as keys
            return self.df[(self.df['Qvalue'] <= qvalue) & peptide_protein_q_filter ].groupby('runName').apply(lambda x: set(x['Precursor']), include_groups=False).to_dict()

    
    @requiredColumns('runName', 'Intensity', 'Rank') # note that 'Precursor' column is added in getIdentifiedPrecursors
    def getIdentifiedPrecursorIntensities(self, qvalue: float = 0.01, run: Optional[str] = None, precursorLevel = False) -> pd.DataFrame:
        '''
        Get a dataframe of identified precursors and their intensities (of only the top feature) from the results file 
        Args:
            qvalue (float): Qvalue threshold
            run (str): Run name
            precursorLevel (bool): If True, do not filter by protein Q.Value (only on precursor level) - "False" Only supported for DIA-NN results type will automatically be True otherwise
        '''
        ids = self.getIdentifiedPrecursors(qvalue=qvalue, run=run, precursorLevel=precursorLevel)

        if isinstance(ids, set):
            return self.df[(self.df['Precursor'].isin(ids)) & (self.df['Rank'] == 1)][['runName', 'Precursor', 'Intensity']]
        else: #isinstance(ids, dict)
            out = {}
            for run, precs in ids.items():
                out[run] = self.df[(self.df['Precursor'].isin(precs)) & (self.df['runName'] == run) & (self.df['Rank'] == 1)][['runName', 'Precursor', 'Intensity']].reset_index(drop=True)
            return pd.concat(out)

    @requiredColumns('ProteinId', 'runName')
    def getIdentifiedProteins(self, qvalue: float = 0.01, run:Optional[str] = None) -> Union[set, Dict[str, set]]:
        if self.peptide_protein_context is None:
            raise ValueError("Peptide-Protein context is not set, please specify the context to compute peptide and protein level q value")
        if not 'Qvalue_protein' in self.df.columns:
            self.appendColumns(['Qvalue_protein'])
        if isinstance(run, str):
            return set(self.df[(self.df['runName'] == run) & (self.df['Qvalue_protein'] <= qvalue)]['ProteinId'])
        else:
            return self.df[(self.df['Qvalue_protein'] <= qvalue)][['ProteinId', 'runName']].groupby(['runName']).apply(lambda x: set(x['ProteinId']), include_groups=False).to_dict()

    @requiredColumns('ModifiedPeptideSequence', 'runName')
    def getIdentifiedPeptides(self, qvalue: float = 0.01, run:Optional[str] = None) -> Union[set, Dict[str, set]]:
        if self.peptide_protein_context is None:
            raise ValueError("Peptide-Protein context is not set, please specify the context to compute peptide and protein level q value")
        if not 'Qvalue_peptide' in self.df.columns:
            self.appendColumns(['Qvalue_peptide'])
        if isinstance(run, str):
            return set(self.df[(self.df['runName'] == run) & (self.df['Qvalue_peptide'] <= qvalue)]['ModifiedPeptideSequence'])
        else:
            return self.df[(self.df['Qvalue_peptide'] <= qvalue)][['runName', 'ModifiedPeptideSequence']].groupby('runName').apply(lambda x: set(x['ModifiedPeptideSequence'])).to_dict()
    
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