from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from backend.database.base import Base
from backend.models.user import generate_uuid

class Artifact(Base):
    __tablename__ = "artifacts"

    id = Column(String, primary_key=True, default=generate_uuid)
    den_id = Column(String, ForeignKey("dens.id", ondelete="CASCADE"), nullable=False)
    rock_id = Column(String, ForeignKey("rocks.id", ondelete="CASCADE"), nullable=False)
    
    title = Column(String, nullable=False)
    artifact_type = Column(String, nullable=False) # e.g., "CHEAT_SHEET", "FLASHCARDS", "SUMMARY"
    content_markdown = Column(Text, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
