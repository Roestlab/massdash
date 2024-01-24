"""
massdash/structs/Spectrum
~~~~~~~~~~~~~~~~~~~~~~~~~
"""

from typing import Tuple
import pandas as pd

# Structs
from .Data1D import Data1D

class Spectrum(Data1D):
    ''' 
    This is a single spectrum object. Holds the data and metadata of a spectrum
    '''
    def __init__(self, mz, intensity, label):
        super().__init__(mz, intensity, label)
        
    def toPandasDf(self) -> pd.DataFrame:
        return super().toPandasDfHelper_(self, 'mz')
    
    def pad(self, length: int) -> 'Spectrum':
        """
        Pad the spectrum with zeros on both sides.

        Args:
            pad (int): The number of zeros to pad on both sides.

        Returns:
            Chromatogram: A new chromatogram object with padded data and intensity.
        """
        new_data, new_intensity = super().pad(length)
        return Spectrum(new_data, new_intensity, self.label)