from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from backend.database.base import Base
from backend.models.user import generate_uuid

class Ban(Base):
    __tablename__ = "bans"

    id = Column(String, primary_key=True, default=generate_uuid)
    den_id = Column(String, ForeignKey("dens.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
