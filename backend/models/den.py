from sqlalchemy import Column, String, DateTime, Text, Integer, Boolean
from sqlalchemy.sql import func
from backend.database.base import Base
from backend.models.user import generate_uuid

class Den(Base):
    __tablename__ = "dens"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    is_public = Column(String, default="true") # Using string "true"/"false" for boolean simplicity or Boolean
    invite_code = Column(String, nullable=True)
    max_members = Column(Integer, nullable=True) # None means unlimited
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
