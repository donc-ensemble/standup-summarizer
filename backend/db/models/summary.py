from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime, timezone
from db.base import Base
from sqlalchemy.orm import relationship

class Summary(Base):
    __tablename__ = "summaries"

    id = Column(Integer, primary_key=True, index=True)
    channel_id = Column(Integer, ForeignKey("channels.id"), nullable=False)
    audio_file_path = Column(String, nullable=False)
    transcript = Column(String)
    summary = Column(String)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    channel = relationship("Channel", back_populates="summaries")
