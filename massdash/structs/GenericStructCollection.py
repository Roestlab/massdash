"""
massdash/structs/GenericStructCollection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

class GenericStructCollection(dict):
    '''
    Dictionary like object where keys are the run names and values are the data structures.
    '''

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def getRuns(self):
        return self.keys()