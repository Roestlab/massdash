from massseer.structs.Peptide import Peptide
from typing import List

class Protein:
    '''
    Class to represent a protein
    '''

    def __init__(self, accession: str, peptides: List[Peptide]):
        self.accession = accession
        self.peptides = peptides