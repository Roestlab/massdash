"""
massdash/structs/Mobilogram
~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import pandas as pd

# Structs
from .Data1D import Data1D

class Mobilogram(Data1D):
    ''' 
    This is a single mobilogram object. Holds the data and metadata of a mobilogram
    '''
    def __init__(self, im, intensity, label):
        super().__init__(im, intensity, label)

    def toPandasDf(self) -> pd.DataFrame:
        return super().toPandasDfHelper_(self, 'im')
    
    def adjust_length(self, length: int) -> 'Mobilogram':
        """
        Adjust the length of the mobilogram to a given length, this involved either padding or truncating the mobilogram

        Args:
            length (int): The desired output length.

        Returns:
            Mobilogram: A new Mobilogram object with padded/truncated driftTime and intensity.
        """
        new_data, new_intensity = super().adjust_length(length)
        return Mobilogram(new_data, new_intensity, self.label)