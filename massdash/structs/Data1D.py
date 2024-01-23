"""
massdash/structs/Data1D
~~~~~~~~~~~~~~~~~~~~~~~
"""

from abc import ABC, abstractmethod
from typing import Optional, Tuple
import numpy as np
import pandas as pd

class Data1D(ABC):
    ''' 
    Abstract class of storing a 1D data set where have the data vs intensity
    '''

    def __init__(self, data: np.array, intensity: np.array, label: str='None') -> None:
        self.intensity = np.array(intensity)
        self.data = np.array(data)
        self.label = label

    def __str__(self):
        return f"{'-'*8} {self.__class__.__name__} {'-'*8}\nlabel: {self.label}\nlength of {self.__class__.__name__}: {len(self.data)}"

    #def __repr__(self):
    #    return f"{self.__class__.__name__} object with label {self.label} and {len(self.data)} data points"
    
    def empty(self) -> bool:
        """
        Check if the Chromatogram is empty.

        Returns:
            bool: True if both rt and intensity are empty, False otherwise.
        """
        return not (self.data.any() and self.intensity.any())
 
    def max(self, boundary: Optional[Tuple[float,float]] = None) -> (float, float):
        """
        Calculate the highest intensity within a given boundary.

        Args:
            boundary (tuple): A tuple containing the left and right boundaries.

        Returns:
            float: The highest intensity within the given boundary.
        """
        if boundary is not None:
            return self.filter(boundary).max()
        else:
            idx_max = np.argmax(self.intensity)
            return (self.data[idx_max], self.intensity[idx_max])
        
    def filter(self, boundary: Tuple[float, float]) -> 'cls':
        """
        Filter the 1D object to only include data points within a given boundary.

        Args:
            boundary (tuple): A tuple containing the left and right boundaries of the region of interest. The unit is either m/z, IM or RT depending on underlying object

        Returns:
            Data1D instance: A Data1D child (Chromatogram, Mobilogram, Spectrum) copy with filtered intensity values.
        """
        if isinstance(boundary, tuple):
            newData = self.__class__(self.data.copy(), self.intensity.copy(), self.label)
            left, right = boundary
            mask = (newData.data >= left) & (newData.data <= right)
            newData.data = newData.data[mask]
            newData.intensity = newData.intensity[mask]
            return newData
        else:
            raise ValueError("Boundary must be a tuple.")   

    def sum(self, boundary: Optional[Tuple[float,float]] = None) -> float:
        """
        Calculates the integrated intensity of a chromatogram within a given boundary.

        Args:
            boundary (tuple): A tuple containing the left and right boundaries of the integration range.

        Returns:
            float: The integrated intensity of the chromatogram within the given boundary.
        """
        if boundary is not None:
            return self.filter(boundary).sum()
        else:
            return np.sum(self.intensity)

    def median(self, boundary: Optional[Tuple[float, float]] = None) -> float:
        """
        Calculate the median intensity of a given boundary in the chromatogram data.

        Args:
            chrom_data (list): A list of tuples containing the retention time and intensity values of a chromatogram.
            boundary (tuple): A tuple containing the left and right boundaries of the region of interest.

        Returns:
            float: The median intensity value of the data points within the given boundary.
        """
        if boundary is not None:
            return self.filter(boundary).median()
        else:
            return np.median(self.intensity)

    def pad(self, length):
        """
        Pad the data and intensity arrays with zeros to a given length. Modifies the object in place.

        Args:
            length (int): The length of the output array
        
        Returns: 
            (new_data, new_intensity) : tuple of padded data and intensity

        """

        #### need to slice the array
        if length == len(self.data):
            new_data = self.data
            new_intensity = self.intensity
        elif length < len(self.data):
            if length % 2 == 0:
                slice_left = slice_right = length // 2
            else: # length % 2 == 1
                slice_left = length // 2 + 1
                slice_right = length // 2
            new_data = self.data[slice_left:-slice_right]
            new_intensity = self.intensity[slice_left:-slice_right]
        else: # length > len(self.data):
            ### infer the chromatogram step size
            step = self.data[1] - self.data[0]

            both_even_or_odd = length % 2 == len(self.data) % 2
            if both_even_or_odd:
                pad_left = pad_right = (length - len(self.data)) // 2

                new_intensity = np.copy(self.intensity)
                new_intensity = np.pad(new_intensity, (pad_left, pad_right), 'constant', constant_values=0)
            else:
                pad_left = (length - len(self.data)) // 2 + 1
                pad_right = (length - len(self.data)) // 2
                #### length is odd, unequal paddings #####
            
            #### Pad the data to left and right ####
            data_right = np.linspace(self.data[-1] + step, self.data[-1] + step * pad_right, num=pad_right)
            data_left = np.linspace(self.data[0] - step * pad_left, self.data[0] - step, num=pad_left)
            new_data = np.concatenate((data_left, self.data, data_right))
            new_intensity = np.copy(self.intensity)
            new_intensity = np.pad(new_intensity, (pad_left, pad_right), 'constant', constant_values=0)
        return (new_data, new_intensity)


    @abstractmethod
    def toPandasDf(self) -> pd.DataFrame:
        pass
   
    def toPandasDfHelper_(self, columnName) -> pd.DataFrame:
        '''
        Helper for converting a 1D data to pandas dataframe 
        '''
        df = pd.DataFrame(np.column_stack([self.data, self.intensity]),
                            columns=[columnName, 'intensity'])
        df['annotation'] = self.label
        return df
