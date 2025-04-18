from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime, timezone
from db.base import Base
from sqlalchemy.orm import relationship


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    channels = relationship(
        "Channel",
        back_populates="project",
        cascade="all, delete-orphan",
        order_by="desc(Channel.created_at)",
    )
