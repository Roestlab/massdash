from massseer.structs.Chromatogram import Chromatogram
from typing import List

class TransitionGroup:
    '''
    Class for Storing a transition group
    '''
    def __init__(self, precursorChroms: List[Chromatogram], transitionChroms: List[Chromatogram]):
        self.precursorChroms = precursorChroms
        self.transitionChroms = transitionChroms