from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Float, JSON
from sqlalchemy.sql import func
from backend.database.base import Base
from backend.models.user import generate_uuid

class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(String, primary_key=True, default=generate_uuid)
    material_id = Column(String, ForeignKey("materials.id", ondelete="CASCADE"), nullable=False)
    den_id = Column(String, ForeignKey("dens.id", ondelete="CASCADE"), nullable=False)
    
    modality = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    content_type = Column(String, nullable=False) # e.g. 'transcript', 'equation', 'diagram_label'
    confidence = Column(String, default="UNKNOWN") # HIGH, MEDIUM, LOW, UNKNOWN
    
    # Metadata as JSON (timestamps, coordinates, page number, slide number)
    metadata_json = Column(JSON, nullable=True) 
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class EvidenceRelation(Base):
    __tablename__ = "evidence_relations"

    id = Column(String, primary_key=True, default=generate_uuid)
    den_id = Column(String, ForeignKey("dens.id", ondelete="CASCADE"), nullable=False)
    rock_id = Column(String, ForeignKey("rocks.id", ondelete="CASCADE"), nullable=True)
    source_evidence_id = Column(String, ForeignKey("evidence.id", ondelete="CASCADE"), nullable=False)
    target_evidence_id = Column(String, ForeignKey("evidence.id", ondelete="CASCADE"), nullable=False)
    
    relationship = Column(String, nullable=False) # SUPPORTS, ELABORATES, REFERS_TO, CONTRADICTS
    confidence = Column(String, default="UNKNOWN")
    reasoning = Column(Text, nullable=True)
    
    is_resolved = Column(Integer, default=0) # 0 for false, 1 for true (SQLite compatibility)
    resolution_note = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
