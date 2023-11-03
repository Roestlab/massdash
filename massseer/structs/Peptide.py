from massseer.structs.Precursor
from massseer.structs.Product
from typing import List

class Peptide:
    '''
    Class to represent a peptide
    '''
    def __init__(self, sequence: str, precursor: Precursor, products: List[Product]):
        self.sequence = sequence
        self.precursor = precursor
        self.products = products

    def get_precursor_mz(self) -> float:
        return self.precursor.mz

    def get_precursor_charge(self) -> int:
        return self.precursor.charge

    def get_product_mzs(self) -> List[float]:
        return [product.mz for product in self.products]
    
    def get_product_charges(self) -> List[int]:
        return [product.charge for product in self.products]

    def get_product_annotations(self) -> List[str]:
        return [product.annotation for product in self.products]