from abc import ABC, abstractmethod

class Parser(ABC):

    @abstractmethod
    def extract_text() -> str: 
        """Extract all text from the document"""
        pass
