"""
massdash/structs/Spectrum
~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import pandas as pd

# Structs
from .Data1D import Data1D

class Spectrum(Data1D):
    ''' 
    A single spectrum object storing mz and intensity data.
    '''
    def __init__(self, mz, intensity, label):
        super().__init__(mz, intensity, label)
        
    def toPandasDf(self) -> pd.DataFrame:
        return super().toPandasDfHelper_('mz')
    
    def adjust_length(self, length: int) -> 'Spectrum':
        """
        Adjust the length of the spectrum to a given length, this involved either padding or truncating the spectrum

        Args:
            length (int): The desired output length.

        Returns:
            Spectrum: A new Spectrum object with padded/truncated length of mz and intensity.
        """
        new_data, new_intensity = super().adjust_length(length)
        return Spectrum(new_data, new_intensity, self.label)