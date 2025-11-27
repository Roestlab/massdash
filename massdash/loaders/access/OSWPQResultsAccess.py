"""
massdash/loaders/access/OSWPQResultsAccess
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import os
import pandas as pd
import numpy as np
from typing import List, Optional, Dict, Union, Literal
from pathlib import Path

# Loaders
from .GenericResultsAccess import GenericResultsAccess
# Structs
from ...structs.TransitionGroupFeature import TransitionGroupFeature
# Utils
from ...util import LOGGER

# Required imports for PyArrow
import pyarrow.dataset as ds
from functools import reduce, lru_cache
import operator

class OSWPQResultsAccess(GenericResultsAccess):
    """
    Class for accessing .oswpq directory containing precursors_features.parquet and transition_features.parquet files.
    
    The OSWPQResultsAccess class provides memory-efficient parsing of OpenSWATH results stored in Parquet format.
    See https://pyprophet.readthedocs.io/en/latest/file_formats.html#split-parquet-format-parquet-oswpq-oswpqd for details.
    It uses PyArrow datasets for lazy evaluation, avoiding loading entire files into memory and enabling efficient
    filtering and column projection at the parquet level.
    
    Parameters
    ----------
    filename : str
        Path to the .oswpq directory containing the required parquet files
    verbose : bool, optional
        Enable verbose logging (default: False)
        
    Raises
    ------
    ValueError
        If filename is not a directory
    FileNotFoundError
        If required parquet files are missing
    RuntimeError
        If parquet files cannot be loaded or PyArrow is not available
        
    Notes
    -----
    The .oswpq directory must contain exactly these two files:
    - precursors_features.parquet: Precursor-level features and scoring
    - transition_features.parquet: Transition-level features and intensities
    
    This class requires PyArrow for lazy evaluation using PyArrow datasets.
    
    Examples
    --------
    >>> access = OSWPQResultsAccess('/path/to/results.oswpq')
    >>> runs = access.getRunNames()
    >>> precursors = access.getIdentifiedPrecursors(qvalue=0.01)
    >>> has_im = access.has_im
    """

    def __init__(self, filename: str, verbose: bool = False) -> None:
        super().__init__(filename, verbose)
        self.filename = filename
        self.precursors_dataset = None
        self.transitions_dataset = None
        self._precursors_schema = None
        self._transitions_schema = None
        self._runHash = None
        
        # Validate that filename is a directory containing required files
        if not os.path.isdir(filename):
            raise ValueError(f"OSWPQResultsAccess requires a directory, got: {filename}")
        
        self.precursors_file = os.path.join(filename, 'precursors_features.parquet')
        self.transitions_file = os.path.join(filename, 'transition_features.parquet')
        
        if not os.path.exists(self.precursors_file):
            raise FileNotFoundError(f"Required file not found: {self.precursors_file}")
        if not os.path.exists(self.transitions_file):
            raise FileNotFoundError(f"Required file not found: {self.transitions_file}")
        
        # Initialize lazy datasets
        self._initialize_datasets()

        # Initialize run hash
        self._initialize_run_hash()

    def _initialize_run_hash(self):
        """Initialize run dictionary for run name to ID mapping"""
        tbl = self.precursors_dataset.to_table(columns=['FILENAME', 'RUN_ID'])
        unique_pairs = tbl.group_by(['FILENAME', 'RUN_ID']).aggregate([])
        self._runHash = unique_pairs.to_pandas()
        self._runHash['runName'] = self._runHash['FILENAME'].apply(lambda x: Path(x).stem)

    def _initialize_datasets(self):
        """Initialize pyarrow datasets for lazy evaluation"""
        try:
            # Use pyarrow.dataset for lazy loading and filtering
            self.precursors_dataset = ds.dataset(self.precursors_file, format="parquet")
            self.transitions_dataset = ds.dataset(self.transitions_file, format="parquet")
            # Cache schemas for metadata access
            self._precursors_schema = self.precursors_dataset.schema
            self._transitions_schema = self.transitions_dataset.schema
            LOGGER.info(f"Initialized lazy datasets for OSWPQ data: {self.filename}")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize pyarrow datasets: {e}")

    def _execute_precursor_query(self, filters=None, columns=None, append_precursor_col=True):
        """
        Execute a query on the precursors dataset with optional filters and column selection

        args
        filters: Optional list of filter tuples (column, operator, value)
        columns: Optional list of additional columns to select
        """

        # Validate requested columns only when we plan to append Precursor components
        if append_precursor_col and columns is not None:
            assert 'MODIFIED_SEQUENCE' not in columns, "MODIFIED_SEQUENCE cannot be in columns, it is added automatically"
            assert 'PRECURSOR_CHARGE' not in columns, "PRECURSOR_CHARGE cannot be in columns, it is added automatically"
            assert 'Precursor' not in columns, "Precursor cannot be in columns, it is added automatically"
        try:
            # Convert filters to pyarrow expressions if present
            filter_expr = OSWPQResultsAccess._execute_query_helper(filters)
            table = self.precursors_dataset.to_table(columns=columns + ['MODIFIED_SEQUENCE', 'PRECURSOR_CHARGE'] if append_precursor_col else columns, filter=filter_expr)
            df = table.to_pandas()
        except Exception as e:
            raise RuntimeError(f"PyArrow query failed: {e}")

        if append_precursor_col:
            df['Precursor'] = (
                df['MODIFIED_SEQUENCE'].astype(str) +
                df['PRECURSOR_CHARGE'].astype(str)
            )
            df = df.drop(columns=['MODIFIED_SEQUENCE', 'PRECURSOR_CHARGE'])
        return df
    def _execute_transition_query(self, filters=None, columns=None):
        """
        Execute a query on the transition dataset with optional filters and column selection

        args
        filters: Optional list of filter tuples (column, operator, value)
        columns: Optional list of additional columns to select
        """
    
        try:
            # Convert filters to pyarrow expressions if present
            filter_expr = OSWPQResultsAccess._execute_query_helper(filters)
            table = self.transitions_dataset.to_table(columns=columns, filter=filter_expr)
            df = table.to_pandas()
        except Exception as e:
            raise RuntimeError(f"PyArrow query failed: {e}")

        return df
    
    @staticmethod
    def _execute_query_helper(filters):
        filter_expr = None
        if filters:
            exprs = []
            for col, op, val in filters:
                if op == '==':
                    exprs.append(ds.field(col) == val)
                elif op == '<=':
                    exprs.append(ds.field(col) <= val)
                elif op == '>=':
                    exprs.append(ds.field(col) >= val)
                elif op == '<':
                    exprs.append(ds.field(col) < val)
                elif op == '>':
                    exprs.append(ds.field(col) > val)
                elif op == '!=':
                    exprs.append(ds.field(col) != val)
            if exprs:
                filter_expr = reduce(operator.and_, exprs)

        return filter_expr


    def getRunNames(self):
        return self._runHash['runName'].tolist()
    
    def _runIDFromRunName(self, run_name):
        df =  self._runHash[self._runHash['FILENAME'].str.contains(run_name, regex=False)]['RUN_ID']
        if df.empty:
            LOGGER.warning(f"Run name {run_name} not found.")
            return None
        else:
            return df.values[0]
 

    @property
    @lru_cache(maxsize=None)
    def has_im(self) -> bool:
        """Check if the data contains ion mobility information"""
        # Check schema first if available
        if self._precursors_schema is not None:
            im_columns = ['EXP_IM', 'FEATURE_MS1_EXP_IM', 'FEATURE_MS2_EXP_IM']
            schema_columns = [field.name for field in self._precursors_schema]
            return any(col in schema_columns for col in im_columns)

    
    def _add_context_specific_q_values(self, qvalue, context: Literal['global', 'run_specific', 'experiment_wide']):
        filters = []
        if context == 'run_specific':
            if 'SCORE_PEPTIDE_RUN_SPECIFIC_Q_VALUE' in [n.name for n in self._precursors_schema]:
                filters.append(('SCORE_PEPTIDE_RUN_SPECIFIC_Q_VALUE', '<=', qvalue))
            if 'SCORE_PROTEIN_RUN_SPECIFIC_Q_VALUE' in [n.name for n in self._precursors_schema]:
                filters.append(('SCORE_PROTEIN_RUN_SPECIFIC_Q_VALUE', '<=', qvalue))
        elif context == 'experiment_wide':
            if 'SCORE_PEPTIDE_EXPERIMENT_WIDE_Q_VALUE' in [n.name for n in self._precursors_schema]:
                filters.append(('SCORE_PEPTIDE_EXPERIMENT_WIDE_Q_VALUE', '<=', qvalue))
            if 'SCORE_PROTEIN_EXPERIMENT_WIDE_Q_VALUE' in [n.name for n in self._precursors_schema]:
                filters.append(('SCORE_PROTEIN_EXPERIMENT_WIDE_Q_VALUE', '<=', qvalue))
        elif context == 'global':
            if 'SCORE_PEPTIDE_GLOBAL_Q_VALUE' in [n.name for n in self._precursors_schema]:
                filters.append(('SCORE_PEPTIDE_GLOBAL_Q_VALUE', '<=', qvalue))
            if 'SCORE_PROTEIN_GLOBAL_Q_VALUE' in [n.name for n in self._precursors_schema]:
                filters.append(('SCORE_PROTEIN_GLOBAL_Q_VALUE', '<=', qvalue))
        return filters

   
    def _getIdentifiedPrecursorsHelper(self, qvalue: float = 0.01, run: Optional[str] = None, precursorLevel: bool = False, context: Literal['global', 'run_specific', 'experiment_wide'] = 'run_specific', columns=[]) -> pd.DataFrame:
        """Helper method to get identified precursors with specified filters and columns"""
        # Select necessary columns
        columns = [ 'FEATURE_MS2_AREA_INTENSITY' ]
        
        # Build filters for efficient querying
        filters = [
            ('PRECURSOR_DECOY', '==', 0),
            ('SCORE_MS2_Q_VALUE', '<=', qvalue),
            ('SCORE_MS2_PEAK_GROUP_RANK', '==', 1)  # Only include top-ranked peak groups
        ]
        if not precursorLevel:
            filters += self._add_context_specific_q_values(qvalue, context)

        if isinstance(run, str):
            # Filter by specific run
            run_id = self._runIDFromRunName(run)
            filters.append(('RUN_ID', '==', run_id))
        else:
            columns.append('RUN_ID')

        filtered_df = self._execute_precursor_query(filters=filters, columns=columns, append_precursor_col=True)
        filtered_df = filtered_df.rename(columns={'FEATURE_MS2_AREA_INTENSITY': 'Intensity'})
        
        if not isinstance(run, str):
            filtered_df = filtered_df.merge(self._runHash[['RUN_ID', 'runName']], on='RUN_ID').drop(columns=['RUN_ID'])
        return filtered_df
    
    def getIdentifiedPrecursors(self, qvalue: float = 0.01, run: Optional[str] = None, precursorLevel: bool = False, context: Literal['global', 'run_specific', 'experiment_wide'] = 'run_specific') -> Union[set, Dict[str, set]]:
        """Get identified precursors at specified q-value threshold"""
        # Use the appropriate q-value column based on precursorLevel
        filtered_df = self._getIdentifiedPrecursorsHelper(qvalue, run, precursorLevel, context)
        if isinstance(run, str):
            return set(filtered_df['Precursor'].unique())
        else:
            return filtered_df.groupby('runName')['Precursor'].apply(set).to_dict()

    def getIdentifiedPrecursorIntensities(self, qvalue: float = 0.01, run: Optional[str] = None, precursorLevel: bool = False, context: Literal['global', 'run_specific', 'experiment_wide'] = 'run_specific') -> pd.DataFrame:
        """Get identified precursor intensities"""
        filtered_df = self._getIdentifiedPrecursorsHelper(qvalue, run, precursorLevel, context, columns=['FEATURE_MS2_AREA_INTENSITY'])
        filtered_df = filtered_df.rename(columns={'FEATURE_MS2_AREA_INTENSITY': 'Intensity'})
        
        return filtered_df

    def getIdentifiedProteins(self, qvalue: float = 0.01, run: Optional[str] = None, context: Literal['global', 'run_specific', 'experiment_wide'] = 'run_specific') -> Union[set, Dict[str, set]]:
        """Get identified proteins"""
        # Use peptide-level q-value for protein identification
        if context == 'run_specific':
            qvalue_col = 'SCORE_PROTEIN_RUN_SPECIFIC_Q_VALUE'
        elif context == 'experiment_wide':
            qvalue_col = 'SCORE_PROTEIN_EXPERIMENT_WIDE_Q_VALUE'
        elif context == 'global':
            qvalue_col = 'SCORE_PROTEIN_GLOBAL_Q_VALUE'
        else:
            raise ValueError(f"Invalid context: {context}. Must be one of 'global', 'run_specific', or 'experiment_wide'.")

        filters = [
            ('PROTEIN_DECOY', '==', 0),
            (qvalue_col, '<=', qvalue)
        ]

        columns = ['PROTEIN_ACCESSION', qvalue_col]
        if isinstance(run, str):
            # Filter by specific run
            run_id = self._runIDFromRunName(run)
            filters.append(('RUN_ID', '==', run_id))
        else:
            columns.append('RUN_ID')

        filtered_df = self._execute_precursor_query(filters=filters, columns=columns, append_precursor_col=False)
        
        if isinstance(run, str):
            return set(filtered_df['PROTEIN_ACCESSION']) 
        else:
            filtered_df = filtered_df.merge(self._runHash[['RUN_ID', 'runName']], on='RUN_ID').drop(columns=['RUN_ID'])
            return filtered_df.groupby('runName')['PROTEIN_ACCESSION'].apply(set).to_dict()

    def getIdentifiedPeptides(self, qvalue: float = 0.01, run: Optional[str] = None, context: Literal['global', 'run_specific', 'experiment_wide'] = 'run_specific') -> Union[set, Dict[str, set]]:
        """Get identified peptides"""
        # Use peptide-level q-value for peptide identification
        if context == 'run_specific':
            qvalue_col = 'SCORE_PEPTIDE_RUN_SPECIFIC_Q_VALUE'
        elif context == 'experiment_wide':
            qvalue_col = 'SCORE_PEPTIDE_EXPERIMENT_WIDE_Q_VALUE'
        elif context == 'global':
            qvalue_col = 'SCORE_PEPTIDE_GLOBAL_Q_VALUE'
        else:
            raise ValueError(f"Invalid context: {context}. Must be one of 'global', 'run_specific', or 'experiment_wide'.")

        filters = [
            ('PEPTIDE_DECOY', '==', 0),
            (qvalue_col, '<=', qvalue)
        ]

        columns = ['MODIFIED_SEQUENCE', qvalue_col]
        if isinstance(run, str):
            # Filter by specific run
            run_id = self._runIDFromRunName(run)
            filters.append(('RUN_ID', '==', run_id))
        else:
            columns.append('RUN_ID')

        filtered_df = self._execute_precursor_query(filters=filters, columns=columns, append_precursor_col=False)

        if isinstance(run, str):
            return set(filtered_df['MODIFIED_SEQUENCE']) 
        else:
            filtered_df = filtered_df.merge(self._runHash[['RUN_ID', 'runName']], on='RUN_ID').drop(columns=['RUN_ID'])
            return filtered_df.groupby('runName')['MODIFIED_SEQUENCE'].apply(set).to_dict()

    def getSoftware(self) -> str:
        """Return software name"""
        return "OpenSWATH"

    def _getTransitionGroupFeaturesHelper(self, runname: str, pep: str, charge: int, columns=None) -> pd.DataFrame:
        """ Helper method to get transition group features with specified filters and columns"""
        # Build filters for efficient querying
        filters = [
            ('MODIFIED_SEQUENCE', '==', pep),
            ('PRECURSOR_CHARGE', '==', charge)
        ]
        
        # Select necessary columns
        columns = [
            'RUN_ID',
            'LEFT_WIDTH', 'RIGHT_WIDTH', 'FEATURE_MS2_AREA_INTENSITY',
            'SCORE_MS2_Q_VALUE', 'EXP_RT', 'FEATURE_MS2_APEX_INTENSITY',
            'PRECURSOR_MZ'
        ]
        if self.has_im:
            columns.append('EXP_IM')

        if isinstance(runname, str):
            # Filter by specific run
            run_id = self._runIDFromRunName(runname)
            filters.append(('RUN_ID', '==', run_id))
        
        return self._execute_precursor_query(filters=filters, columns=columns, append_precursor_col=True)
    
    def getTransitionGroupFeatures(self, runname: str, pep: str, charge: int) -> List[TransitionGroupFeature]:
        """Get transition group features for a specific peptide and charge"""

        filtered_df = self._getTransitionGroupFeaturesHelper(runname, pep, charge)
        
        features = []
        for _, row in filtered_df.iterrows():
            feature = TransitionGroupFeature(
                leftBoundary=row.get('LEFT_WIDTH', 0),
                rightBoundary=row.get('RIGHT_WIDTH', 0),
                areaIntensity=row.get('FEATURE_MS2_AREA_INTENSITY', 0),
                qvalue=row.get('SCORE_MS2_Q_VALUE', 1.0),
                consensusApex=row.get('EXP_RT', 0),
                consensusApexIntensity=row.get('FEATURE_MS2_APEX_INTENSITY', 0),
                consensusApexIM=row.get('EXP_IM') if self.has_im else None,
                precursor_mz=row.get('PRECURSOR_MZ'),
                sequence=pep,
                precursor_charge = charge,
                software=self.getSoftware()
            )
            features.append(feature)
        
        return features

    def getTransitionGroupFeaturesDf(self, runname: str, pep: str, charge: int) -> pd.DataFrame:
        """Get transition group features as DataFrame"""
        # Build filters for efficient querying
        filtered_df = self._getTransitionGroupFeaturesHelper(runname, pep, charge)

        filtered_df.rename(columns={
            'LEFT_WIDTH': 'leftBoundary',
            'RIGHT_WIDTH': 'rightBoundary',
            'FEATURE_MS2_AREA_INTENSITY': 'areaIntensity',
            'SCORE_MS2_Q_VALUE': 'qvalue',
            'EXP_RT': 'consensusApex',
            'FEATURE_MS2_APEX_INTENSITY': 'consensusApexIntensity',
            'EXP_IM': 'consensusApexIM',
            'PRECURSOR_CHARGE': 'precursor_charge',
            'MODIFIED_SEQUENCE': 'sequence'
        }, inplace=True)
        filtered_df['software'] = self.getSoftware()
        filtered_df['sequence'] = pep
        filtered_df['precursor_charge'] = charge

        return filtered_df
       
    def getTopTransitionGroupFeature(self, runname: str, pep: str, charge: int) -> TransitionGroupFeature:
        """Get the top (best q-value) transition group feature"""
        features = self.getTransitionGroupFeatures(runname, pep, charge)
        if not features:
            return None
        
        # Return the feature with the best (lowest) q-value
        try:
            return min(features, key=lambda f: f.qvalue)
        except ValueError:
            raise RuntimeError("results must be scored to select the top feature")
        
    def getTopTransitionGroupFeatureDf(self, runname: str, pep: str, charge: int) -> pd.DataFrame:
        """Get the top (best q-value) transition group feature as DataFrame"""
        features = self.getTransitionGroupFeaturesDf(runname, pep, charge)
        try:
            return features[features.qvalue == min(features.qvalue)]
        except ValueError:
            LOGGER.warning("No features found for the specified peptide and charge.")
            return pd.DataFrame(columns=self.columns)
        
    def getPrecursorID(self, pep: str, charge: int) -> Optional[int]:
        """Get precursor ID for a given peptide and charge"""
        filters = [
            ('MODIFIED_SEQUENCE', '==', pep),
            ('PRECURSOR_CHARGE', '==', charge)
        ]
        df = self._execute_precursor_query(filters=filters, columns=['PRECURSOR_ID'], append_precursor_col=False)
        if not df.empty:
            return df['PRECURSOR_ID'].iloc[0]
        else:
            LOGGER.warning(f"No precursor ID found for {pep} {charge}.")
            return None

    def populateTransitionGroupFeature(self, transition_group_feature: TransitionGroupFeature) -> TransitionGroupFeature:
        """
        Appends library information to a TransitionGroupFeature object

        Args:
            transition_group_feature (TransitionGroupFeature): The TransitionGroupFeature object to append library information to.

        Returns:
            TransitionGroupFeature: The TransitionGroupFeature object with appended library information.
        """

        # determine the precursor_id from sequence and charge
        precursor_id = self.getPrecursorID(transition_group_feature.sequence, transition_group_feature.precursor_charge)


        # from the precursor id get the library data found in transition_features.parquet
        filters = [
            ('PRECURSOR_ID', '==', precursor_id)
        ]
        df_transitionLvl = self._execute_transition_query(filters=filters, columns=['ANNOTATION', 'PRODUCT_MZ'])
        df_precursorLvl = self._execute_precursor_query(filters=filters, columns=['PRECURSOR_MZ'], append_precursor_col=False)

        if df_transitionLvl.empty:
            LOGGER.warning(f"No library data found for {transition_group_feature.sequence} {transition_group_feature.precursor_charge}")
            return transition_group_feature
        transition_group_feature.product_annotations = df_transitionLvl['ANNOTATION'].tolist()
        transition_group_feature.product_mz = df_transitionLvl['PRODUCT_MZ'].tolist()
        transition_group_feature.precursor_mz = df_precursorLvl['PRECURSOR_MZ'].iloc[0]
        return transition_group_feature