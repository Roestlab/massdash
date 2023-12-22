from typing import List, Tuple

# Data modules
import pandas as pd
import numpy as np

# Structs
from massseer.structs.Chromatogram import Chromatogram
from massseer.structs.Mobilogram import Mobilogram
from massseer.structs.Spectrum import Spectrum
# Utils
from massseer.util import LOGGER
from massseer.structs.TransitionGroup import TransitionGroup
from massseer.structs.TargetedDIAConfig import TargetedDIAConfig

class FeatureMap:
    '''
    Class for storing a feature map a feature map only contains the following columns:
    - mz: mass to charge ratio
    - rt: retention time
    - im: ion mobility
    - int: intensity
    - ms_level: 1 for precursor, 2 for fragment
    - annotation: annotation of precursor/fragment
    
    Attributes:
        feature_df (pd.DataFrame): A DataFrame containing the feature map
        has_im (bool): A boolean indicating if the feature map has ion mobility data
        
    Methods:
        empty: Check if the FeatureMap is empty.
        average_intensity_across_two_dimensions: Compute the average intensity across two dimensions of a DataFrame.
        get_precursor_chromatograms: Get a list of precursor chromatograms from the feature map.
        get_transition_chromatograms: Get a list of transition chromatograms from the feature map.
        get_precursor_mobilograms: Get a list of precursor ion mobility from the feature map.
        get_transition_mobilograms: Get a list of transition ion mobility from the feature map.
        get_precursor_spectra: Get a list of precursor spectra from the feature map.
        get_transition_spectra: Get a list of transition spectra from the feature map.
    '''
    def __init__(self, feature_df: pd.DataFrame, config: TargetedDIAConfig=None, verbose: bool=False):
        self.feature_df = feature_df
        self.has_im = 'im' in feature_df.columns and feature_df['im'].notnull().all()
        self.config = config
        
        LOGGER.name = 'FeatureMap'
        if verbose:
            LOGGER.setLevel('DEBUG')
        else:
            LOGGER.setLevel('INFO')

    def empty(self) -> bool:
        """
        Check if the FeatureMap is empty.

        Returns:
            bool: True if the feature_df is empty, False otherwise.
        """
        return self.feature_df.empty

    @staticmethod
    def average_intensity_across_two_dimensions(df: pd.DataFrame, index: str='im', columns: str='rt', values: str='int', axis: int=0) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute the average intensity across two dimensions of a DataFrame.

        Args:
            df (pd.DataFrame): The input DataFrame.
            index (str): The name of the index column. Default is 'im'.
            columns (str): The name of the columns. Default is 'rt'.
            values (str): The name of the values. Default is 'int'.
            axis (int): The axis to compute the average intensity across. Must be 0 or 1. Default is 0.

        Returns:
            Tuple of two numpy arrays: The x-axis values and the average intensity values.
        """
        matrix = df.pivot_table(index=index, columns=columns, values=values)

        if axis == 0:
            x_arr = matrix.columns.to_numpy()
        elif axis == 1:
            x_arr = matrix.index.to_numpy()
        else:
            raise ValueError(f'axis must be 0 or 1, not {axis}')

        matrix = matrix.to_numpy()
        # Set cells in 2D matrix with nan values to 0
        matrix[np.isnan(matrix)] = 0
        int_arr = np.mean(matrix, axis=axis)

        return x_arr, int_arr

    def to_chromatograms(self) -> TransitionGroup:
        '''
        Convert the feature map to a TransitionGroup object storing chromatograms

        Returns:
            TransitionGroup: A TransitionGroup object storing chromatograms
        '''
        return TransitionGroup(self.get_precursor_chromatograms(), self.get_transition_chromatograms())
    
    def to_mobilograms(self) -> TransitionGroup:
        '''
        Convert the feature map to a TransitionGroup object storing mobilograms
        
        Returns:
            TransitionGroup: A TransitionGroup object storing mobilograms
        '''
        return TransitionGroup(self.get_precursor_mobilograms(), self.get_transition_mobilograms())
    
    def to_spectra(self) -> TransitionGroup:
        '''
        Convert the feature map to a TransitionGroup object storing spectra
        
        Returns:
            TransitionGroup: A TransitionGroup object storing spectra
        '''
        return TransitionGroup(self.get_precursor_spectra(), self.get_transition_spectra())

    def get_precursor_chromatograms(self) -> List[Chromatogram]:
        '''
        Get a list of precursor chromatograms from the feature map
        '''
        if self.feature_df.shape[0] == 0:
            return [Chromatogram(np.array([]), np.array([]), 'No precursor chromatograms found')]
        # Filter the feature map to only precursor chromatograms
        precursor_df = self.feature_df[self.feature_df['ms_level']==1]
        if precursor_df.shape[0] == 0:
            return [Chromatogram(np.array([]), np.array([]), 'No precursor chromatograms found')]
        # If ion mobility data is present, compute mean of intensities across ion mobility for retention time
        if self.has_im:
            rt_arr, int_arr = FeatureMap.average_intensity_across_two_dimensions(precursor_df)
        else:
            rt_arr = precursor_df['rt'].to_numpy()
            int_arr = precursor_df['int'].to_numpy()
        
        precursor_chromatogram = Chromatogram(rt_arr, int_arr, f'{pd.unique(precursor_df["Annotation"].values)[0]}')
        return [precursor_chromatogram]

    def get_transition_chromatograms(self) -> List[Chromatogram]:
        '''
        Get a list of transition chromatograms from the feature map
        '''
        if self.feature_df.shape[0] == 0:
            return [Chromatogram(np.array([]), np.array([]), 'No transition chromatograms found')]

        # Filter the feature map to only transition chromatograms
        transition_df = self.feature_df[self.feature_df['ms_level']==2]
        transition_chromatograms = []
        for transition in pd.unique(transition_df['product_mz']):
            transition_df_tmp = transition_df[transition_df['product_mz']==transition]

            # If ion mobility data is present, compute mean of intensities across ion mobility for retention time
            if self.has_im  and transition_df_tmp.shape[0] > 1:
                rt_arr, int_arr = FeatureMap.average_intensity_across_two_dimensions(transition_df_tmp)
            else:
                rt_arr = transition_df_tmp['rt'].to_numpy()
                int_arr = transition_df_tmp['int'].to_numpy()

            transition_chromatogram = Chromatogram(rt_arr, int_arr, f'{pd.unique(transition_df_tmp["Annotation"].values)[0]}')
            transition_chromatograms.append(transition_chromatogram)
        return transition_chromatograms

    def get_precursor_mobilograms(self) -> List[Mobilogram]:
        '''
        Get a list of precursor ion mobility from the feature map
        '''
        if self.feature_df.shape[0] == 0:
            return [Mobilogram(np.array([]), np.array([]), 'No precursor ion mobility found')]
        # Filter the feature map to only precursor ion mobility
        precursor_df = self.feature_df[self.feature_df['ms_level']==1]
        
        if precursor_df.shape[0] == 0:
            return [Mobilogram(np.array([]), np.array([]), 'No precursor ion mobility found')]
        # If ion mobility data is present, compute mean of intensities across retention time for ion mobility
        if 'rt' in precursor_df.columns:
            im_arr, int_arr = FeatureMap.average_intensity_across_two_dimensions(precursor_df, axis=1)
        else:
            im_arr = precursor_df['im'].to_numpy()
            int_arr = precursor_df['int'].to_numpy()
        precursor_ion_mobility = Mobilogram(im_arr, int_arr, f'{pd.unique(precursor_df["Annotation"].values)[0]}')
        return [precursor_ion_mobility]

    def get_transition_mobilograms(self) -> List[Mobilogram]:
        '''
        Get a list of transition ion mobility from the feature map
        '''
        if self.feature_df.shape[0] == 0:
            return [Mobilogram(np.array([]), np.array([]), 'No transition ion mobility found')]
        # Filter the feature map to only transition ion mobility
        transition_df = self.feature_df[self.feature_df['ms_level']==2]
        if transition_df.shape[0] == 0:
            return [Mobilogram(np.array([]), np.array([]), 'No transition ion mobility found')]
        transition_ion_mobilities = []
        for transition in pd.unique(transition_df['product_mz']):
            transition_df_tmp = transition_df[transition_df['product_mz']==transition]

            # If ion mobility data is present, compute mean of intensities across retention time for ion mobility
            if self.has_im and transition_df_tmp.shape[0] > 1:
                im_arr, int_arr = FeatureMap.average_intensity_across_two_dimensions(transition_df_tmp, axis=1)
            else:
                im_arr = transition_df_tmp['im'].to_numpy()
                int_arr = transition_df_tmp['int'].to_numpy()
            transition_ion_mobility = Mobilogram(im_arr, int_arr, f'{pd.unique(transition_df_tmp["Annotation"].values)[0]}')
            transition_ion_mobilities.append(transition_ion_mobility)
        return transition_ion_mobilities

    def get_precursor_spectra(self) -> List[Spectrum]:
        '''
        Get a list of precursor spectra from the feature map
        '''
        if self.feature_df.shape[0] == 0:
            return [Spectrum(np.array([]), np.array([]), 'No precursor spectra found')]
        # Filter the feature map to only precursor spectra
        precursor_df = self.feature_df[self.feature_df['ms_level']==1]
        precursor_spectra = []
        for precursor in pd.unique(precursor_df['precursor_mz']):
            precursor_df_tmp = precursor_df[precursor_df['precursor_mz']==precursor]
            precursor_spectrum = Spectrum(precursor_df_tmp['mz'].to_numpy(), precursor_df_tmp['int'].to_numpy(), f'{pd.unique(precursor_df_tmp["Annotation"].values)[0]}')
            precursor_spectra.append(precursor_spectrum)
        return precursor_spectra

    def get_transition_spectra(self) -> List[Spectrum]:
        '''
        Get a list of transition spectra from the feature map
        '''
        if self.feature_df.shape[0] == 0:
            return [Spectrum(np.array([]), np.array([]), 'No transition spectra found')]
        # Filter the feature map to only transition spectra
        transition_df = self.feature_df[self.feature_df['ms_level']==2]
        transition_spectra = []
        for transition in pd.unique(transition_df['product_mz']):
            transition_df_tmp = transition_df[transition_df['product_mz']==transition]
            transition_spectrum = Spectrum(transition_df_tmp['mz'].to_numpy(), transition_df_tmp['int'].to_numpy(), f'{pd.unique(transition_df_tmp["Annotation"].values)[0]}')
            transition_spectra.append(transition_spectrum)
        return transition_spectra