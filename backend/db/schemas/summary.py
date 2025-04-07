from pydantic import BaseModel, field_validator, ConfigDict
from datetime import datetime, timezone


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
    status: str

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

    @field_validator("status")
    def validate_status(cls, v: str) -> str:
        allowed_statuses = {"pending", "processing", "completed", "failed"}
        if v not in allowed_statuses:
            raise ValueError(f"Status must be one of {allowed_statuses}")
        return v.lower()
