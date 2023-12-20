
from typing import List, Union

# Loaders
from massseer.loaders.access.MzMLDataAccess import MzMLDataAccess
from massseer.loaders.GenericLoader import GenericLoader
from massseer.loaders.access.OSWDataAccess import OSWDataAccess
from massseer.loaders.access.ResultsTSVDataAccess import ResultsTSVDataAccess
# Utils
from massseer.util import LOGGER

class MzMLDataLoader(GenericLoader):
    '''
    Class to load data from MzMLFiles using a .osw output file or .tsv report file
    
    Attributes:
        rsltsFile: (str) The path to the report file (DIANN-TSV or OSW)
        dataFiles: (str/List[str]) The path to the mzML file(s)
        
    Methods:
        get_row_indices_for_peptide: Get the row indices in the report for a peptide and charge state
        load_report_for_precursor: Load the report file for a precursor
        load_report: Load the report file
    '''
    def __init__(self, rsltsFile: str, dataFiles: Union[str, List[str]], verbose: bool=False) -> None:
        super().__init__(rsltsFile, dataFiles, verbose)
        self.dataFiles = [MzMLDataAccess(f, 'ondisk') for f in dataFiles]
        self.rsltsFile = self.loadResultsFile(rsltsFile)
                   
    def loadResultsFile(self, rsltsFile: str) -> None:
        '''
        Load the report file, currently only DIA-NN tsv files are supported
        
        Args:
            rsltsFile: (str) The path to the report file
            
        Returns:
            self: (reportLoader) The reportLoader object
        '''
        if rsltsFile.endswith('.osw'):
            self.rsltsFile = OSWDataAccess(rsltsFile, self.dataFiles)
        elif rsltsFile.endswith('.tsv'):
            self.rsltsFile = ResultsTSVDataAccess(rsltsFile, self.dataFiles)
        else:
            raise Exception(f"Error: Unsupported file type {rsltsFile}")