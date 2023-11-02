from typing import List
import os
import pandas as pd
import streamlit as st

class TransitionList:
    REQUIRED_TSV_COLUMNS: List[str] = ['PrecursorMz', 'ProductMz', 'PrecursorCharge', 'ProductCharge',
                                   'LibraryIntensity', 'NormalizedRetentionTime', 'PeptideSequence',
                                   'ModifiedPeptideSequence', 'ProteinId', 'GeneName', 'FragmentType',
                                   'FragmentSeriesNumber', 'Annotation', 'PrecursorIonMobility']

    def __init__(self) -> None:
        self.data: pd.DataFrame = pd.DataFrame()

    @staticmethod
    def from_tsv(file_path: str) -> 'TransitionList':
        transition_list: 'TransitionList' = TransitionList()
        transition_list.data = pd.read_csv(file_path, sep='\t')
        if transition_list._validate_columns():
            return transition_list
        else:
            raise ValueError(f"The TSV file does not have the required columns.\n {TransitionList.REQUIRED_TSV_COLUMNS}")

    @staticmethod
    def from_pqp(file_path: str) -> 'TransitionList':
        # TODO: Implement the logic to load data from a PQP file
        # Probably implement a class in SqlDataAccess
        pass

    @staticmethod
    @st.cache_data()
    def from_file(file_path: str) -> 'TransitionList':
        _, file_extension = os.path.splitext(file_path)
        if file_extension.lower() == '.tsv':
            return TransitionList.from_tsv(file_path)
        elif file_extension.lower() == '.pqp':
            return TransitionList.from_pqp(file_path)
        else:
            raise ValueError("Unsupported file format")

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

    def get_peptide_fragment_annotation_list(self, peptide: str, charge: int) -> List[str]:
        return self.data[(self.data['ModifiedPeptideSequence'] == peptide) & (self.data['PrecursorCharge'] == charge)]['Annotation'].tolist()
    

    def _validate_columns(self) -> bool:
        return all(col in self.data.columns for col in self.REQUIRED_TSV_COLUMNS)