"""
Intelligent Scheduling Engine
Handles automatic time slot finding, conflict resolution, and priority-based rescheduling
"""
from datetime import datetime, timedelta, time, timezone
from typing import List, Optional, Tuple, Dict
from sqlalchemy.orm import Session
from uuid import UUID
from events.models import CalendarEvent
from events.enums import PriorityTag


class CalendarScheduler:
    """
    Core scheduling engine with:
    - Smart time slot finding
    - Priority-based scheduling
    - Auto-rescheduling of lower-priority tasks
    - Conflict detection and resolution
    """
    
    # Working hours configuration
    WORK_START_HOUR = 9
    WORK_END_HOUR = 18
    LUNCH_START_HOUR = 12
    LUNCH_DURATION_MINUTES = 60
    
    # Protected priorities - NEVER reschedule these
    PROTECTED_PRIORITIES = [9, 10]  # Urgent and Critical tasks
    
    # Priority mapping
    PRIORITY_MAP = {
        PriorityTag.URGENT: 10,
        PriorityTag.HIGH: 8,
        PriorityTag.MEDIUM: 5,
        PriorityTag.LOW: 3,
        PriorityTag.OPTIONAL: 1
    }
    
    def __init__(self, db: Session, user_datetime: Optional[datetime] = None):
        self.db = db
        # Store user_datetime for use in scheduling
        if user_datetime is None:
            user_datetime = datetime.now(timezone.utc)
        elif user_datetime.tzinfo is None:
            user_datetime = user_datetime.replace(tzinfo=timezone.utc)
        self.user_datetime = user_datetime
    
    def parse_duration(self, duration_str: str) -> int:
        """
        Parse duration string like "2h", "30m", "1h30m" into total minutes
        
        Returns:
            Total minutes (defaults to 30 if parsing fails)
        """
        if not duration_str:
            return 30
        
        # Ensure duration_str is a string
        if not isinstance(duration_str, str):
            duration_str = str(duration_str)
        
        duration_str = duration_str.lower().strip()
        total_minutes = 0
        
        # Parse hours
        if 'h' in duration_str:
            parts = duration_str.split('h')
            try:
                hours = int(parts[0])
                total_minutes += hours * 60
                duration_str = parts[1] if len(parts) > 1 else ''
            except ValueError:
                pass
        
        # Parse minutes
        if 'm' in duration_str:
            minutes_str = duration_str.replace('m', '').strip()
            if minutes_str:
                try:
                    total_minutes += int(minutes_str)
                except ValueError:
                    pass
        
        # Default to 30 minutes if parsing fails
        return total_minutes if total_minutes > 0 else 30
    
    def get_priority_number_from_tag(self, priority_tag: str) -> Tuple[int, PriorityTag]:
        """
        Convert priority tag string to priority number and PriorityTag enum
        
        Args:
            priority_tag: String like "high", "medium", "low", "urgent", "optional"
        
        Returns:
            Tuple of (priority_number, PriorityTag)
        """
        # Ensure priority_tag is a string
        if not isinstance(priority_tag, str):
            priority_tag = str(priority_tag)
            
        priority_tag_lower = priority_tag.lower().strip()
        
        if priority_tag_lower == "urgent":
            return (10, PriorityTag.URGENT)
        elif priority_tag_lower == "high":
            return (8, PriorityTag.HIGH)
        elif priority_tag_lower in ["medium", "med"]:
            return (5, PriorityTag.MEDIUM)
        elif priority_tag_lower == "low":
            return (3, PriorityTag.LOW)
        elif priority_tag_lower == "optional":
            return (1, PriorityTag.OPTIONAL)
        else:
            # Default to medium
            return (5, PriorityTag.MEDIUM)
    
    def get_user_events_in_range(
        self,
        user_id: UUID,
        start_date: datetime,
        end_date: datetime
    ) -> List[CalendarEvent]:
        """
        Get all events for a user within a date range, ordered by start time
        """
        return self.db.query(CalendarEvent).filter(
            CalendarEvent.user_id == user_id,
            CalendarEvent.start_time >= start_date,
            CalendarEvent.start_time < end_date
        ).order_by(CalendarEvent.start_time).all()
    
    def find_available_slots(
        self,
        user_id: UUID,
        date: datetime,
        duration_minutes: int,
        working_hours_only: bool = True
    ) -> List[Tuple[datetime, datetime]]:
        """
        Find all available time slots on a given date
        
        Args:
            user_id: User UUID
            date: Target date to find slots on
            duration_minutes: Required duration in minutes
            working_hours_only: Only find slots during working hours
        
        Returns:
            List of (start_time, end_time) tuples for available slots
        """
        # Set up the day boundaries (timezone-aware)
        start_of_day = datetime.combine(date.date(), time(self.WORK_START_HOUR, 0), tzinfo=timezone.utc)
        end_of_day = datetime.combine(date.date(), time(self.WORK_END_HOUR, 0), tzinfo=timezone.utc)
        
        # Get all events for this day
        events = self.get_user_events_in_range(user_id, start_of_day, end_of_day)
        
        available_slots = []
        current_time = start_of_day
        
        for event in events:
            # Check if there's a gap before this event
            event_start = event.start_time
            
            # Skip events with invalid times
            if not event_start or not event.end_time:
                continue
            
            if current_time < event_start:
                gap_duration = (event_start - current_time).total_seconds() / 60
                if duration_minutes is not None and gap_duration >= duration_minutes:
                    available_slots.append((current_time, event_start))
            
            # Move current_time to after this event
            current_time = max(current_time, event.end_time)
        
        # Check if there's time at the end of the day
        if current_time < end_of_day:
            gap_duration = (end_of_day - current_time).total_seconds() / 60
            if duration_minutes is not None and gap_duration >= duration_minutes:
                available_slots.append((current_time, end_of_day))
        
        return available_slots
    
    def find_best_slot(
        self,
        user_id: UUID,
        duration_minutes: int,
        preferred_date: Optional[datetime] = None,
        max_days_ahead: int = 7
    ) -> Optional[Tuple[datetime, datetime]]:
        """
        Find the best available time slot
        
        Args:
            user_id: User UUID
            duration_minutes: Required duration in minutes
            preferred_date: Preferred date (defaults to today)
            max_days_ahead: Maximum days to look ahead
        
        Returns:
            Tuple of (start_time, end_time) or None if no slot found
        """
        if preferred_date is None:
            preferred_date = self.user_datetime
        
        # Try to find a slot starting from preferred date
        for day_offset in range(max_days_ahead):
            check_date = preferred_date + timedelta(days=day_offset)
            slots = self.find_available_slots(user_id, check_date, duration_minutes)
            
            if slots:
                # Return the first available slot
                slot_start, slot_end = slots[0]
                slot_end = slot_start + timedelta(minutes=duration_minutes)
                return (slot_start, slot_end)
        
        return None
    
    def has_conflict(
        self,
        user_id: UUID,
        start_time: datetime,
        end_time: datetime,
        exclude_event_id: Optional[UUID] = None
    ) -> bool:
        """
        Check if a time slot conflicts with existing events
        
        Args:
            user_id: User UUID
            start_time: Proposed start time
            end_time: Proposed end time
            exclude_event_id: Event ID to exclude from conflict check (for updates)
        
        Returns:
            True if there's a conflict, False otherwise
        """
        query = self.db.query(CalendarEvent).filter(
            CalendarEvent.user_id == user_id,
            CalendarEvent.start_time < end_time,
            CalendarEvent.end_time > start_time
        )
        
        if exclude_event_id:
            query = query.filter(CalendarEvent.id != exclude_event_id)
        
        conflicts = query.all()
        return len(conflicts) > 0
    
    def get_conflicting_events(
        self,
        user_id: UUID,
        start_time: datetime,
        end_time: datetime
    ) -> List[CalendarEvent]:
        """
        Get all events that conflict with a proposed time slot
        """
        return self.db.query(CalendarEvent).filter(
            CalendarEvent.user_id == user_id,
            CalendarEvent.start_time < end_time,
            CalendarEvent.end_time > start_time
        ).order_by(CalendarEvent.priority_number).all()
    
    def reschedule_lower_priority_events(
        self,
        user_id: UUID,
        new_event_start: datetime,
        new_event_end: datetime,
        new_event_priority: int,
        max_days_to_push: int = 30
    ) -> List[Dict]:
        """
        Reschedule lower-priority events to make room for a higher-priority event
        NEVER reschedules Priority 9-10 (Urgent/Critical) tasks.
        
        Args:
            user_id: User UUID
            new_event_start: Start time of the new high-priority event
            new_event_end: End time of the new high-priority event
            new_event_priority: Priority number of the new event
            max_days_to_push: Maximum days to push events into the future
        
        Returns:
            List of rescheduled events with old and new times
        """
        conflicting_events = self.get_conflicting_events(user_id, new_event_start, new_event_end)
        rescheduled = []
        
        for event in conflicting_events:
            # Only reschedule if the new event has higher priority
            if event.priority_number is not None and event.priority_number >= new_event_priority:
                continue
            
            # NEVER reschedule Priority 9-10 (Urgent/Critical) tasks
            if event.priority_number in self.PROTECTED_PRIORITIES:
                continue
            
            # Calculate the duration of the conflicting event
            event_duration = (event.end_time - event.start_time).total_seconds() / 60
            
            # Try to find a new slot for this event
            # Start looking from the day after the new event
            search_start = new_event_end.replace(hour=self.WORK_START_HOUR, minute=0, second=0)
            new_slot = self.find_best_slot(
                user_id,
                int(event_duration),
                preferred_date=search_start,
                max_days_ahead=max_days_to_push
            )
            
            if new_slot:
                old_start = event.start_time
                old_end = event.end_time
                
                # Update the event with new times
                event.start_time = new_slot[0]
                event.end_time = new_slot[1]
                self.db.commit()
                
                rescheduled.append({
                    'event_id': str(event.id),
                    'event_title': event.task_title,
                    'old_start': old_start.isoformat(),
                    'old_end': old_end.isoformat(),
                    'new_start': new_slot[0].isoformat(),
                    'new_end': new_slot[1].isoformat(),
                    'priority': event.priority_tag.value
                })
        
        return rescheduled
    
    def schedule_with_auto_reschedule(
        self,
        user_id: UUID,
        task_title: str,
        duration_minutes: int,
        priority_number: int,
        priority_tag: PriorityTag,
        preferred_date: Optional[datetime] = None,
        description: Optional[str] = None,
        force_today: bool = False
    ) -> Dict:
        """
        Schedule a new event, automatically rescheduling lower-priority events if needed
        
        Args:
            user_id: User UUID
            task_title: Title of the task
            duration_minutes: Duration in minutes
            priority_number: Priority number (1-10)
            priority_tag: Priority tag enum
            preferred_date: Preferred date/time (defaults to today)
            description: Event description
            force_today: Force scheduling today even if it requires rescheduling
        
        Returns:
            Dictionary with scheduling result and any rescheduled events
        """
        if preferred_date is None:
            preferred_date = self.user_datetime
        
        # First, try to find an available slot without conflicts
        best_slot = self.find_best_slot(
            user_id,
            duration_minutes,
            preferred_date=preferred_date,
            max_days_ahead=1 if force_today else 7
        )
        
        if best_slot:
            # No conflicts, schedule directly
            new_event = CalendarEvent(
                task_title=task_title,
                description=description,
                start_time=best_slot[0],
                end_time=best_slot[1],
                priority_number=priority_number,
                priority_tag=priority_tag,
                user_id=user_id
            )
            self.db.add(new_event)
            self.db.commit()
            self.db.refresh(new_event)
            
            return {
                'success': True,
                'event': new_event.to_dict(),
                'rescheduled_events': [],
                'message': f"Successfully scheduled '{task_title}' from {best_slot[0].strftime('%Y-%m-%d %H:%M')} to {best_slot[1].strftime('%H:%M')}"
            }
        
        # No available slot found, try to reschedule lower-priority events
        if priority_number is not None and (force_today or priority_number >= 7):  # High priority
            # Propose a time slot (first available hour in working hours)
            proposed_start = datetime.combine(
                preferred_date.date(),
                time(self.WORK_START_HOUR, 0),
                tzinfo=timezone.utc
            )
            
            # Find first potential slot
            day_start = datetime.combine(preferred_date.date(), time(self.WORK_START_HOUR, 0), tzinfo=timezone.utc)
            day_end = datetime.combine(preferred_date.date(), time(self.WORK_END_HOUR, 0), tzinfo=timezone.utc)
            events = self.get_user_events_in_range(user_id, day_start, day_end)
            
            if events:
                # Try to fit in gaps or at the end
                for i in range(len(events)):
                    if i == 0:
                        gap_start = day_start
                        gap_end = events[i].start_time
                    else:
                        gap_start = events[i-1].end_time
                        gap_end = events[i].start_time
                    
                    gap_minutes = (gap_end - gap_start).total_seconds() / 60
                    if duration_minutes is not None and gap_minutes >= duration_minutes:
                        proposed_start = gap_start
                        break
                else:
                    # Try end of day
                    if events:
                        proposed_start = max(events[-1].end_time, day_start)
            
            proposed_end = proposed_start + timedelta(minutes=duration_minutes)
            
            # Reschedule conflicting lower-priority events
            rescheduled = self.reschedule_lower_priority_events(
                user_id,
                proposed_start,
                proposed_end,
                priority_number
            )
            
            # Now create the event
            new_event = CalendarEvent(
                task_title=task_title,
                description=description,
                start_time=proposed_start,
                end_time=proposed_end,
                priority_number=priority_number,
                priority_tag=priority_tag,
                user_id=user_id
            )
            self.db.add(new_event)
            self.db.commit()
            self.db.refresh(new_event)
            
            return {
                'success': True,
                'event': new_event.to_dict(),
                'rescheduled_events': rescheduled,
                'message': f"Scheduled '{task_title}' from {proposed_start.strftime('%Y-%m-%d %H:%M')} to {proposed_end.strftime('%H:%M')}. Rescheduled {len(rescheduled)} lower-priority events."
            }
        
        # Cannot schedule
        return {
            'success': False,
            'event': None,
            'rescheduled_events': [],
            'message': f"Could not find a suitable time slot for '{task_title}'. Calendar is fully booked."
        }
