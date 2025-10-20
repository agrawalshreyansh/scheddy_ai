from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date, timezone, time
from uuid import UUID
from events.models import CalendarEvent, CalendarDate
from events.schemas import CalendarEventCreate, CalendarEventUpdate, CalendarDateCreate, CalendarDateUpdate


def create_calendar_event(db: Session, event: CalendarEventCreate) -> CalendarEvent:
    """Create a new calendar event"""
    db_event = CalendarEvent(
        task_title=event.task_title,
        description=event.description,
        start_time=event.start_time,
        end_time=event.end_time,
        priority_number=event.priority_number,
        priority_tag=event.priority_tag,
        user_id=event.user_id
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


def get_calendar_event(db: Session, event_id: UUID) -> Optional[CalendarEvent]:
    """Get a calendar event by ID"""
    return db.query(CalendarEvent).filter(CalendarEvent.id == event_id).first()


def get_calendar_events(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    user_id: Optional[UUID] = None
) -> List[CalendarEvent]:
    """Get list of calendar events with optional filtering by user"""
    query = db.query(CalendarEvent)
    if user_id:
        query = query.filter(CalendarEvent.user_id == user_id)
    return query.offset(skip).limit(limit).all()


def get_events_by_date_range(
    db: Session,
    start_date: datetime,
    end_date: datetime,
    user_id: Optional[UUID] = None
) -> List[CalendarEvent]:
    """Get events within a date range"""
    query = db.query(CalendarEvent).filter(
        CalendarEvent.start_time >= start_date,
        CalendarEvent.end_time <= end_date
    )
    if user_id:
        query = query.filter(CalendarEvent.user_id == user_id)
    return query.all()


def update_calendar_event(
    db: Session, 
    event_id: UUID, 
    event_update: CalendarEventUpdate
) -> Optional[CalendarEvent]:
    """Update a calendar event"""
    db_event = db.query(CalendarEvent).filter(CalendarEvent.id == event_id).first()
    if not db_event:
        return None
    
    update_data = event_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_event, field, value)
    
    db.commit()
    db.refresh(db_event)
    return db_event


def delete_calendar_event(db: Session, event_id: UUID) -> bool:
    """Delete a calendar event"""
    db_event = db.query(CalendarEvent).filter(CalendarEvent.id == event_id).first()
    if not db_event:
        return False
    
    db.delete(db_event)
    db.commit()
    return True


# Calendar Date Controllers

def create_calendar_date(db: Session, calendar_date: CalendarDateCreate) -> CalendarDate:
    """Create a new calendar date"""
    db_date = CalendarDate(
        event_date=calendar_date.event_date,
        event_uuid=calendar_date.event_uuid
    )
    db.add(db_date)
    db.commit()
    db.refresh(db_date)
    return db_date


def get_calendar_date(db: Session, date_id: UUID) -> Optional[CalendarDate]:
    """Get a calendar date by ID"""
    return db.query(CalendarDate).filter(CalendarDate.id == date_id).first()


def get_calendar_dates_by_event(db: Session, event_uuid: UUID) -> List[CalendarDate]:
    """Get all dates for a specific calendar event"""
    return db.query(CalendarDate).filter(CalendarDate.event_uuid == event_uuid).all()


def get_calendar_dates_by_date_range(
    db: Session,
    start_date: date,
    end_date: date,
    event_uuid: Optional[UUID] = None
) -> List[CalendarDate]:
    """Get calendar dates within a date range, optionally filtered by event"""
    query = db.query(CalendarDate).filter(
        CalendarDate.event_date >= start_date,
        CalendarDate.event_date <= end_date
    )
    if event_uuid:
        query = query.filter(CalendarDate.event_uuid == event_uuid)
    return query.all()


def update_calendar_date(
    db: Session,
    date_id: UUID,
    date_update: CalendarDateUpdate
) -> Optional[CalendarDate]:
    """Update a calendar date"""
    db_date = db.query(CalendarDate).filter(CalendarDate.id == date_id).first()
    if not db_date:
        return None
    
    update_data = date_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_date, field, value)
    
    db.commit()
    db.refresh(db_date)
    return db_date


def delete_calendar_date(db: Session, date_id: UUID) -> bool:
    """Delete a calendar date"""
    db_date = db.query(CalendarDate).filter(CalendarDate.id == date_id).first()
    if not db_date:
        return False
    
    db.delete(db_date)
    db.commit()
    return True


# Conflict Detection and Scheduling Helpers

