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
        """
        Initialize a Product instance with the specified m/z, charge, and annotation.

        Args:
            mz (float): The mass-to-charge ratio of the product.
            charge (int): The charge of the product.
            annotation (str): The annotation of the product.
        """
        self.mz = mz
        self.charge = charge            
        self.annotation = annotation
        self._library_intensity = None

    def __str__(self) -> str:
        """
        Returns a string representation of the product.

        Returns:
            str: A string representation of the product.
        """
        product_info = "\n".join([f"  {product}" for product in self.products])
        return f"{'-'*8} Precursor {'-'*8}\nm/z: {self.mz}\nCharge: {self.charge}\nProducts:\n{product_info}\nLibrary intensity: {self.library_intensity}\nLibrary RT: {self.library_rt}\nLibrary IM: {self.library_ion_mobility}"


    @property
    def library_intensity(self) -> float:
        """
        Returns the library intensity of the product.

        Returns:
            float: The library intensity of the product.
        """
        return self._library_intensity

    @library_intensity.setter
    def library_intensity(self, value: float) -> None:
        """
        Sets the library intensity of the product.

        Args:
            value (float): The library intensity to set.

        Returns:
            None
        """
        self._library_intensity = value
