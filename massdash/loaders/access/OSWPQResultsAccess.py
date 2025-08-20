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

class OSWPQResultsAccess(GenericResultsAccess):
    """
    Class for accessing .oswpq directory containing precursors_features.parquet and transition_features.parquet files.
    """

    def __init__(self, filename: str, verbose: bool = False) -> None:
        super().__init__(filename, verbose)
        self.filename = filename
        self.precursors_df = None
        self.transitions_df = None
        
        # Validate that filename is a directory containing required files
        if not os.path.isdir(filename):
            raise ValueError(f"OSWPQResultsAccess requires a directory, got: {filename}")
        
        precursors_file = os.path.join(filename, 'precursors_features.parquet')
        transitions_file = os.path.join(filename, 'transition_features.parquet')
        
        if not os.path.exists(precursors_file):
            raise FileNotFoundError(f"Required file not found: {precursors_file}")
        if not os.path.exists(transitions_file):
            raise FileNotFoundError(f"Required file not found: {transitions_file}")
        
        # Load the parquet files
        self._load_data(precursors_file, transitions_file)
        
    def _load_data(self, precursors_file: str, transitions_file: str):
        """Load the parquet files into dataframes"""
        try:
            self.precursors_df = pd.read_parquet(precursors_file)
            self.transitions_df = pd.read_parquet(transitions_file)
            
            # Create helper columns for easier access
            self.precursors_df['Precursor'] = (
                self.precursors_df['MODIFIED_SEQUENCE'].astype(str) + 
                self.precursors_df['PRECURSOR_CHARGE'].astype(str)
            )
            
            LOGGER.info(f"Loaded {len(self.precursors_df)} precursor features and {len(self.transitions_df)} transition features")
            
        except Exception as e:
            raise RuntimeError(f"Failed to load parquet files: {e}")

    @property
    def has_im(self) -> bool:
        """Check if the data contains ion mobility information"""
        # Check if any IM-related columns have non-null values
        im_columns = ['EXP_IM', 'FEATURE_MS1_EXP_IM', 'FEATURE_MS2_EXP_IM']
        for col in im_columns:
            if col in self.precursors_df.columns:
                if not self.precursors_df[col].isna().all():
                    return True
        return False

    def getRunNames(self) -> List[str]:
        """Get list of run names from the data"""
        if 'FILENAME' in self.precursors_df.columns:
            # Extract basename without extension
            return [Path(f).stem for f in self.precursors_df['FILENAME'].unique()]
        else:
            # Fallback to RUN_ID if FILENAME is not available
            return [f"run_{rid}" for rid in self.precursors_df['RUN_ID'].unique()]

    def getIdentifiedPrecursors(self, qvalue: float = 0.01, run: Optional[str] = None, precursorLevel: bool = False) -> Union[set, Dict[str, set]]:
        """Get identified precursors at specified q-value threshold"""
        # Use the appropriate q-value column based on precursorLevel
        if precursorLevel:
            qvalue_col = 'SCORE_MS2_Q_VALUE'
        else:
            # Use protein-level q-value if available, fallback to peptide-level
            if 'SCORE_PEPTIDE_RUN_SPECIFIC_Q_VALUE' in self.precursors_df.columns:
                qvalue_col = 'SCORE_PEPTIDE_RUN_SPECIFIC_Q_VALUE'
            else:
                qvalue_col = 'SCORE_MS2_Q_VALUE'
        
        # Filter by q-value and non-decoy
        filtered_df = self.precursors_df[
            (self.precursors_df[qvalue_col] <= qvalue) & 
            (self.precursors_df['PRECURSOR_DECOY'] == 0)
        ]
        
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
            
            return set(run_filtered['Precursor'])
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
            if 'SCORE_PEPTIDE_RUN_SPECIFIC_Q_VALUE' in self.precursors_df.columns:
                qvalue_col = 'SCORE_PEPTIDE_RUN_SPECIFIC_Q_VALUE'
            else:
                qvalue_col = 'SCORE_MS2_Q_VALUE'
        
        # Filter by q-value and non-decoy
        filtered_df = self.precursors_df[
            (self.precursors_df[qvalue_col] <= qvalue) & 
            (self.precursors_df['PRECURSOR_DECOY'] == 0)
        ]
        
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
            
            return run_filtered[['Precursor', intensity_col]].rename(columns={intensity_col: 'Intensity'}).copy()
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
        if 'SCORE_PEPTIDE_RUN_SPECIFIC_Q_VALUE' in self.precursors_df.columns:
            qvalue_col = 'SCORE_PEPTIDE_RUN_SPECIFIC_Q_VALUE'
        else:
            qvalue_col = 'SCORE_MS2_Q_VALUE'
        
        filtered_df = self.precursors_df[
            (self.precursors_df[qvalue_col] <= qvalue) & 
            (self.precursors_df['PROTEIN_DECOY'] == 0)
        ]
        
        if isinstance(run, str):
            if 'FILENAME' in filtered_df.columns:
                run_filtered = filtered_df[filtered_df['FILENAME'].str.contains(run, na=False)]
            else:
                try:
                    run_id = int(run.replace('run_', ''))
                    run_filtered = filtered_df[filtered_df['RUN_ID'] == run_id]
                except:
                    run_filtered = pd.DataFrame()
            
            return set(run_filtered['PROTEIN_ACCESSION'])
        else:
            if 'FILENAME' in filtered_df.columns:
                return filtered_df.groupby('FILENAME')['PROTEIN_ACCESSION'].apply(set).to_dict()
            else:
                return filtered_df.groupby('RUN_ID')['PROTEIN_ACCESSION'].apply(set).to_dict()

    def getIdentifiedPeptides(self, qvalue: float = 0.01, run: Optional[str] = None) -> Union[set, Dict[str, set]]:
        """Get identified peptides"""
        if 'SCORE_PEPTIDE_RUN_SPECIFIC_Q_VALUE' in self.precursors_df.columns:
            qvalue_col = 'SCORE_PEPTIDE_RUN_SPECIFIC_Q_VALUE'
        else:
            qvalue_col = 'SCORE_MS2_Q_VALUE'
        
        filtered_df = self.precursors_df[
            (self.precursors_df[qvalue_col] <= qvalue) & 
            (self.precursors_df['PEPTIDE_DECOY'] == 0)
        ]
        
        if isinstance(run, str):
            if 'FILENAME' in filtered_df.columns:
                run_filtered = filtered_df[filtered_df['FILENAME'].str.contains(run, na=False)]
            else:
                try:
                    run_id = int(run.replace('run_', ''))
                    run_filtered = filtered_df[filtered_df['RUN_ID'] == run_id]
                except:
                    run_filtered = pd.DataFrame()
            
            return set(run_filtered['MODIFIED_SEQUENCE'])
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
        # Find matching features
        filtered_df = self.precursors_df[
            (self.precursors_df['MODIFIED_SEQUENCE'] == pep) & 
            (self.precursors_df['PRECURSOR_CHARGE'] == charge)
        ]
        
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
        # Find matching features
        filtered_df = self.precursors_df[
            (self.precursors_df['MODIFIED_SEQUENCE'] == pep) & 
            (self.precursors_df['PRECURSOR_CHARGE'] == charge)
        ]
        
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