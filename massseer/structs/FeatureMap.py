from massseer.structs.Chromatogram import Chromatogram
from massseer.structs.Mobilogram import Mobilogram
from massseer.structs.Spectrum import Spectrum
from typing import List
import pandas as pd
import numpy as np

class FeatureMap:
    '''
    Class for storing a feature map
    '''
    def __init__(self, feature_df: pd.DataFrame):
        self.feature_df = feature_df
        self.has_im = 'im' in feature_df.columns

    @staticmethod
    def average_intensity_across_two_dimensions(df: pd.DataFrame, index: str='im', columns: str='rt', values: str='int', axis: int=0):
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


    def get_precursor_chromatograms(self) -> List[Chromatogram]:
        '''
        Get a list of precursor chromatograms from the feature map
        '''
        # Filter the feature map to only precursor chromatograms
        precursor_df = self.feature_df[self.feature_df['ms_level']==1]
        # If ion mobility data is present, compute mean of intensities across ion mobility for retention time
        if 'im' in precursor_df.columns:
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
        # Filter the feature map to only transition chromatograms
        transition_df = self.feature_df[self.feature_df['ms_level']==2]
        transition_chromatograms = []
        for transition in pd.unique(transition_df['product_mz']):
            transition_df_tmp = transition_df[transition_df['product_mz']==transition]

            # If ion mobility data is present, compute mean of intensities across ion mobility for retention time
            if 'im' in transition_df_tmp.columns and transition_df_tmp.shape[0] > 1:
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
        # Filter the feature map to only precursor ion mobility
        precursor_df = self.feature_df[self.feature_df['ms_level']==1]
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
        # Filter the feature map to only transition ion mobility
        transition_df = self.feature_df[self.feature_df['ms_level']==2]
        transition_ion_mobilities = []
        for transition in pd.unique(transition_df['product_mz']):
            transition_df_tmp = transition_df[transition_df['product_mz']==transition]

            # If ion mobility data is present, compute mean of intensities across retention time for ion mobility
            if 'im' in transition_df_tmp.columns  and transition_df_tmp.shape[0] > 1:
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
        # Filter the feature map to only transition spectra
        transition_df = self.feature_df[self.feature_df['ms_level']==2]
        transition_spectra = []
        for transition in pd.unique(transition_df['product_mz']):
            transition_df_tmp = transition_df[transition_df['product_mz']==transition]
            transition_spectrum = Spectrum(transition_df_tmp['mz'].to_numpy(), transition_df_tmp['int'].to_numpy(), f'{pd.unique(transition_df_tmp["Annotation"].values)[0]}')
            transition_spectra.append(transition_spectrum)
        return transition_spectra