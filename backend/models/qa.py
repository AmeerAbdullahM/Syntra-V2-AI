from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.sql import func
from backend.database.base import Base
from backend.models.user import generate_uuid

class QAThread(Base):
    __tablename__ = "qa_threads"

    id = Column(String, primary_key=True, default=generate_uuid)
    den_id = Column(String, ForeignKey("dens.id", ondelete="CASCADE"), nullable=False)
    author_id = Column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    question = Column(Text, nullable=False)
    status = Column(String, default="OPEN") # OPEN, RESOLVED
    
    # Optional linked context (e.g. they asked a question about a specific concept or rock)
    linked_rock_id = Column(String, ForeignKey("rocks.id", ondelete="SET NULL"), nullable=True)
    linked_concept_id = Column(String, ForeignKey("fused_concepts.id", ondelete="SET NULL"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class QAMessage(Base):
    __tablename__ = "qa_messages"

    id = Column(String, primary_key=True, default=generate_uuid)
    thread_id = Column(String, ForeignKey("qa_threads.id", ondelete="CASCADE"), nullable=False)
    author_id = Column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True) # If null, it's the AI
    
    content = Column(Text, nullable=False)
    is_ai = Column(String, default="false") # "true" or "false"
    
    # Explanations from AI might include sources/evidence IDs
    sources_json = Column(JSON, nullable=True) 

    created_at = Column(DateTime(timezone=True), server_default=func.now())
