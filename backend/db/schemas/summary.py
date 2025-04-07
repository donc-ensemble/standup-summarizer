from pydantic import BaseModel
from datetime import datetime

class SummaryBase(BaseModel):
    channel_id: int
    original_filename: str
    transcript: str
    summary: str

class SummaryCreate(SummaryBase):
    job_id: str

class SummaryResponse(SummaryBase):
    id: int
    job_id: str
    created_at: datetime
    slack_notification_sent: bool

    class Config:
        from_attributes = True