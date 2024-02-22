"""
massdash/structs/TransitionGroupCollection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
from ..plotting import PlotConfig, InteractivePlotter

# Internal Imports
from .GenericStructCollection import GenericStructCollection

class TransitionGroupCollection(GenericStructCollection):
    '''
    A collection of TransitionGroups Objects with the Mapping <RunName>:<TransitionGroup>
    '''
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        