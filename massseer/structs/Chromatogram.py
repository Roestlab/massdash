import numpy as np

class Chromatogram:
    ''' 
    This is a single chromatogram object. Holds the data and metadata of a chromatogram
    '''
    def __init__(self, rt, intensity, label):
        self.intensity = np.array(intensity)
        self.rt = np.array(rt)
        self.label = label

    def __str__(self):
        return f"{'-'*8} Chromatogram {'-'*8}\nlabel: {self.label}\nlength of chromatogram: {len(self.rt)}"
    
    def empty(self) -> bool:
        """
        Check if the Chromatogram is empty.

        Returns:
            bool: True if both rt and intensity are empty, False otherwise.
        """
        return not (self.rt.any() and self.intensity.any())
