# Structs
from massseer.structs.TransitionGroup import TransitionGroup
from massseer.structs.TransitionGroupFeature import TransitionGroupFeature
# Loaders
from massseer.loaders.GenericLoader import GenericLoader
from massseer.loaders.reportLoader import reportLoader
# Utils
from massseer.util import LOGGER


class DiaNNLoader(GenericLoader):
    ''' 
    Class to load a Dia-NN report file
    
    Attributes:
        results_file_path: (str) The path to the results file
        transition_file_path: (str) The path to the transition file
        report: (reportLoader) The reportLoader object
        
    Methods:
        loadTransitionGroups: Load transition groups from the given targeted transition list
        loadTransitionGroupFeature: Load transition group features from the given targeted transition list
        load_report: Load the report file
        load_report_for_precursor: Load the report file for a precursor
    '''

    def __init__(self, results_file_path: str, verbose: bool=False) -> None:
        super().__init__(results_file_path, None)
        self.report = reportLoader(results_file_path, verbose)
        
        LOGGER.name = "DiaNNLoader"
        if verbose:
            LOGGER.setLevel("DEBUG")
        else:
            LOGGER.setLevel("INFO")

    def __repr__(self) -> str:
        return f"DiaNNLoader(results_file_path={self.results_file_path}, verbose={self.verbose})"

    def loadTransitionGroups(pep_id: str, charge: int) -> TransitionGroup:
        pass

    def loadTransitionGroupFeature(pep_id: str, charge: int) -> TransitionGroupFeature:
        pass

    def load_report(self) -> None:
        '''
        Load the report file
        '''
        self.report.load_report()
    
    def load_report_for_precursor(self, peptide: str, charge: int) -> reportLoader:
        '''
        Load the report file for a precursor
        
        Args:
            peptide: (str) The peptide sequence to search for
            charge: (int) The charge state to search for
            
        Returns:
            self: (reportLoader) The reportLoader object
        '''
        return self.report.load_report_for_precursor(peptide, charge)
