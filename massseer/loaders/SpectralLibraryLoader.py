from abc import ABC, abstractmethod
from typing import List
import os
import pandas as pd
import streamlit as st

from massseer.loaders.TransitionTSVLoader import TransitionTSVLoader
from massseer.loaders.TransitionPQPLoader import TransitionPQPLoader

from massseer.util import get_logger

# # single const instance of logger
LOGGER = get_logger(__name__)

class SpectralLibraryLoader:

    def __init__(self, in_file) -> None:
        self.in_file = in_file
        self.data: pd.DataFrame = pd.DataFrame()

    def load(_self) -> 'TransitionList':
        LOGGER.debug(f"Loading transition file {_self.in_file}")
        _, file_extension = os.path.splitext(_self.in_file)
        if file_extension.lower() == '.tsv':
            loader = TransitionTSVLoader(_self.in_file)
        elif file_extension.lower() == '.pqp':
            loader = TransitionPQPLoader(_self.in_file)
        else:
            raise ValueError("Unsupported file format")

        _self.data = loader._load()

    def save(self, file_path: str) -> None:
        self.data.to_csv(file_path, sep='\t', index=False)

    def filter_by_protein(self, protein_id) -> pd.DataFrame:
        return self.data[self.data['ProteinId'] == protein_id]

    def filter_by_charge(self, charge: int) -> pd.DataFrame:
        return self.data[self.data['PrecursorCharge'] == charge]

    def filter_by_peptide_sequence(self, peptide_sequence: str) -> pd.DataFrame:
        return self.data[self.data['ModifiedPeptideSequence'] == peptide_sequence]

    def get_unique_genes(self) -> List[str]:
        return self.data['GeneName'].unique()

    def get_unique_proteins(self) -> List[str]:
        return self.data['ProteinId'].unique()

    def get_unique_peptide_sequences(self) -> List[str]:
        return self.data['ModifiedPeptideSequence'].unique()

    def get_unique_charge_states(self) -> List[int]:
        return self.data['PrecursorCharge'].unique()

    def get_unique_peptides_per_protein(self, protein) -> List[str]:
        return self.data[self.data['ProteinId'] == protein]['ModifiedPeptideSequence'].unique()

    def get_unique_charge_states_per_peptide(self, peptide) -> List[int]:
        return self.data[self.data['ModifiedPeptideSequence'] == peptide]['PrecursorCharge'].unique()

    def get_peptide_precursor_mz(self, peptide: str, charge: int) -> float:
        return self.data[(self.data['ModifiedPeptideSequence'] == peptide) & (self.data['PrecursorCharge'] == charge)]['PrecursorMz'].iloc[0]
    
    def get_peptide_product_mz_list(self, peptide: str, charge: int) -> List[float]:
        return self.data[(self.data['ModifiedPeptideSequence'] == peptide) & (self.data['PrecursorCharge'] == charge)]['ProductMz'].tolist()
        
    def get_peptide_product_charge_list(self, peptide: str, charge: int) -> List[int]:
        return self.data[(self.data['ModifiedPeptideSequence'] == peptide) & (self.data['PrecursorCharge'] == charge)]['ProductCharge'].tolist()
    
    def get_peptide_retention_time(self, peptide: str, charge: int) -> float:
        return self.data[(self.data['ModifiedPeptideSequence'] == peptide) & (self.data['PrecursorCharge'] == charge)]['NormalizedRetentionTime'].iloc[0] 
    
    def get_peptide_ion_mobility(self, peptide: str, charge: int) -> float:
        return self.data[(self.data['ModifiedPeptideSequence'] == peptide) & (self.data['PrecursorCharge'] == charge)]['PrecursorIonMobility'].iloc[0]

    def get_peptide_library_intensity(self, peptide: str, charge: int) -> float:
        return self.data[(self.data['ModifiedPeptideSequence'] == peptide) & (self.data['PrecursorCharge'] == charge)]['LibraryIntensity'].iloc[0]

    def get_peptide_fragment_annotation_list(self, peptide: str, charge: int) -> List[str]:
        return self.data[(self.data['ModifiedPeptideSequence'] == peptide) & (self.data['PrecursorCharge'] == charge)]['Annotation'].tolist()
    
    def filter_for_target_transition_list(self, protein:str, peptide: str, charge: int) -> pd.DataFrame:
        return self.data[( self.data['ProteinId'] == protein) & (self.data['ModifiedPeptideSequence'] == peptide) & (self.data['PrecursorCharge'] == charge)]