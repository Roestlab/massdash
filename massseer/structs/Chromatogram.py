import numpy as np

class Chromatogram:
    ''' 
    This is a single chromatogram object. Holds the data and metadata of a chromatogram
    '''
    def __init__(self, rt, intensity, label):
        self.intensity = np.array(intensity)
        self.rt = np.array(rt)
        self.label = label
