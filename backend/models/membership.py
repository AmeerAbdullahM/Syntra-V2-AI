from sqlalchemy import Column, String, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from backend.database.base import Base
from backend.models.user import generate_uuid
import enum

class RoleEnum(str, enum.Enum):
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"

class Membership(Base):
    __tablename__ = "den_memberships"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    den_id = Column(String, ForeignKey("dens.id", ondelete="CASCADE"), nullable=False)
    role = Column(String, nullable=False, default=RoleEnum.MEMBER.value)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
