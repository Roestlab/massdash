from abc import ABC, abstractmethod

class BaseUISettings(ABC):
    """
    Base class for UI settings.
    """

    def __init__(self) -> None:
        self.threads = 1
        
    @abstractmethod
    def create_ui(self):
        pass