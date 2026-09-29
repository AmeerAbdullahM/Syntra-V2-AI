from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from backend.database.base import Base
from backend.models.user import generate_uuid
import enum

class MaterialStatusEnum(str, enum.Enum):
    UPLOADED = "UPLOADED"
    VALIDATING = "VALIDATING"
    QUEUED = "QUEUED"
    EXTRACTING = "EXTRACTING"
    ALIGNING = "ALIGNING"
    FUSING = "FUSING"
    CHECKING_CONFLICTS = "CHECKING_CONFLICTS"
    GENERATING_ARTIFACTS = "GENERATING_ARTIFACTS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    RETRYING = "RETRYING"

class ModalityEnum(str, enum.Enum):
    AUDIO = "AUDIO"
    VISUAL = "VISUAL"
    DOCUMENT = "DOCUMENT"
    TEXT = "TEXT"

class Material(Base):
    __tablename__ = "materials"

    id = Column(String, primary_key=True, default=generate_uuid)
    den_id = Column(String, ForeignKey("dens.id", ondelete="CASCADE"), nullable=False)
    rock_id = Column(String, ForeignKey("rocks.id", ondelete="CASCADE"), nullable=False)
    uploader_id = Column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    original_filename = Column(String, nullable=False)
    stored_filename = Column(String, nullable=False)
    mime_type = Column(String, nullable=False)
    size_bytes = Column(Integer, nullable=False)
    checksum = Column(String, nullable=False)
    modality = Column(String, nullable=False)
    
    processing_status = Column(String, default=MaterialStatusEnum.UPLOADED.value)
    failure_reason = Column(Text, nullable=True)
    
    upload_timestamp = Column(DateTime(timezone=True), server_default=func.now())
    processing_timestamp = Column(DateTime(timezone=True), nullable=True)

    rock = relationship("Rock")
    den = relationship("Den")
    uploader = relationship("User")
