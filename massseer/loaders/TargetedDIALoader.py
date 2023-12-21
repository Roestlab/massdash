from typing import List, Dict, Optional, Literal
import pandas as pd
import numpy as np  

# Structs
from massseer.structs.TransitionGroup import TransitionGroup
from massseer.structs.TransitionGroupFeature import TransitionGroupFeature
from massseer.structs.FeatureMap import FeatureMap
# Loaders
from massseer.loaders.mzMLDataAccess import mzMLDataAccess
from massseer.loaders.access.TargetedDIADataAccess import TargetedDIAConfig, TargetedDIADataAccess

class TargetedDIALoader:
    ''' 
    Class for loading Chromatograms and peak features
    Classes which inherit from this should contain one results file and one transition file
    
    Attributes:
        mzmlFiles (List[str]): A list of mzML files.
        rsltsFile (Optional[str]): The results file.
        config (TargetedDIAConfig): The configuration for reducing the spectra.
        mzml_data_container (Dict): A dictionary containing the mzML data.
        mzml_targeted_exp (Dict): A dictionary containing the mzML targeted experiment data.
        mzml_reduced_dfs (Dict): A dictionary containing the mzML reduced dataframes.
        
    Methods:
        load_mzml_data: Loads mzML data from the specified mzmlFiles into a dictionary.
        targeted_diapasef_data_access: Accesses targeted DIA data from mzML files and stores them in a dictionary.
        reduce_targeted_spectra: Reduce the spectra for a given peptide in the targeted experiment.
        find_closest_reference_mz: Find the closest reference m/z value in the given list to provided m/z values.
        apply_mz_mapping: Apply mz mapping to the given row based on the ms_level.
        get_targeted_dataframe: Generate a targeted dataframe based on the given parameters.
        loadTransitionGroups: Loads transition groups from the given targeted transition list.
    '''

    def __init__(self, mzmlFiles: List[str], rsltsFile: Optional[str]=None,  config: TargetedDIAConfig=TargetedDIAConfig(), verbose: bool=False) -> None:
        self.mzmlFiles = mzmlFiles
        self.rsltsFile = rsltsFile
        self.mzml_data_container = {}
        self.mzml_targeted_exp = {}
        self.mzml_reduced_dfs = {}
        self.verbose = verbose

        # Configuration
        self.config = config

    def load_mzml_data(self) -> None:
        """
        Loads mzML data from the specified mzmlFiles into a dictionary.

        Returns:
            None
        """
        mzml_data_container = {}
        for mzmlFile in self.mzmlFiles:
            mzml_io = mzMLDataAccess(mzmlFile, 'ondisk', self.verbose)
            mzml_io.load_data()
            mzml_data_container[mzmlFile] = mzml_io
        self.mzml_data_container = mzml_data_container

    def targeted_diapasef_data_access(self) -> None:
        """
        Accesses targeted DIA data from mzML files and stores them in a dictionary.

        This method iterates over the mzML data container and creates a TargetedDIADataAccess object for each mzML file.
        The TargetedDIADataAccess object is then stored in a dictionary with the file name as the key.

        Returns:
            None
        """
        mzml_targeted_exp = {}
        for file, mzml_data in self.mzml_data_container.items():
            exp = TargetedDIADataAccess(mzml_data, self.config, 'ondisk', self.verbose)
            mzml_targeted_exp[file] = exp
        self.mzml_targeted_exp = mzml_targeted_exp

    def reduce_targeted_spectra(self, peptide: Dict, config: TargetedDIAConfig) -> None:
        """
        Reduce the spectra for a given peptide in the targeted experiment.

        Args:
            peptide (Dict): A dictionary containing peptide information for each file.
            config (TargetedDIAConfig): The configuration for reducing the spectra.

        Returns:
            None
        """
        for file, exp in self.mzml_targeted_exp.items():
            exp.reduce_spectra(peptide[file], config)

    def find_closest_reference_mz(self, given_mz: np.array, reference_mz_values: np.array) -> np.array:
        """
        Find the closest reference m/z value in the given list to provided m/z values.

        Args:
            given_mz (np.array): An array of m/z values for which to find the closest reference m/z values.
            reference_mz_values (np.array): An array of reference m/z values to compare against.

        Returns:
            np.array: An array of the closest reference m/z values from the provided list.
        """
        closest_mz = reference_mz_values[np.argmin(np.abs(reference_mz_values - given_mz[:, None]), axis=1)]
        return closest_mz

    def apply_mz_mapping(self, row: pd.DataFrame, peptide_product_mz_list: List) -> Literal["float", "np.nan"]:
        """
        Apply mz mapping to the given row based on the ms_level.

        Args:
            row (pd.DataFrame): The row containing the data.
            peptide_product_mz_list (List): The list of peptide product m/z values.

        Returns:
            Union[float, np.nan]: The mapped m/z value.
        """
        if row['ms_level'] == 2:
            return self.find_closest_reference_mz(np.array([row['mz']]), np.array(peptide_product_mz_list))[0]
        elif row['ms_level'] == 1:
            return row['precursor_mz']
        else:
            return np.nan

    def get_targeted_dataframe(self, mslevels: List, peptide_product_mz_list: List, target_transition_list: pd.DataFrame) -> Dict:
            """
            Generate a targeted dataframe based on the given parameters.

            Args:
                mslevels (List): A list of MS levels to filter the dataframe.
                peptide_product_mz_list (List): A list of peptide product m/z values.
                target_transition_list (pd.DataFrame): A dataframe containing target transition information.

            Returns:
                Dict: A dictionary containing the generated targeted dataframes for each file.
            """
            mzml_reduced_dfs = {}
            for file, exp in self.mzml_targeted_exp.items():
                df = exp.get_df(mslevels)
                if df.shape[0] > 0:
                    df['product_mz'] = df.apply(self.apply_mz_mapping, args=(peptide_product_mz_list,) , axis=1)
                    # Merge df with target_transition_list on df.product_mz and target_transition_list.ProductMz
                    df = pd.merge(df, target_transition_list, left_on='product_mz', right_on='ProductMz', how='left')
                    # Fill in missing PrecursorCharge values to the single unique value in PrecursorCharge column that is not None
                    df['PrecursorCharge'] = df['PrecursorCharge'].fillna(df['PrecursorCharge'].unique()[0])
                    # Fill in missing PeptideSequence values to the single unique value in PeptideSequence column that is not None
                    df['PeptideSequence'] = df['PeptideSequence'].fillna(df['PeptideSequence'].unique()[0])
                    # Fill in missing ModifiedPeptideSequence values to the single unique value in ModifiedPeptideSequence column that is not None
                    df['ModifiedPeptideSequence'] = df['ModifiedPeptideSequence'].fillna(df['ModifiedPeptideSequence'].unique()[0])
                    # Fill in missing ProteinId values to the single unique value in ProteinId column that is not None
                    df['ProteinId'] = df['ProteinId'].fillna(df['ProteinId'].unique()[0])
                    # Fill in missing GeneName values to the single unique value in GeneName column that is not None
                    df['GeneName'] = df['GeneName'].fillna(df['GeneName'].unique()[0])
                    # Fill in missing NormalizedRetentionTime values to the single unique value in NormalizedRetentionTime column that is not None
                    df['NormalizedRetentionTime'] = df['NormalizedRetentionTime'].fillna(df['NormalizedRetentionTime'].unique()[0])
                    # Fill in missing PrecursorIonMobility values to the single unique value in PrecursorIonMobility column that is not None
                    df['PrecursorIonMobility'] = df['PrecursorIonMobility'].fillna(df['PrecursorIonMobility'].unique()[0])
                    # Fill in missing Annotation values in column Annotation where rows ms_level == 1 and Annotation is None, fill in with 'Precursor_i0'
                    df.loc[(df['ms_level'] == 1) & (df['Annotation'].isnull()), 'Annotation'] = 'Precursor_i0'
                    # Drop columns 'PrecursorMz', 'ProductMz' from df in place
                    df.drop(columns=['PrecursorMz', 'ProductMz'], axis=1, inplace=True)
                    # Sort df by native_id, ms_level, precursor_mz, product_mz in place
                    df.sort_values(by=['native_id', 'ms_level', 'precursor_mz', 'product_mz'], inplace=True)
                mzml_reduced_dfs[exp] = df
            self.mzml_reduced_dfs = mzml_reduced_dfs
            return mzml_reduced_dfs

    def loadTransitionGroups(self, targeted_transition_list: pd.DataFrame) -> TransitionGroup:
            """
            Loads transition groups from the given targeted transition list.

            Args:
                targeted_transition_list (pd.DataFrame): The targeted transition list.

            Returns:
                dict: A dictionary containing the loaded transition groups, where the keys are file names and the values are TransitionGroup objects.
            """
            out = {}
            for file, mzml_df in self.mzml_reduced_dfs.items():
                transition_group = TransitionGroup.from_feature_map(FeatureMap(mzml_df, self.verbose), targeted_transition_list)
                out[file] = transition_group
            return out