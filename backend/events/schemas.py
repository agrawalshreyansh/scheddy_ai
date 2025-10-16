from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, List
from datetime import datetime, date
from uuid import UUID
from events.enums import PriorityTag


class CalendarEventBase(BaseModel):
    """Base CalendarEvent schema with common attributes"""
    task_title: str = Field(..., min_length=1, max_length=200, description="Title of the task/event")
    description: Optional[str] = Field(None, description="Detailed description of the task/event")
    start_time: datetime = Field(..., description="Start time of the event")
    end_time: datetime = Field(..., description="End time of the event")
    priority_number: int = Field(5, ge=1, le=10, description="Priority number between 1 (lowest) and 10 (highest)")
    priority_tag: PriorityTag = Field(PriorityTag.MEDIUM, description="Priority tag for the event")


class CalendarEventCreate(CalendarEventBase):
    """Schema for creating a new calendar event"""
    user_id: UUID = Field(..., description="ID of the user who owns this event")


class CalendarEventUpdate(BaseModel):
    """Schema for updating calendar event information"""
    task_title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    priority_number: Optional[int] = Field(None, ge=1, le=10, description="Priority number between 1 and 10")
    priority_tag: Optional[PriorityTag] = None


class CalendarEventResponse(CalendarEventBase):
    """Schema for calendar event response"""
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Calendar Date Schemas

class CalendarDateBase(BaseModel):
    """Base CalendarDate schema with common attributes"""
    event_date: date = Field(..., description="Specific date for the event occurrence")


class CalendarDateCreate(CalendarDateBase):
    """Schema for creating a new calendar date"""
    event_uuid: UUID = Field(..., description="UUID of the calendar event this date belongs to")


class CalendarDateUpdate(BaseModel):
    """Schema for updating calendar date information"""
    event_date: Optional[date] = None


class CalendarDateResponse(CalendarDateBase):
    """Schema for calendar date response"""
    id: UUID
    event_uuid: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CalendarEventWithDatesResponse(CalendarEventBase):
    """Schema for calendar event response with related dates"""
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    dates: List[CalendarDateResponse] = []

    model_config = ConfigDict(from_attributes=True)
