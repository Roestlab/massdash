from massseer.structs.Peptide import Peptide

class Protein:
    '''
    Class to represent a protein.

    Attributes:
    -----------
    accession : str
        The protein's accession number.
    peptides : list
        A list of Peptide objects representing the protein's peptides.
    '''
    def __init__(self, accession: str):
        self.accession = accession
        self.peptides = []

    def __str__(self) -> str:
        '''
        Returns a string representation of the protein.

        Returns:
            str: A string representation of the protein.
        '''
        return f"{'-'*8} Protein {'-'*8}\nAccession: {self.accession}\n" + ", ".join(str(peptide) for peptide in self.peptides)


    def add_peptide(self, peptide: Peptide) -> None:
            """
            Adds a peptide to the protein's list of peptides.

            Args:
                peptide (Peptide): The peptide to add.

            Returns:
                None
            """
            self.peptides.append(peptide)
