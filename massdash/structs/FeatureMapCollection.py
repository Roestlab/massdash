"""
massdash/structs/FeatureMapCollection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

from .GenericStructCollection import GenericStructCollection
from .TransitionGroupCollection import TransitionGroupCollection

class FeatureMapCollection(GenericStructCollection):
    '''
    A collection of FeatureMap Objects with the Mapping <RunName>:<FeatureMap>
    '''
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def to_chromatograms(self):
        '''
        Convert the FeatureMapCollection to a TransitionGroupCollection

        Returns:
            TransitionGroupCollection: A collection of TransitionGroups Objects with the Mapping <RunName>:<TransitionGroup> storing Chromatograms
        '''
        return TransitionGroupCollection({run: featureMap.to_chromatograms() for run, featureMap in self.items()})
    
    def to_spectra(self):
        '''
        Convert the FeatureMapCollection to a TransitionGroupCollection

        Returns:
            TransitionGroupCollection: A collection of TransitionGroups Objects with the Mapping <RunName>:<TransitionGroup> storing Spectra
        '''
        return TransitionGroupCollection({run: featureMap.to_spectra() for run, featureMap in self.items()})
 
    def to_mobilograms(self):
        '''
        Convert the FeatureMapCollection to a TransitionGroupCollection

        Returns:
            TransitionGroupCollection: A collection of TransitionGroups Objects with the Mapping <RunName>:<TransitionGroup> storing Mobilograms
        '''
        return TransitionGroupCollection({run: featureMap.to_mobilograms() for run, featureMap in self.items()})