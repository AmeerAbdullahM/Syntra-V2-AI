import os
from typing import BinaryIO
from backend.storage.interface import StorageInterface
from backend.config.settings import settings
import shutil

class LocalStorageAdapter(StorageInterface):
    def __init__(self, base_path: str = None):
        self.base_path = base_path or settings.LOCAL_STORAGE_PATH
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path)

    def _get_full_path(self, file_path: str) -> str:
        # Prevent path traversal
        base_abs = os.path.abspath(self.base_path)
        normalized_path = os.path.abspath(os.path.join(self.base_path, file_path))
        if os.path.commonpath([base_abs, normalized_path]) != base_abs:
            raise ValueError("Path traversal attempted")
        return normalized_path

    def save(self, file_path: str, content: BinaryIO) -> str:
        full_path = self._get_full_path(file_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "wb") as f:
            shutil.copyfileobj(content, f)
        return file_path

    def get(self, file_path: str) -> BinaryIO:
        full_path = self._get_full_path(file_path)
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        return open(full_path, "rb")

    def delete(self, file_path: str) -> bool:
        full_path = self._get_full_path(file_path)
        if os.path.exists(full_path):
            os.remove(full_path)
            return True
        return False
