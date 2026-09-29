from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

class QueueInterface(ABC):
    @abstractmethod
    def enqueue(self, job_type: str, den_id: str, target_id: str, user_id: str, payload: Dict[str, Any]) -> str:
        """Enqueue a new job and return its ID."""
        pass
        
    @abstractmethod
    def dequeue(self, job_type: str) -> Optional[Dict[str, Any]]:
        """Dequeue the next pending job of the given type.
        Returns a dict containing 'job_id' and 'payload', or None if empty."""
        pass
        
    @abstractmethod
    def complete(self, job_id: str):
        """Mark a job as completed."""
        pass
        
    @abstractmethod
    def fail(self, job_id: str, error_message: str):
        """Mark a job as failed."""
        pass
