from pydantic import BaseModel
from datetime import datetime

class SummaryBase(BaseModel):
    channel_id: int
    audio_file_path: str
    transcript: str | None = None
    summary: str | None = None

class SummaryCreate(SummaryBase):
    pass

class SummaryResponse(SummaryBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True