"""
massdash/loaders/access/OSWPQResultsAccess
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import os
import pandas as pd
import numpy as np
from typing import List, Optional, Dict, Union
from pathlib import Path

# Loaders
from .GenericResultsAccess import GenericResultsAccess
# Structs
from ...structs.TransitionGroupFeature import TransitionGroupFeature
# Utils
from ...util import LOGGER

# Required imports for PyArrow
import pyarrow as pa
import pyarrow.parquet as pq
import pyarrow.compute as pc

class OSWPQResultsAccess(GenericResultsAccess):
    """
    Class for accessing .oswpq directory containing precursors_features.parquet and transition_features.parquet files.
    
    The OSWPQResultsAccess class provides memory-efficient parsing of OpenSWATH results stored in Parquet format.
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
        
    def _initialize_datasets(self):
        """Initialize pyarrow datasets for lazy evaluation"""
        try:
            # Use pyarrow datasets for lazy loading
            self.precursors_dataset = pq.ParquetDataset(self.precursors_file)
            self.transitions_dataset = pq.ParquetDataset(self.transitions_file)
            
            # Cache schemas for metadata access
            self._precursors_schema = self.precursors_dataset.schema
            self._transitions_schema = self.transitions_dataset.schema
            
            LOGGER.info(f"Initialized lazy datasets for OSWPQ data: {self.filename}")
            
        except Exception as e:
            raise RuntimeError(f"Failed to initialize pyarrow datasets: {e}")

    def _execute_precursor_query(self, filters=None, columns=None):
        """Execute a query on the precursors dataset with optional filters and column selection"""
        try:
            # Use pyarrow for efficient filtering and column selection
            table = self.precursors_dataset.read(columns=columns, filters=filters)
            df = table.to_pandas()
            
            # Add helper column if not already present
            if 'Precursor' not in df.columns and 'MODIFIED_SEQUENCE' in df.columns and 'PRECURSOR_CHARGE' in df.columns:
                df['Precursor'] = (
                    df['MODIFIED_SEQUENCE'].astype(str) + 
                    df['PRECURSOR_CHARGE'].astype(str)
                )
            
            return df
        except Exception as e:
            raise RuntimeError(f"PyArrow query failed: {e}")


    @property
    def has_im(self) -> bool:
        """Check if the data contains ion mobility information"""
        # Check schema first if available
        if self._precursors_schema is not None:
            im_columns = ['EXP_IM', 'FEATURE_MS1_EXP_IM', 'FEATURE_MS2_EXP_IM']
            schema_columns = [field.name for field in self._precursors_schema]
            return any(col in schema_columns for col in im_columns)
        
        # Fallback to checking a small sample
        sample_df = self._execute_precursor_query(
            columns=['EXP_IM', 'FEATURE_MS1_EXP_IM', 'FEATURE_MS2_EXP_IM']
        )
        if sample_df.empty:
            return False
            
        for col in ['EXP_IM', 'FEATURE_MS1_EXP_IM', 'FEATURE_MS2_EXP_IM']:
            if col in sample_df.columns and not sample_df[col].isna().all():
                return True
        return False

    def getRunNames(self) -> List[str]:
        """Get list of run names from the data"""
        # Query only the columns we need
        df = self._execute_precursor_query(columns=['FILENAME', 'RUN_ID'])
        
        if 'FILENAME' in df.columns:
            # Extract basename without extension
            return [Path(f).stem for f in df['FILENAME'].unique()]
        else:
            # Fallback to RUN_ID if FILENAME is not available
            return [f"run_{rid}" for rid in df['RUN_ID'].unique()]

    def getIdentifiedPrecursors(self, qvalue: float = 0.01, run: Optional[str] = None, precursorLevel: bool = False) -> Union[set, Dict[str, set]]:
        """Get identified precursors at specified q-value threshold"""
        # Use the appropriate q-value column based on precursorLevel
        if precursorLevel:
            qvalue_col = 'SCORE_MS2_Q_VALUE'
        else:
            # Use protein-level q-value if available, fallback to peptide-level
            qvalue_col = 'SCORE_PEPTIDE_RUN_SPECIFIC_Q_VALUE'  # Will check if exists in query
        
        # Build filters for efficient querying
        filters = [
            ('PRECURSOR_DECOY', '==', 0)
        ]
        
        # Add q-value filter
        filters.append((qvalue_col, '<=', qvalue))
        
        # Select only necessary columns
        columns = ['Precursor', 'MODIFIED_SEQUENCE', 'PRECURSOR_CHARGE', 'FILENAME', 'RUN_ID', qvalue_col, 'PRECURSOR_DECOY']
        
        # Add fallback column if primary doesn't exist
        if not precursorLevel:
            columns.append('SCORE_MS2_Q_VALUE')
        
        filtered_df = self._execute_precursor_query(filters=filters, columns=columns)
        
        # Handle fallback q-value column if the preferred one doesn't exist
        if qvalue_col not in filtered_df.columns:
            if precursorLevel:
                return set() if isinstance(run, str) else {}
            else:
                qvalue_col = 'SCORE_MS2_Q_VALUE'
                filtered_df = filtered_df[filtered_df[qvalue_col] <= qvalue]
        
        if isinstance(run, str):
            # Filter by specific run
            if 'FILENAME' in filtered_df.columns:
                run_filtered = filtered_df[filtered_df['FILENAME'].str.contains(run, na=False)]
            else:
                # Try to match by RUN_ID
                try:
                    run_id = int(run.replace('run_', ''))
                    run_filtered = filtered_df[filtered_df['RUN_ID'] == run_id]
                except:
                    run_filtered = pd.DataFrame()
            
            return set(run_filtered['Precursor']) if 'Precursor' in run_filtered.columns else set()
        else:
            # Group by run and return dict
            if 'FILENAME' in filtered_df.columns:
                return filtered_df.groupby('FILENAME')['Precursor'].apply(set).to_dict()
            else:
                return filtered_df.groupby('RUN_ID')['Precursor'].apply(set).to_dict()

    def getIdentifiedPrecursorIntensities(self, qvalue: float = 0.01, run: Optional[str] = None, precursorLevel: bool = False) -> pd.DataFrame:
        """Get identified precursor intensities"""
        # Use the appropriate q-value column
        if precursorLevel:
            qvalue_col = 'SCORE_MS2_Q_VALUE'
        else:
            qvalue_col = 'SCORE_PEPTIDE_RUN_SPECIFIC_Q_VALUE'
        
        # Build filters for efficient querying
        filters = [
            ('PRECURSOR_DECOY', '==', 0),
            (qvalue_col, '<=', qvalue)
        ]
        
        # Select necessary columns
        columns = [
            'Precursor', 'MODIFIED_SEQUENCE', 'PRECURSOR_CHARGE',
            'FILENAME', 'RUN_ID', qvalue_col, 'PRECURSOR_DECOY',
            'FEATURE_MS2_AREA_INTENSITY', 'FEATURE_MS1_AREA_INTENSITY'
        ]
        
        filtered_df = self._execute_precursor_query(filters=filters, columns=columns)
        
        # Handle fallback q-value column
        if qvalue_col not in filtered_df.columns:
            if not precursorLevel:
                qvalue_col = 'SCORE_MS2_Q_VALUE'
                columns.append(qvalue_col)
                filtered_df = self._execute_precursor_query(filters=[
                    ('PRECURSOR_DECOY', '==', 0),
                    (qvalue_col, '<=', qvalue)
                ], columns=columns)
        
        # Use MS2 area intensity as the main intensity measure
        intensity_col = 'FEATURE_MS2_AREA_INTENSITY'
        if intensity_col not in filtered_df.columns:
            intensity_col = 'FEATURE_MS1_AREA_INTENSITY'  # Fallback
        
        if isinstance(run, str):
            # Filter by specific run
            if 'FILENAME' in filtered_df.columns:
                run_filtered = filtered_df[filtered_df['FILENAME'].str.contains(run, na=False)]
            else:
                try:
                    run_id = int(run.replace('run_', ''))
                    run_filtered = filtered_df[filtered_df['RUN_ID'] == run_id]
                except:
                    run_filtered = pd.DataFrame()
            
            result = run_filtered[['Precursor', intensity_col]].rename(columns={intensity_col: 'Intensity'}).copy()
            return result
        else:
            # Include run information
            result_df = filtered_df[['Precursor', intensity_col]].copy()
            result_df['Intensity'] = result_df[intensity_col]
            
            if 'FILENAME' in filtered_df.columns:
                result_df['runName'] = filtered_df['FILENAME'].apply(lambda x: Path(x).stem)
            else:
                result_df['runName'] = filtered_df['RUN_ID'].apply(lambda x: f"run_{x}")
            
            return result_df[['runName', 'Precursor', 'Intensity']].copy()

    def getIdentifiedProteins(self, qvalue: float = 0.01, run: Optional[str] = None) -> Union[set, Dict[str, set]]:
        """Get identified proteins"""
        # Use peptide-level q-value for protein identification
        qvalue_col = 'SCORE_PEPTIDE_RUN_SPECIFIC_Q_VALUE'
        
        filters = [
            ('PROTEIN_DECOY', '==', 0),
            (qvalue_col, '<=', qvalue)
        ]
        
        columns = ['PROTEIN_ACCESSION', 'FILENAME', 'RUN_ID', qvalue_col, 'PROTEIN_DECOY']
        
        filtered_df = self._execute_precursor_query(filters=filters, columns=columns)
        
        # Handle fallback q-value column
        if qvalue_col not in filtered_df.columns:
            qvalue_col = 'SCORE_MS2_Q_VALUE'
            columns.append(qvalue_col)
            filtered_df = self._execute_precursor_query(filters=[
                ('PROTEIN_DECOY', '==', 0),
                (qvalue_col, '<=', qvalue)
            ], columns=columns)
        
        if isinstance(run, str):
            if 'FILENAME' in filtered_df.columns:
                run_filtered = filtered_df[filtered_df['FILENAME'].str.contains(run, na=False)]
            else:
                try:
                    run_id = int(run.replace('run_', ''))
                    run_filtered = filtered_df[filtered_df['RUN_ID'] == run_id]
                except:
                    run_filtered = pd.DataFrame()
            
            return set(run_filtered['PROTEIN_ACCESSION']) if 'PROTEIN_ACCESSION' in run_filtered.columns else set()
        else:
            if 'FILENAME' in filtered_df.columns:
                return filtered_df.groupby('FILENAME')['PROTEIN_ACCESSION'].apply(set).to_dict()
            else:
                return filtered_df.groupby('RUN_ID')['PROTEIN_ACCESSION'].apply(set).to_dict()

    def getIdentifiedPeptides(self, qvalue: float = 0.01, run: Optional[str] = None) -> Union[set, Dict[str, set]]:
        """Get identified peptides"""
        qvalue_col = 'SCORE_PEPTIDE_RUN_SPECIFIC_Q_VALUE'
        
        filters = [
            ('PEPTIDE_DECOY', '==', 0),
            (qvalue_col, '<=', qvalue)
        ]
        
        columns = ['MODIFIED_SEQUENCE', 'FILENAME', 'RUN_ID', qvalue_col, 'PEPTIDE_DECOY']
        
        filtered_df = self._execute_precursor_query(filters=filters, columns=columns)
        
        # Handle fallback q-value column
        if qvalue_col not in filtered_df.columns:
            qvalue_col = 'SCORE_MS2_Q_VALUE'
            columns.append(qvalue_col)
            filtered_df = self._execute_precursor_query(filters=[
                ('PEPTIDE_DECOY', '==', 0),
                (qvalue_col, '<=', qvalue)
            ], columns=columns)
        
        if isinstance(run, str):
            if 'FILENAME' in filtered_df.columns:
                run_filtered = filtered_df[filtered_df['FILENAME'].str.contains(run, na=False)]
            else:
                try:
                    run_id = int(run.replace('run_', ''))
                    run_filtered = filtered_df[filtered_df['RUN_ID'] == run_id]
                except:
                    run_filtered = pd.DataFrame()
            
            return set(run_filtered['MODIFIED_SEQUENCE']) if 'MODIFIED_SEQUENCE' in run_filtered.columns else set()
        else:
            if 'FILENAME' in filtered_df.columns:
                return filtered_df.groupby('FILENAME')['MODIFIED_SEQUENCE'].apply(set).to_dict()
            else:
                return filtered_df.groupby('RUN_ID')['MODIFIED_SEQUENCE'].apply(set).to_dict()

    def getSoftware(self) -> str:
        """Return software name"""
        return "OpenSWATH-OSWPQ"

    def getTransitionGroupFeatures(self, runname: str, pep: str, charge: int) -> List[TransitionGroupFeature]:
        """Get transition group features for a specific peptide and charge"""
        # Build filters for efficient querying
        filters = [
            ('MODIFIED_SEQUENCE', '==', pep),
            ('PRECURSOR_CHARGE', '==', charge)
        ]
        
        # Select necessary columns
        columns = [
            'MODIFIED_SEQUENCE', 'PRECURSOR_CHARGE', 'FILENAME', 'RUN_ID',
            'LEFT_WIDTH', 'RIGHT_WIDTH', 'FEATURE_MS2_AREA_INTENSITY',
            'SCORE_MS2_Q_VALUE', 'EXP_RT', 'FEATURE_MS2_APEX_INTENSITY',
            'EXP_IM', 'PRECURSOR_MZ'
        ]
        
        filtered_df = self._execute_precursor_query(filters=filters, columns=columns)
        
        # Filter by run
        if 'FILENAME' in filtered_df.columns:
            run_filtered = filtered_df[filtered_df['FILENAME'].str.contains(runname, na=False)]
        else:
            try:
                run_id = int(runname.replace('run_', ''))
                run_filtered = filtered_df[filtered_df['RUN_ID'] == run_id]
            except:
                run_filtered = pd.DataFrame()
        
        features = []
        for _, row in run_filtered.iterrows():
            feature = TransitionGroupFeature(
                leftBoundary=row.get('LEFT_WIDTH', 0),
                rightBoundary=row.get('RIGHT_WIDTH', 0),
                areaIntensity=row.get('FEATURE_MS2_AREA_INTENSITY', 0),
                qvalue=row.get('SCORE_MS2_Q_VALUE', 1.0),
                consensusApex=row.get('EXP_RT', 0),
                consensusApexIntensity=row.get('FEATURE_MS2_APEX_INTENSITY', 0),
                consensusApexIM=row.get('EXP_IM') if self.has_im else None,
                precursor_mz=row.get('PRECURSOR_MZ'),
                precursor_charge=row.get('PRECURSOR_CHARGE'),
                sequence=row.get('MODIFIED_SEQUENCE'),
                software=self.getSoftware()
            )
            features.append(feature)
        
        return features

    def getTransitionGroupFeaturesDf(self, runname: str, pep: str, charge: int) -> pd.DataFrame:
        """Get transition group features as DataFrame"""
        # Build filters for efficient querying
        filters = [
            ('MODIFIED_SEQUENCE', '==', pep),
            ('PRECURSOR_CHARGE', '==', charge)
        ]
        
        # Select necessary columns
        columns = [
            'MODIFIED_SEQUENCE', 'PRECURSOR_CHARGE', 'FILENAME', 'RUN_ID',
            'LEFT_WIDTH', 'RIGHT_WIDTH', 'FEATURE_MS2_AREA_INTENSITY',
            'SCORE_MS2_Q_VALUE', 'EXP_RT', 'FEATURE_MS2_APEX_INTENSITY',
            'EXP_IM'
        ]
        
        filtered_df = self._execute_precursor_query(filters=filters, columns=columns)
        
        # Filter by run
        if 'FILENAME' in filtered_df.columns:
            run_filtered = filtered_df[filtered_df['FILENAME'].str.contains(runname, na=False)]
        else:
            try:
                run_id = int(runname.replace('run_', ''))
                run_filtered = filtered_df[filtered_df['RUN_ID'] == run_id]
            except:
                run_filtered = pd.DataFrame()
        
        if run_filtered.empty:
            return pd.DataFrame(columns=self.columns)
        
        # Map columns to expected format
        result_df = pd.DataFrame({
            'leftBoundary': run_filtered.get('LEFT_WIDTH', 0),
            'rightBoundary': run_filtered.get('RIGHT_WIDTH', 0),
            'areaIntensity': run_filtered.get('FEATURE_MS2_AREA_INTENSITY', 0),
            'qvalue': run_filtered.get('SCORE_MS2_Q_VALUE', 1.0),
            'consensusApex': run_filtered.get('EXP_RT', 0),
            'consensusApexIntensity': run_filtered.get('FEATURE_MS2_APEX_INTENSITY', 0),
            'precursor_charge': run_filtered.get('PRECURSOR_CHARGE'),
            'sequence': run_filtered.get('MODIFIED_SEQUENCE'),
            'software': self.getSoftware()
        })
        
        if self.has_im:
            result_df['consensusApexIM'] = run_filtered.get('EXP_IM')
        
        return result_df[self.columns]

    def getTopTransitionGroupFeature(self, runname: str, pep: str, charge: int) -> TransitionGroupFeature:
        """Get the top (best q-value) transition group feature"""
        features = self.getTransitionGroupFeatures(runname, pep, charge)
        if not features:
            return None
        
        # Return the feature with the best (lowest) q-value
        return min(features, key=lambda f: f.qvalue if f.qvalue is not None else float('inf'))