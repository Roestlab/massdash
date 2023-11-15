import numpy as np

class Spectrum:
    ''' 
    This is a single spectrum object. Holds the data and metadata of a spectrum
    '''
    def __init__(self, mz, intensity, label):
        self.intensity = np.array(intensity)
        self.mz = np.array(mz)
        self.label = label

    def __str__(self):
        return f"{'-'*8} Spectrum {'-'*8}\nlabel: {self.label}\nlength of spectrum: {len(self.mz)}"
    
    def empty(self) -> bool:
        """
        Check if the Spectrum is empty.

        Returns:
            bool: True if both mz and intensity are empty, False otherwise.
        """
        return not (self.mz.any() and self.intensity.any())