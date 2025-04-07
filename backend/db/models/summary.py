from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from datetime import datetime, timezone
from db.base import Base
from sqlalchemy.orm import relationship

class Summary(Base):
    __tablename__ = "summaries"

    id = Column(Integer, primary_key=True, index=True)
    channel_id = Column(Integer, ForeignKey("channels.id"))
    job_id = Column(String, unique=True, index=True)
    original_filename = Column(String)
    transcript = Column(Text)
    summary = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    slack_notification_sent = Column(Boolean, default=False)
    
    channel = relationship("Channel", back_populates="summaries")