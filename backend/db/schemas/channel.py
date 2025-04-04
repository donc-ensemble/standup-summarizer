from pydantic import BaseModel
from datetime import datetime

class ChannelBase(BaseModel):
    project_id: int
    label: str
    channel_id: str

class ChannelCreate(ChannelBase):
    pass

class ChannelResponse(ChannelBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True