import numpy as np

class Mobilogram:
    ''' 
    This is a single mobilogram object. Holds the data and metadata of a mobilogram
    '''
    def __init__(self, im, intensity, label):
        self.intensity = np.array(intensity)
        self.im = np.array(im)
        self.label = label

    def __str__(self):
        return f"{'-'*8} Mobilogram {'-'*8}\nlabel: {self.label}\nlength of mobilogram: {len(self.im)}"