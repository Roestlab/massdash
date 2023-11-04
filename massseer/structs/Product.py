class Product:
    """
    A class representing a product.

    Attributes:
    ----------
    mz : float
        The mass-to-charge ratio of the product.
    charge : int
        The charge of the product.
    annotation : str
        The annotation of the product.
    """
    def __init__(self, mz: float, charge: int, annotation: str):
        self.mz = mz
        self.charge = charge            
        self.annotation = annotation

