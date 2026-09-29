from backend.config.settings import settings
from backend.storage.interface import StorageInterface
from backend.storage.local import LocalStorageAdapter

def get_storage() -> StorageInterface:
    if settings.STORAGE_BACKEND == "local":
        return LocalStorageAdapter()
    # elif settings.STORAGE_BACKEND == "s3":
    #     return ObjectStorageAdapter()
    else:
        # Default to local if not recognized
        return LocalStorageAdapter()
