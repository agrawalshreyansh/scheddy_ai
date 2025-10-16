from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date
from uuid import UUID

from db.database import get_db
from events.enums import PriorityTag
from events.schemas import (
    CalendarEventCreate, CalendarEventUpdate, CalendarEventResponse,
    CalendarDateCreate, CalendarDateUpdate, CalendarDateResponse,
    CalendarEventWithDatesResponse
)
from events.controllers import (
    create_calendar_event,
    get_calendar_event,
    get_calendar_events,
    get_events_by_date_range,
    update_calendar_event,
    delete_calendar_event,
    create_calendar_date,
    get_calendar_date,
    get_calendar_dates_by_event,
    get_calendar_dates_by_date_range,
    update_calendar_date,
    delete_calendar_date
)

router = APIRouter(
    prefix="/calendar",
    tags=["calendar"],
    responses={404: {"description": "Not found"}},
)


@router.post("/events", response_model=CalendarEventResponse, status_code=status.HTTP_201_CREATED)
def create_event(
    event: CalendarEventCreate,
    db: Session = Depends(get_db)
):
    """Create a new calendar event"""
    # Validate that end_time is after start_time
    if event.end_time <= event.start_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End time must be after start time"
        )
    return create_calendar_event(db=db, event=event)


@router.get("/events/{event_id}", response_model=CalendarEventResponse)
def read_event(event_id: UUID, db: Session = Depends(get_db)):
    """Get a specific calendar event by ID"""
    db_event = get_calendar_event(db=db, event_id=event_id)
    if db_event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calendar event not found"
        )
    return db_event


@router.get("/events", response_model=List[CalendarEventResponse])
def read_events(
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[UUID] = Query(None, description="Filter by user ID"),
    db: Session = Depends(get_db)
):
    """Get list of calendar events"""
    events = get_calendar_events(db=db, skip=skip, limit=limit, user_id=user_id)
    return events


@router.get("/events/range/", response_model=List[CalendarEventResponse])
def read_events_by_range(
    start_date: datetime = Query(..., description="Start of date range"),
    end_date: datetime = Query(..., description="End of date range"),
    user_id: Optional[UUID] = Query(None, description="Filter by user ID"),
    db: Session = Depends(get_db)
):
    """Get calendar events within a date range"""
    if end_date <= start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date must be after start date"
        )
    events = get_events_by_date_range(
        db=db, 
        start_date=start_date, 
        end_date=end_date, 
        user_id=user_id
    )
    return events


@router.put("/events/{event_id}", response_model=CalendarEventResponse)
def update_event(
    event_id: UUID,
    event: CalendarEventUpdate,
    db: Session = Depends(get_db)
):
    """Update a calendar event"""
    db_event = update_calendar_event(db=db, event_id=event_id, event_update=event)
    if db_event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calendar event not found"
        )
    return db_event


@router.delete("/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(event_id: UUID, db: Session = Depends(get_db)):
    """Delete a calendar event"""
    success = delete_calendar_event(db=db, event_id=event_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calendar event not found"
        )
    return None


@router.get("/events/priority/{priority_tag}", response_model=List[CalendarEventResponse])
def read_events_by_priority(
    priority_tag: PriorityTag,
    user_id: Optional[UUID] = Query(None, description="Filter by user ID"),
    db: Session = Depends(get_db)
):
    """Get calendar events filtered by priority tag"""
    from events.models import CalendarEvent
    query = db.query(CalendarEvent).filter(CalendarEvent.priority_tag == priority_tag)
    if user_id:
        query = query.filter(CalendarEvent.user_id == user_id)
    events = query.all()
    return events


# Calendar Date Endpoints

@router.post("/dates", response_model=CalendarDateResponse, status_code=status.HTTP_201_CREATED)
def create_date(
    calendar_date: CalendarDateCreate,
    db: Session = Depends(get_db)
):
    """Create a new calendar date for an event"""
    # Verify that the event exists
    event = get_calendar_event(db=db, event_id=calendar_date.event_uuid)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calendar event not found"
        )
    return create_calendar_date(db=db, calendar_date=calendar_date)


@router.get("/dates/{date_id}", response_model=CalendarDateResponse)
def read_date(date_id: UUID, db: Session = Depends(get_db)):
    """Get a specific calendar date by ID"""
    db_date = get_calendar_date(db=db, date_id=date_id)
    if db_date is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calendar date not found"
        )
    return db_date


@router.get("/events/{event_id}/dates", response_model=List[CalendarDateResponse])
def read_dates_by_event(event_id: UUID, db: Session = Depends(get_db)):
    """Get all dates for a specific calendar event"""
    # Verify that the event exists
    event = get_calendar_event(db=db, event_id=event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calendar event not found"
        )
    dates = get_calendar_dates_by_event(db=db, event_uuid=event_id)
    return dates


@router.get("/dates/range/", response_model=List[CalendarDateResponse])
def read_dates_by_range(
    start_date: date = Query(..., description="Start of date range"),
    end_date: date = Query(..., description="End of date range"),
    event_uuid: Optional[UUID] = Query(None, description="Filter by event UUID"),
    db: Session = Depends(get_db)
):
    """Get calendar dates within a date range"""
    if end_date < start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date must be on or after start date"
        )
    dates = get_calendar_dates_by_date_range(
        db=db,
        start_date=start_date,
        end_date=end_date,
        event_uuid=event_uuid
    )
    return dates


@router.put("/dates/{date_id}", response_model=CalendarDateResponse)
def update_date(
    date_id: UUID,
    date_update: CalendarDateUpdate,
    db: Session = Depends(get_db)
):
    """Update a calendar date"""
    db_date = update_calendar_date(db=db, date_id=date_id, date_update=date_update)
    if db_date is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calendar date not found"
        )
    return db_date


@router.delete("/dates/{date_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_date(date_id: UUID, db: Session = Depends(get_db)):
    """Delete a calendar date"""
    success = delete_calendar_date(db=db, date_id=date_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calendar date not found"
        )
    return None


@router.get("/events/{event_id}/with-dates", response_model=CalendarEventWithDatesResponse)
def read_event_with_dates(event_id: UUID, db: Session = Depends(get_db)):
    """Get a calendar event with all its related dates"""
    db_event = get_calendar_event(db=db, event_id=event_id)
    if db_event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calendar event not found"
        )
    return db_event
