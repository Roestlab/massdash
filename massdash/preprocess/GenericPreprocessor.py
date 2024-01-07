"""
massdash/preprocess/GenericPreprocessor
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""


from structs.TransitionGroup import TransitionGroup

class GenericPreprocessor:
    def __init__(self, transition_group: TransitionGroup):
        self.transition_group = transition_group

    def preprocess(self):
        # Generic preprocessing logic
        pass