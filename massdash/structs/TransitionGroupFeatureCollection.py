"""
massdash/structs/TransitionGroupFeatureCollection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

from .GenericStructCollection import GenericStructCollection
from collections import defaultdict

class TransitionGroupFeatureCollection(defaultdict, GenericStructCollection):
    '''
    A collection of TransitionGroupFeature Objects with the Mapping <RunName>:List[<TransitionGroupFeature>]
    '''
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def __str__(self) -> str:
        return str(__class__.__name__) + '\n' + '\n'.join(f'{k}: {v}' for k, v in self.items())
    
    def __repr__(self) -> str:
        return str(__class__.__name__) + '\n' + '\n'.join(f'{k}: {v}' for k, v in self.items())