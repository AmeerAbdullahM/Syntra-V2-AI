from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class MaterialCreate(BaseModel):
    den_id: str
    rock_id: str
    uploader_id: str
    original_filename: str
    stored_filename: str
    mime_type: str
    size_bytes: int
    checksum: str
    modality: str

class MaterialResponse(BaseModel):
    id: str
    den_id: str
    rock_id: str
    uploader_id: Optional[str]
    original_filename: str
    stored_filename: str
    mime_type: str
    size_bytes: int
    checksum: str
    modality: str
    processing_status: str
    failure_reason: Optional[str]
    upload_timestamp: datetime
    processing_timestamp: Optional[datetime]

    model_config = {"from_attributes": True}
