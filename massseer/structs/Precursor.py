from massseer.structs.Product import Product

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
        """
        Initialize a Precursor instance with the specified m/z and charge.

        Args:
            mz (float): The m/z value of the precursor ion.
            charge (int): The charge state of the precursor ion.
        """
        self.mz = mz
        self.charge = charge
        self.products = []
        self._library_intensity = None
        self._library_rt = None
        self._library_ion_mobility = None
        self.chromatogram_peak_feature = None
        self.mobilogram_peak_feature = None

    def __str__(self) -> str:
        """
        Returns a string representation of the Precursor object, including its m/z value, charge state, product ions,
        library intensity, library retention time, and library ion mobility.
        """
        return f"{'-'*8} Precursor {'-'*8}\nm/z: {self.mz}\nCharge: {self.charge}\nLibrary intensity: {self.library_intensity}\nLibrary RT: {self.library_rt}\nLibrary IM: {self.library_ion_mobility}\n{'-'*8} Chromatogram -{self.chromatogram_peak_feature}\n{'-'*8}Mobilogram -{self.mobilogram_peak_feature}\n" + "\n".join(str(products) for products in self.products)

    @property
    def library_intensity(self):
        """
        Returns the library intensity of the precursor.

        Returns:
            float: The library intensity of the precursor.
        """
        return self._library_intensity

    @property
    def library_rt(self):
        """
        Returns the library retention time of the precursor.

        Returns:
            float: The library retention time of the precursor.
        """
        return self._library_rt

    @property
    def library_ion_mobility(self):
        """
        Returns the library ion mobility of the precursor.

        Returns:
            float: The library ion mobility of the precursor.
        """
        return self._library_ion_mobility

    def add_product(self, product):
        """
        Adds a product to the list of products associated with this precursor.

        Args:
            product: The product to add.

        Returns:
            None
        """
        self.products.append(product)

    @library_intensity.setter
    def library_intensity(self, value):
        """
        Sets the library intensity of the precursor.

        Args:
            value (float): The library intensity to set.

        Returns:
            None
        """
        self._library_intensity = value

    @library_rt.setter
    def library_rt(self, value):
        """
        Sets the library retention time of the precursor.

        Args:
            value (float): The library retention time to set.

        Returns:
            None
        """
        self._library_rt = value

    @library_ion_mobility.setter
    def library_ion_mobility(self, value):
        """
        Sets the library ion mobility of the precursor.

        Args:
            value (float): The library ion mobility to set.

        Returns:
            None
        """
        self._library_ion_mobility = value

    def get_library_intensity(self):
        """
        Returns the library intensity of the precursor.

        Returns:
            float: The library intensity of the precursor.
        """
        return self._library_intensity

    def get_library_rt(self):
        """
        Returns the library retention time of the precursor.

        Returns:
            float: The library retention time of the precursor.
        """
        return self._library_rt

    def get_library_ion_mobility(self):
        """
        Returns the library ion mobility of the precursor.

        Returns:
            float: The library ion mobility of the precursor.
        """
        return self._library_ion_mobility
