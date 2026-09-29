from sqlalchemy import Column, String, Integer, DateTime, Text
from sqlalchemy.sql import func
from backend.database.base import Base
from backend.models.user import generate_uuid
import enum

class JobStatusEnum(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    RETRYING = "RETRYING"

class JobTypeEnum(str, enum.Enum):
    MATERIAL_PROCESS = "MATERIAL_PROCESS"
    QA_PROCESS = "QA_PROCESS"
    ROCK_FUSION = "ROCK_FUSION"

class Job(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True, default=generate_uuid)
    job_type = Column(String, nullable=False)
    status = Column(String, default=JobStatusEnum.PENDING.value)
    payload = Column(Text, nullable=False) # JSON encoded string
    
    den_id = Column(String, nullable=False, index=True)
    target_id = Column(String, nullable=False) # Material ID or QA ID
    user_id = Column(String, nullable=True) # Requester

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    retry_count = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
