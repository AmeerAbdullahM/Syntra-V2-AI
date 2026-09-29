from abc import ABC, abstractmethod
from typing import BinaryIO

class StorageInterface(ABC):
    @abstractmethod
    def save(self, file_path: str, content: BinaryIO) -> str:
        """Saves a file to storage and returns a unique key or path."""
        pass

    @abstractmethod
    def get(self, file_path: str) -> BinaryIO:
        """Retrieves a file from storage."""
        pass

    @abstractmethod
    def delete(self, file_path: str) -> bool:
        """Deletes a file from storage."""
        pass
