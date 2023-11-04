class Precursor:
    """
    A class representing a precursor ion in mass spectrometry.

    Attributes:
    -----------
    mz : float
        The m/z value of the precursor ion.
    charge : int
        The charge state of the precursor ion.
    """

    def __init__(self, mz: float, charge: int):
        self.mz = mz            
        self.charge = charge

