from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class RockCreate(BaseModel):
    den_id: str
    title: str
    description: Optional[str] = None
    order_index: int = 0

class RockResponse(BaseModel):
    id: str
    den_id: str
    title: str
    description: Optional[str]
    order_index: int
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}
