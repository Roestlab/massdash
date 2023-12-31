'''
This is an abstract class for loading spectra from a file.
'''
from massseer.loaders.GenericLoader import GenericLoader
from abc import ABC, abstractmethod
from massseer.structs.TransitionGroup import TransitionGroup
from typing import List, Union, Literal

class GenericSpectrumLoader(GenericLoader, ABC):
    def __init__(self, rsltsFile: str, dataFiles: Union[str, List[str]], libraryFile: str = None, rsltsFileType: Literal['OpenSWATH', 'DIA-NN'] = 'DIA-NN', verbose: bool=False, mode: Literal['module', 'gui'] = 'module'):
        super().__init__(rsltsFile=rsltsFile, dataFiles=dataFiles, libraryFile=libraryFile, rsltsFileType=rsltsFileType, verbose=verbose, mode=mode)

    @abstractmethod
    def loadFeatureMaps(self, pep_id: str, charge: int) -> dict[str, TransitionGroup]:
        return super().loadTopTransitionGroupFeature(pep_id, charge)