def check_time_slot_conflict(
    db: Session,
    user_id: UUID,
    start_time: datetime,
    end_time: datetime,
    exclude_event_id: Optional[UUID] = None
) -> bool:
    """
    Check if a proposed time slot conflicts with existing events
    
    Args:
        db: Database session
        user_id: User UUID
        start_time: Proposed start time
        end_time: Proposed end time
        exclude_event_id: Event ID to exclude from check (useful for updates)
    
    Returns:
        True if there's a conflict, False otherwise
    """
    query = db.query(CalendarEvent).filter(
        CalendarEvent.user_id == user_id,
        CalendarEvent.start_time < end_time,
        CalendarEvent.end_time > start_time
    )
    
    if exclude_event_id:
        query = query.filter(CalendarEvent.id != exclude_event_id)
    
    return query.count() > 0


def get_conflicting_events(
    db: Session,
    user_id: UUID,
    start_time: datetime,
    end_time: datetime
) -> List[CalendarEvent]:
    """
    Get all events that conflict with a proposed time slot
    
    Args:
        db: Database session
        user_id: User UUID
        start_time: Proposed start time
        end_time: Proposed end time
    
    Returns:
        List of conflicting CalendarEvent objects
    """
    return db.query(CalendarEvent).filter(
        CalendarEvent.user_id == user_id,
        CalendarEvent.start_time < end_time,
        CalendarEvent.end_time > start_time
    ).order_by(CalendarEvent.start_time).all()


def find_next_available_slot(
    db: Session,
    user_id: UUID,
    duration_minutes: int,
    start_search_from: datetime,
    max_days_ahead: int = 7,
    working_hours_start: int = 9,
    working_hours_end: int = 18
) -> Optional[tuple[datetime, datetime]]:
    """
    Find the next available time slot that can accommodate the given duration
    
    Args:
        db: Database session
        user_id: User UUID
        duration_minutes: Required duration in minutes
        start_search_from: Start searching from this datetime
        max_days_ahead: Maximum number of days to search ahead
        working_hours_start: Start of working hours (hour, 0-23)
        working_hours_end: End of working hours (hour, 0-23)
    
    Returns:
        Tuple of (start_time, end_time) or None if no slot found
    """
    from datetime import time, timedelta
    
    current_date = start_search_from.date()
    end_search_date = current_date + timedelta(days=max_days_ahead)
    
    while current_date <= end_search_date:
        day_start = datetime.combine(current_date, time(working_hours_start, 0), tzinfo=timezone.utc)
        day_end = datetime.combine(current_date, time(working_hours_end, 0), tzinfo=timezone.utc)
        
        # Get events for this day
        events = get_events_by_date_range(db, day_start, day_end, user_id=user_id)
        
        # If no events, the whole day is available
        if not events:
            return (day_start, day_start + timedelta(minutes=duration_minutes))
        
        # Check gaps between events
        current_time = day_start
        for event in sorted(events, key=lambda e: e.start_time if e.start_time else day_start):
            # Skip events with invalid times
            if not event.start_time or not event.end_time:
                continue
                
            if current_time < event.start_time:
                gap_duration = (event.start_time - current_time).total_seconds() / 60
                if duration_minutes is not None and gap_duration >= duration_minutes:
                    return (current_time, current_time + timedelta(minutes=duration_minutes))
            current_time = max(current_time, event.end_time)
        
        # Check if there's time at the end of the day
        if current_time < day_end:
            remaining_duration = (day_end - current_time).total_seconds() / 60
            if duration_minutes is not None and remaining_duration >= duration_minutes:
                return (current_time, current_time + timedelta(minutes=duration_minutes))
        
        # Move to next day
        current_date += timedelta(days=1)
    
    return None


def get_events_by_priority(
    db: Session,
    user_id: UUID,
    min_priority: Optional[int] = None,
    max_priority: Optional[int] = None,
    skip: int = 0,
    limit: int = 100
) -> List[CalendarEvent]:
    """
    Get events filtered by priority range
    
    Args:
        db: Database session
        user_id: User UUID
        min_priority: Minimum priority number (inclusive)
        max_priority: Maximum priority number (inclusive)
        skip: Number of records to skip
        limit: Maximum number of records to return
    
    Returns:
        List of CalendarEvent objects
    """
    query = db.query(CalendarEvent).filter(CalendarEvent.user_id == user_id)
    
    if min_priority is not None:
        query = query.filter(CalendarEvent.priority_number >= min_priority)
    
    if max_priority is not None:
        query = query.filter(CalendarEvent.priority_number <= max_priority)
    
    return query.order_by(CalendarEvent.priority_number.desc()).offset(skip).limit(limit).all()

