"""
massdash/loaders/SpectralLibraryLoader
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import os
from typing import List
import pandas as pd

# Loaders
from .access.TransitionTSVDataAccess import TransitionTSVDataAccess
from .access.TransitionPQPDataAccess import TransitionPQPDataAccess
# Structs
from ..structs.TransitionGroupFeature import TransitionGroupFeature
# Utils
from ..util import LOGGER

class SpectralLibraryLoader:
    """
    Class for loading spectral library files.
    
    Attributes:
        in_file (str): The path to the spectral library file.
        data (pd.DataFrame): The spectral library data.
        
    Methods:
        load: Loads the spectral library file.
        save: Saves the spectral library data to a file.
        get_unique_proteins: Retrieves a list of unique protein IDs from the spectral library.
        get_unique_peptides_per_protein: Retrieves a list of unique peptide sequences for a given protein.
        get_unique_charge_states_per_peptide: Retrieves a list of unique charge states for a given peptide.
        get_peptide_precursor_mz: Retrieves the precursor m/z value for a given peptide and charge.
        get_peptide_product_mz_list: Retrieves a list of product m/z values for a given peptide and charge.
        get_peptide_product_charge_list: Retrieves a list of product charges for a given peptide and charge.
        get_peptide_retention_time: Retrieves the retention time for a given peptide and charge.
        get_peptide_ion_mobility: Retrieves the ion mobility of a peptide with a specific charge from the spectral library.
        get_peptide_library_intensity: Retrieves the library intensity for a specific peptide and charge.
        get_peptide_fragment_annotation_list: Retrieves a list of fragment annotations for a given peptide and charge.
        filter_for_target_transition_list: Filters the data for a specific target transition list based on the given protein, peptide, and charge.
    """
    def __init__(self, in_file: str, verbose: bool=False) -> None:
        self.in_file = in_file
        self.data: pd.DataFrame = self.load()
        self.has_im = 'PrecursorIonMobility' in self.data.columns and self.data['PrecursorIonMobility'].notnull().any()
        
        LOGGER.name = "SpectralLibraryLoader"
        if verbose:
            LOGGER.setLevel("DEBUG")
        else:
            LOGGER.setLevel("INFO")

    def load(self) -> pd.DataFrame:
        """
        Load the transition list file
        """
        LOGGER.debug(f"Loading transition file {self.in_file}")
        _, file_extension = os.path.splitext(self.in_file)
        if file_extension.lower() == '.tsv':
            return TransitionTSVDataAccess(self.in_file).load()
        elif file_extension.lower() == '.pqp' or file_extension.lower() == '.osw':
            return TransitionPQPDataAccess(self.in_file).load()
        else:
            raise ValueError("Unsupported file format")

    def save(self, file_path: str) -> None:
        """
        Save the data to a file.

        Args:
            file_path (str): The path to the file where the data will be saved.

        Returns:
            None
        """
        self.data.to_csv(file_path, sep='\t', index=False)

    def get_unique_proteins(self) -> List[str]:
        """
        Returns a list of unique protein IDs from the data.

        Returns:
            List[str]: A list of unique protein IDs.
        """
        return self.data['ProteinId'].unique()

    def get_unique_peptides_per_protein(self, protein: str) -> List[str]:
        """
        Returns a list of unique peptide sequences for a given protein.

        Args:
            protein (str): The protein ID.

        Returns:
            List[str]: A list of unique peptide sequences.
        """
        return self.data[self.data['ProteinId'] == protein]['ModifiedPeptideSequence'].unique()

    def get_unique_charge_states_per_peptide(self, peptide: str) -> List[int]:
        """
        Returns a list of unique charge states for a given peptide.

        Args:
            peptide (str): The peptide sequence.

        Returns:
            List[int]: A list of unique charge states associated with the peptide.
        """
        return self.data[self.data['ModifiedPeptideSequence'] == peptide]['PrecursorCharge'].unique()

    def get_peptide_precursor_mz(self, peptide: str, charge: int) -> float:
        """
        Get the precursor m/z value for a given peptide and charge.

        Parameters:
        peptide (str): The modified peptide sequence.
        charge (int): The precursor charge.

        Returns:
        float: The precursor m/z value.
        """
        return self.data[(self.data['ModifiedPeptideSequence'] == peptide) & (self.data['PrecursorCharge'] == charge)]['PrecursorMz'].iloc[0]
    
    def get_peptide_product_mz_list(self, peptide: str, charge: int) -> List[float]:
        """
        Retrieve a list of product m/z values for a given peptide and charge.

        Args:
            peptide (str): The modified peptide sequence.
            charge (int): The precursor charge.

        Returns:
            List[float]: A list of product m/z values.

        """
        return self.data[(self.data['ModifiedPeptideSequence'] == peptide) & (self.data['PrecursorCharge'] == charge)]['ProductMz'].tolist()
    
    # TODO not used remove?
    def populateTransitionGroupFeature(self, transition_group_feature: TransitionGroupFeature) -> TransitionGroupFeature:
        """
        Appends library information to a TransitionGroupFeature object

        Args:
            transition_group_feature (TransitionGroupFeature): The TransitionGroupFeature object to append library information to.

        Returns:
            TransitionGroupFeature: The TransitionGroupFeature object with appended library information.
        """
        library_data = self.data[(self.data['ModifiedPeptideSequence'] == transition_group_feature.sequence) & (self.data['PrecursorCharge'] == transition_group_feature.precursor_charge)]

        if library_data.empty:
            LOGGER.warning(f"No library data found for {transition_group_feature.sequence} {transition_group_feature.precursor_charge}")
            return transition_group_feature
        transition_group_feature.product_annotations = library_data['Annotation'].tolist()
        transition_group_feature.product_mz = library_data['ProductMz'].tolist()
        transition_group_feature.precursor_mz = library_data['PrecursorMz'].iloc[0]
        return transition_group_feature
    
    def populateTransitionGroupFeatures(self, transition_group_features: List[TransitionGroupFeature]) -> List[TransitionGroupFeature]:
        """
        Populates library information for a list of TransitionGroupFeature objects.
        ***Important:*** Assumes that all TransitionGroupFeature objects have the same peptide sequence and precursor charge.
        """
        peptide_sequence = transition_group_features[0].sequence
        precursor_charge = transition_group_features[0].precursor_charge
        library_data = self.data[(self.data['ModifiedPeptideSequence'] == peptide_sequence) & (self.data['PrecursorCharge'] == precursor_charge)]

        for t in transition_group_features:
            t.product_annotations = library_data['Annotation'].tolist()
            t.product_mz = library_data['ProductMz'].tolist()
            t.precursor_mz = library_data['PrecursorMz'].iloc[0]

    def get_peptide_product_charge_list(self, peptide: str, charge: int) -> List[int]:
        """
        Retrieve a list of product charges for a given peptide and charge.

        Args:
            peptide (str): The modified peptide sequence.
            charge (int): The precursor charge.

        Returns:
            List[int]: A list of product charges.

        """
        return self.data[(self.data['ModifiedPeptideSequence'] == peptide) & (self.data['PrecursorCharge'] == charge)]['ProductCharge'].tolist()
    
    def get_peptide_retention_time(self, peptide: str, charge: int) -> float:
        """
        Get the retention time for a given peptide and charge.

        Parameters:
        peptide (str): The modified peptide sequence.
        charge (int): The precursor charge.

        Returns:
        float: The normalized retention time.
        """
        return self.data[(self.data['ModifiedPeptideSequence'] == peptide) & (self.data['PrecursorCharge'] == charge)]['NormalizedRetentionTime'].iloc[0]
    
    def get_peptide_ion_mobility(self, peptide: str, charge: int) -> float:
        """
        Retrieves the ion mobility of a peptide with a specific charge from the spectral library.

        Parameters:
        peptide (str): The modified peptide sequence.
        charge (int): The precursor charge.

        Returns:
        float: The precursor ion mobility.
        """
        return self.data[(self.data['ModifiedPeptideSequence'] == peptide) & (self.data['PrecursorCharge'] == charge)]['PrecursorIonMobility'].iloc[0]

    def get_peptide_library_intensity(self, peptide: str, charge: int) -> float:
        """
        Get the library intensity for a specific peptide and charge.

        Parameters:
            peptide (str): The modified peptide sequence.
            charge (int): The precursor charge.

        Returns:
            float: The library intensity for the specified peptide and charge.
        """
        return self.data[(self.data['ModifiedPeptideSequence'] == peptide) & (self.data['PrecursorCharge'] == charge)]['LibraryIntensity'].iloc[0]

    def get_peptide_fragment_annotation_list(self, peptide: str, charge: int) -> List[str]:
        """
        Retrieves a list of fragment annotations for a given peptide and charge.

        Args:
            peptide (str): The peptide sequence.
            charge (int): The precursor charge.

        Returns:
            List[str]: A list of fragment annotations.
        """
        return self.data[(self.data['ModifiedPeptideSequence'] == peptide) & (self.data['PrecursorCharge'] == charge)]['Annotation'].tolist()
    
    def filter_for_target_transition_list(self, protein: str, peptide: str, charge: int) -> pd.DataFrame:
        """
        Filters the data for a specific target transition list based on the given protein, peptide, and charge.

        Args:
            protein (str): The protein ID.
            peptide (str): The modified peptide sequence.
            charge (int): The precursor charge.

        Returns:
            pd.DataFrame: The filtered data containing the target transition list.
        """
        return self.data[(self.data['ProteinId'] == protein) & (self.data['ModifiedPeptideSequence'] == peptide) & (self.data['PrecursorCharge'] == charge)]
