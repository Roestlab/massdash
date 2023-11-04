from massseer.structs.Precursor import Precursor

from typing import List

class Peptide:
    """
    A class representing a peptide sequence.

    Attributes:
    -----------
    sequence : str
        The amino acid sequence of the peptide.
    products : list
        A list of product ions associated with the peptide.
    """

    def __init__(self, sequence: str):
        self.sequence = sequence

    def __str__(self) -> str:
        """
        Returns a string representation of the peptide.

        Returns:
            str: A string representation of the peptide.
        """
        return f"Peptide: {self.sequence}\n{self.precursor}\n"

    def add_precursor(self, precursor: Precursor) -> None:
        """
        Adds a precursor to the peptide.

        Args:
            precursor (Precursor): The precursor to add.

        Returns:
            None
        """
        self.precursor = precursor

    def get_precursor_mz(self) -> float:
        """
        Returns the precursor m/z value of the peptide.
        
        Returns:
        float: The precursor m/z value of the peptide.
        """
        return self.precursor.mz

    def get_precursor_charge(self) -> int:
        """
        Returns the charge of the precursor ion associated with this peptide.
        
        Returns:
            int: The charge of the precursor ion.
        """
        return self.precursor.charge

    def get_product_mzs(self) -> List[float]:
        """
        Returns a list of the m/z values for all products associated with this peptide.
        
        Returns:
            List[float]: A list of the m/z values for all products associated with this peptide.
        """
        return [product.mz for product in self.precursor.products]
    
    def get_product_charges(self) -> List[int]:
        """
        Returns a list of charges for all products in the peptide.
        """
        return [product.charge for product in self.precursor.products]

    def get_product_annotations(self) -> List[str]:
        """
        Returns a list of annotations for each product in the peptide.
        """
        return [product.annotation for product in self.precursor.products]

    def get_sequence_wo_terminal_period(self) -> str:
        """
        Returns the peptide sequence without the terminal period.
        Example: Convert .(UniMod:1)SEGDSVGESVHGKPSVVYR to (UniMod:1)SEGDSVGESVHGKPSVVYR
        """
        return self.sequence.replace('.', '')