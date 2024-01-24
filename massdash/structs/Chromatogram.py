"""
massdash/structs/Chromatogram
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import pyopenms as po
from typing import Optional
import pandas as pd

# Structs
from .Data1D import Data1D

class Chromatogram(Data1D):
    ''' 
    This is a single chromatogram object. Holds the data and metadata of a chromatogram
    '''
    def __init__(self, rt, intensity, label = 'None'):
        super().__init__(rt, intensity, label)
   
    def to_pyopenms(self, id: Optional[str] = None):
        '''
        Converts the Chromatogram to an OpenMS Chromatogram
        id (str): The nativeID of the chromatogram
        '''
        chrom = po.MSChromatogram()
        chrom.set_peaks((self.data, self.intensity))
        if id is not None:
            chrom.setNativeID(id)
        return chrom
    
    def toPandasDf(self) -> pd.DataFrame:
        return super().toPandasDfHelper_('rt')
    
    def adjust_length(self, length: int) -> 'Chromatogram':
        """
        Adjust the length of the chromatogram to a given length, this involved either padding or truncating the chromatogram

        Args:
            length (int): The desired output length.

        Returns:
            Chromatogram: A new chromatogram object with padded/truncated rt and intensity.
        """
        new_data, new_intensity = super().adjust_length(length)
        return Chromatogram(new_data, new_intensity, self.label)