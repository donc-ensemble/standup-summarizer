from pydantic import BaseModel
from datetime import datetime
from typing import List
from db.schemas.summary import SummaryResponse
class ChannelBase(BaseModel):
    project_id: int
    label: str
    channel_id: str

class ChannelCreate(ChannelBase):
    pass

class ChannelResponse(ChannelBase):
    id: int
    created_at: datetime
    summaries: List[SummaryResponse] = []

    class Config:
        from_attributes = True