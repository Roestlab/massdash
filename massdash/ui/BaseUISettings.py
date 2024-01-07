"""
massdash/ui/BaseUISettings
~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

from abc import ABC, abstractmethod

class BaseUISettings(ABC):
    """
    Base class for UI settings.
    
    Attributes:
        threads (int): Number of threads to use for processing the files.
        
    Methods:
        create_ui: Creates the user interface for the FileInput___UISettings.
    """

    def __init__(self) -> None:
        self.threads = 1
        
    @abstractmethod
    def create_ui(self):
        pass