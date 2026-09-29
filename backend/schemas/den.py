from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DenCreate(BaseModel):
    name: str
    description: Optional[str] = None
    is_public: bool = True
    invite_code: Optional[str] = None
    max_members: Optional[int] = None

class DenResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    is_public: Optional[str] = "true"
    invite_code: Optional[str]
    max_members: Optional[int]
    created_at: datetime

    model_config = {"from_attributes": True}

class MembershipResponse(BaseModel):
    id: str
    user_id: str
    den_id: str
    role: str
    created_at: datetime

    model_config = {"from_attributes": True}

class JoinRequestResponse(BaseModel):
    id: str
    den_id: str
    user_id: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
