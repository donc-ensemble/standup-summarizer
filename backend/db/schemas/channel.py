from pydantic import BaseModel, ConfigDict, field_validator
from datetime import datetime, timezone
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

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda dt: (
                dt.astimezone().isoformat()
                if dt.tzinfo
                else dt.replace(tzinfo=timezone.utc).astimezone().isoformat()
            )
        },
    )

    @field_validator("created_at")
    def convert_datetime_to_local(cls, v: datetime) -> datetime:
        if v is None:
            return v

        if v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)

        return v.astimezone()
