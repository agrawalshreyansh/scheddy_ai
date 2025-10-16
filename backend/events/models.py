from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Date, Integer, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.database import Base
from events.enums import PriorityTag
import uuid


class CalendarEvent(Base):
    """Calendar Event model for storing calendar tasks/events"""
    __tablename__ = "calendar_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    task_title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    
    # Priority fields
    priority_number = Column(Integer, nullable=False, default=5)  # 1-10, default medium (5)
    priority_tag = Column(Enum(PriorityTag), nullable=False, default=PriorityTag.MEDIUM, index=True)
    
    # Foreign key to link to user who created this event
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationship to dates (one-to-many)
    dates = relationship("CalendarDate", back_populates="calendar_event", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<CalendarEvent(id={self.id}, task_title='{self.task_title}', start_time='{self.start_time}')>"

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "task_title": self.task_title,
            "description": self.description,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "priority_number": self.priority_number,
            "priority_tag": self.priority_tag.value if self.priority_tag else None,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class CalendarDate(Base):
    """Calendar Date model for storing specific dates associated with calendar events"""
    __tablename__ = "calendar_dates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    event_date = Column(Date, nullable=False, index=True)
    event_uuid = Column(UUID(as_uuid=True), ForeignKey("calendar_events.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationship back to calendar event (many-to-one)
    calendar_event = relationship("CalendarEvent", back_populates="dates")

    def __repr__(self):
        return f"<CalendarDate(id={self.id}, event_date='{self.event_date}', event_uuid='{self.event_uuid}')>"

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "event_date": self.event_date.isoformat() if self.event_date else None,
            "event_uuid": self.event_uuid,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
