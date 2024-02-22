"""
massdash/structs/GenericStructCollection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

class GenericStructCollection(dict):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def getRuns(self):
        return self.keys()