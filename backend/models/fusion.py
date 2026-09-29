from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.sql import func
from backend.database.base import Base
from backend.models.user import generate_uuid

class FusedConcept(Base):
    __tablename__ = "fused_concepts"

    id = Column(String, primary_key=True, default=generate_uuid)
    den_id = Column(String, ForeignKey("dens.id", ondelete="CASCADE"), nullable=False)
    rock_id = Column(String, ForeignKey("rocks.id", ondelete="CASCADE"), nullable=True) # Making nullable=True initially for migration, then we populate it
    title = Column(String, nullable=False)
    explanation = Column(Text, nullable=False)
    confidence = Column(String, default="UNKNOWN")
    alignment_status = Column(String, nullable=False) # ALIGNED, UNRESOLVED_CONFLICT, EXPLICIT_CORRECTION, INSUFFICIENT_EVIDENCE
    
    # List of evidence IDs supporting this concept
    evidence_ids = Column(JSON, nullable=False) 
    
    accessibility_description = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
