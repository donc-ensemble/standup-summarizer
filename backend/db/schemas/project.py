from pydantic import BaseModel, ConfigDict, field_validator
from datetime import datetime, timezone
from typing import List, Optional

from db.schemas.channel import ChannelResponse


class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectResponse(ProjectBase):
    id: int
    channels: List[ChannelResponse] = []
    created_at: datetime

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
