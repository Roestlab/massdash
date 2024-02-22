"""
massdash/structs/TopTransitionGroupFeatureCollection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

from .GenericStructCollection import GenericStructCollection

class TopTransitionGroupFeatureCollection(GenericStructCollection):
    '''
    A collection of TransitionGroups Objects with the Mapping <RunName>:<TransitionGroupFeature>
    Note: unlike TransitionGroupFeatureCollection, the keys are not a list of TransitionGroupFeatures, just a single TransitionGroupFeature
    '''
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
