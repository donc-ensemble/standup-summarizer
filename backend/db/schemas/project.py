from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

from db.schemas.channel import ChannelResponse

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectResponse(ProjectBase):
    id: int
    channels:List[ChannelResponse] = []
    created_at: datetime

    class Config:
        orm_mode = True