"""
Enhanced Smart Scheduler with User Preferences and Weekly Context
"""
from datetime import datetime, timedelta, time, timezone
from zoneinfo import ZoneInfo
from typing import List, Optional, Tuple, Dict
from sqlalchemy.orm import Session
from uuid import UUID
from events.models import CalendarEvent
from events.enums import PriorityTag
from users.preferences import UserPreference
from users.preference_controllers import (
    get_or_create_user_preference,
    get_week_start_end,
    get_weekly_goal_status,
    get_remaining_goal_tasks
)


class SmartScheduler:
    """
    Enhanced scheduler with:
    - User preferences support
    - Weekly goal tracking
    - Full week context awareness
    - Smart rescheduling across the week
    - Weekend scheduling
    """
    
    # Protected priorities - NEVER reschedule these
    PROTECTED_PRIORITIES = [9, 10]  # Urgent and Critical tasks
    
    def __init__(self, db: Session, user_id: UUID, user_datetime: Optional[datetime] = None, user_timezone: Optional[str] = None):
        self.db = db
        self.user_id = user_id
        self.preference = get_or_create_user_preference(db, user_id)
        
        # Store user timezone (default to UTC if not provided)
        self.user_timezone = ZoneInfo(user_timezone) if user_timezone else timezone.utc
        
        # Store user_datetime for use in scheduling
        if user_datetime is None:
            # Create datetime in user's timezone
            user_datetime = datetime.now(self.user_timezone)
        elif user_datetime.tzinfo is None:
            # If naive datetime provided, assume it's in user's timezone
            user_datetime = user_datetime.replace(tzinfo=self.user_timezone)
        else:
            # Convert to user's timezone if it's in different timezone
            user_datetime = user_datetime.astimezone(self.user_timezone)
        
        self.user_datetime = user_datetime
    
    def parse_duration(self, duration_str: str) -> int:
        """
        Parse duration string like '2h', '30m', '1h30m' into minutes
        
        Args:
            duration_str: Duration string
            
        Returns:
            Total minutes
        """
        if not duration_str:
            return 60  # Default: 1 hour
        
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
        
        # Default to 60 minutes if parsing fails
        return total_minutes if total_minutes > 0 else 60
    
    def parse_time_string(self, time_str: str, reference_date: datetime) -> Optional[datetime]:
        """
        Parse time string like '2pm', '14:00', '9:30am' into a datetime
        
        Args:
            time_str: Time string
            reference_date: Date to apply the time to
            
        Returns:
            Datetime in user's timezone or None if parsing fails
        """
        if not time_str:
            return None
        
        time_str = time_str.lower().strip()
        hour = 0
        minute = 0
        
        try:
            # Handle formats like "2pm", "2:30pm", "14:00"
            if 'pm' in time_str or 'am' in time_str:
                is_pm = 'pm' in time_str
                time_str = time_str.replace('pm', '').replace('am', '').strip()
                
                if ':' in time_str:
                    parts = time_str.split(':')
                    hour = int(parts[0])
                    minute = int(parts[1]) if len(parts) > 1 else 0
                else:
                    hour = int(time_str)
                    minute = 0
                
                # Convert to 24-hour format
                if is_pm and hour != 12:
                    hour += 12
                elif not is_pm and hour == 12:
                    hour = 0
            else:
                # Handle 24-hour format like "14:00"
                if ':' in time_str:
                    parts = time_str.split(':')
                    hour = int(parts[0])
                    minute = int(parts[1]) if len(parts) > 1 else 0
                else:
                    hour = int(time_str)
                    minute = 0
            
            # Create datetime in user's timezone
            result = reference_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # Ensure it's in user's timezone
            if result.tzinfo is None:
                result = result.replace(tzinfo=self.user_timezone)
            else:
                result = result.astimezone(self.user_timezone)
            
            return result
        except (ValueError, AttributeError):
            return None
    
    def get_priority_number_from_tag(self, priority_tag: str) -> Tuple[int, PriorityTag]:
        """Convert priority tag string to priority number and enum"""
        # Ensure priority_tag is a string
        if not isinstance(priority_tag, str):
            priority_tag = str(priority_tag)
            
        priority_tag_lower = priority_tag.lower().strip()
        
        mapping = {
            "urgent": (10, PriorityTag.URGENT),
            "high": (8, PriorityTag.HIGH),
            "medium": (5, PriorityTag.MEDIUM),
            "med": (5, PriorityTag.MEDIUM),
            "low": (3, PriorityTag.LOW),
            "optional": (1, PriorityTag.OPTIONAL)
        }
        
        return mapping.get(priority_tag_lower, (5, PriorityTag.MEDIUM))
    
    def get_next_weekend(self, from_date: datetime = None) -> Tuple[datetime, datetime]:
        """
        Get the next weekend (Saturday and Sunday) in user's timezone
        
        Returns:
            Tuple of (saturday_start, sunday_end) in UTC for database storage
        """
        if from_date is None:
            from_date = self.user_datetime
        
        # Ensure from_date is a datetime object
        if not isinstance(from_date, datetime):
            raise TypeError(f"Expected datetime object for from_date, got {type(from_date).__name__}")
        
        # Ensure from_date is in user's timezone
        if from_date.tzinfo is None:
            from_date = from_date.replace(tzinfo=self.user_timezone)
        else:
            from_date = from_date.astimezone(self.user_timezone)
        
        # Find next Saturday
        days_until_saturday = (5 - from_date.weekday()) % 7
        if days_until_saturday == 0 and from_date.hour >= 18:
            # If it's Saturday evening, go to next weekend
            days_until_saturday = 7
        
        saturday = from_date + timedelta(days=days_until_saturday)
        saturday_start = saturday.replace(hour=10, minute=0, second=0, microsecond=0)
        
        sunday = saturday + timedelta(days=1)
        sunday_end = sunday.replace(hour=20, minute=0, second=0, microsecond=0)
        
        # Convert to UTC for database storage
        return (saturday_start.astimezone(timezone.utc), sunday_end.astimezone(timezone.utc))
    
    def is_work_day(self, date: datetime) -> bool:
        """Check if date is a work day based on user preference"""
        return self.preference.is_work_day(date.weekday())
    
    def is_weekend_day(self, date: datetime) -> bool:
        """Check if date is a weekend day"""
        return self.preference.is_weekend(date.weekday())
    
    def get_available_hours_in_day(self, date: datetime) -> Tuple[datetime, datetime]:
        """
        Get available hours for a specific day based on user preference
        
        Returns:
            Tuple of (day_start, day_end) in user's timezone
        """
        # Ensure date is a datetime object
        if not isinstance(date, datetime):
            raise TypeError(f"Expected datetime object, got {type(date).__name__}")
        
        # Ensure date is in user's timezone
        if date.tzinfo is None:
            date = date.replace(tzinfo=self.user_timezone)
        else:
            date = date.astimezone(self.user_timezone)
            
        work_start_hour, work_end_hour = self.preference.get_work_hours()
        
        # Weekend has different hours
        if self.is_weekend_day(date):
            day_start = datetime.combine(date.date(), time(10, 0), tzinfo=self.user_timezone)
            day_end = datetime.combine(date.date(), time(20, 0), tzinfo=self.user_timezone)
        else:
            day_start = datetime.combine(date.date(), time(work_start_hour, 0), tzinfo=self.user_timezone)
            day_end = datetime.combine(date.date(), time(work_end_hour, 0), tzinfo=self.user_timezone)
        
        # Convert to UTC for database storage
        return (day_start.astimezone(timezone.utc), day_end.astimezone(timezone.utc))
    
    def get_week_events(self, week_identifier: str = None) -> List[CalendarEvent]:
        """Get all events for the week"""
        week_start, week_end = get_week_start_end(week_identifier)
        
        events = self.db.query(CalendarEvent).filter(
            CalendarEvent.user_id == self.user_id,
            CalendarEvent.start_time >= week_start,
            CalendarEvent.start_time < week_end,
            CalendarEvent.start_time.isnot(None),
            CalendarEvent.end_time.isnot(None)
        ).order_by(CalendarEvent.start_time).all()
        
        return events
    
    def get_day_events(self, date: datetime) -> List[CalendarEvent]:
        """Get all events for a specific day"""
        day_start, day_end = self.get_available_hours_in_day(date)
        
        events = self.db.query(CalendarEvent).filter(
            CalendarEvent.user_id == self.user_id,
            CalendarEvent.start_time >= day_start,
            CalendarEvent.start_time < day_end,
            CalendarEvent.start_time.isnot(None),
            CalendarEvent.end_time.isnot(None)
        ).order_by(CalendarEvent.start_time).all()
        
        return events
    
    def find_best_slot_in_week(
        self,
        duration_minutes: int,
        priority_number: int,
        preferred_days: List[str] = None,
        exclude_weekends: bool = False
    ) -> Optional[Tuple[datetime, datetime]]:
        """
        Find best available slot in the current week with full context
        
        Args:
            duration_minutes: Required duration
            priority_number: Priority of the task
            preferred_days: List of day names like ["monday", "tuesday", "weekend"]
            exclude_weekends: Don't schedule on weekends
        
        Returns:
            Tuple of (start_time, end_time) or None
        """
        week_start, week_end = get_week_start_end()
        
        # Get all events this week for context
        week_events = self.get_week_events()
        
        # Build list of days to check
        current_date = max(self.user_datetime, week_start)
        days_to_check = []
        
        while current_date < week_end:
            day_of_week = current_date.weekday()
            is_weekend = self.is_weekend_day(current_date)
            
            # Check if we should include this day
            should_include = True
            
            if exclude_weekends and is_weekend:
                should_include = False
            
            if preferred_days:
                day_name = current_date.strftime("%A").lower()
                if day_name not in [d.lower() for d in preferred_days] and "weekend" not in [d.lower() for d in preferred_days]:
                    should_include = False
                elif "weekend" in [d.lower() for d in preferred_days] and not is_weekend:
                    should_include = False
            
            if should_include and (is_weekend or self.is_work_day(current_date)):
                days_to_check.append(current_date)
            
            current_date += timedelta(days=1)
        
        # Score each potential slot
        best_slot = None
        best_score = -1
        
        for day in days_to_check:
            slots = self.find_slots_in_day(day, duration_minutes)
            
            for slot_start, slot_end in slots:
                score = self.score_time_slot(slot_start, priority_number, week_events)
                
                if score > best_score:
                    best_score = score
                    best_slot = (slot_start, slot_end)
        
        return best_slot
    
    def find_slots_in_day(
        self,
        date: datetime,
        duration_minutes: int
    ) -> List[Tuple[datetime, datetime]]:
        """Find all available slots in a specific day"""
        day_start, day_end = self.get_available_hours_in_day(date)
        events = self.get_day_events(date)
        
        available_slots = []
        current_time = max(day_start, self.user_datetime)
        
        # Add buffer for lunch break - ensure lunch_break_start is a time object
        lunch_break_start_time = self.preference.lunch_break_start if isinstance(self.preference.lunch_break_start, time) else time(12, 0)
        lunch_start = datetime.combine(date.date(), lunch_break_start_time, tzinfo=timezone.utc)
        lunch_end = lunch_start + timedelta(minutes=self.preference.lunch_break_duration if self.preference.lunch_break_duration else 60)
        
        for event in events:
            # Skip events with invalid times
            if not event.start_time or not event.end_time:
                continue
                
            # Check gap before this event
            if current_time < event.start_time:
                # Skip lunch break
                if not (current_time <= lunch_start < event.start_time):
                    gap_duration = (event.start_time - current_time).total_seconds() / 60
                    if duration_minutes is not None and gap_duration >= duration_minutes:
                        available_slots.append((current_time, event.start_time))
            
            current_time = max(current_time, event.end_time)
            
            # Add break time
            if self.preference.min_break_between_tasks > 0:
                current_time += timedelta(minutes=self.preference.min_break_between_tasks)
        
        # Check end of day
        if current_time < day_end:
            gap_duration = (day_end - current_time).total_seconds() / 60
            if duration_minutes is not None and gap_duration >= duration_minutes:
                available_slots.append((current_time, day_end))
        
        return available_slots
    
    def score_time_slot(
        self,
        slot_start: datetime,
        priority_number: int,
        week_events: List[CalendarEvent]
    ) -> float:
        """
        Score a time slot based on various factors
        Higher score = better slot
        """
        score = 100.0
        
        # Prefer morning if user prefers morning
        if self.preference.prefer_morning:
            if slot_start.hour < 12:
                score += 20
            elif slot_start.hour >= 15:
                score -= 10
        
        # Check day load (prefer less busy days)
        day_events = [e for e in week_events if e.start_time and e.start_time.date() == slot_start.date()]
        day_load = len(day_events)
        
        if day_load < 3:
            score += 15
        elif day_load > 6:
            score -= 15
        
        # Prefer weekdays for high priority
        if priority_number is not None and priority_number >= 7 and not self.is_weekend_day(slot_start):
            score += 10
        
        # Slight penalty for weekend for non-leisure tasks
        if priority_number is not None and self.is_weekend_day(slot_start) and priority_number >= 7:
            score -= 5
        
        return score
    
    def schedule_with_context(
        self,
        task_title: str,
        duration_minutes: int,
        priority_number: int,
        priority_tag: PriorityTag,
        when: str = None,
        description: Optional[str] = None,
        category: Optional[str] = None,
        preferred_time: Optional[str] = None
    ) -> Dict:
        """
        Schedule a task with full week context
        
        Args:
            task_title: Task title
            duration_minutes: Duration in minutes
            priority_number: Priority 1-10
            priority_tag: Priority enum
            when: "today", "tomorrow", "weekend", "this_week"
            description: Task description
            category: Task category for goal tracking
            preferred_time: Preferred start time (e.g., "2pm", "14:00", "9:30am")
        
        Returns:
            Dict with scheduling result
        """
        # Determine preferred days and handle preferred time
        preferred_days = None
        exclude_weekends = False
        force_today = False
        specific_start_time = None
        
        # Determine the reference date for the event
        reference_date = self.user_datetime
        if when == "today":
            preferred_days = [self.user_datetime.strftime("%A")]
            force_today = True
            reference_date = self.user_datetime
        elif when == "tomorrow":
            tomorrow = self.user_datetime + timedelta(days=1)
            preferred_days = [tomorrow.strftime("%A")]
            reference_date = tomorrow
        elif when == "weekend":
            preferred_days = ["weekend"]
        elif when == "this_week":
            # Any day this week
            pass
        
        # If user specified a preferred time, try to schedule at that exact time
        if preferred_time:
            specific_start_time = self.parse_time_string(preferred_time, reference_date)
            
            if specific_start_time:
                # Convert to UTC for database query
                specific_start_time_utc = specific_start_time.astimezone(timezone.utc)
                specific_end_time_utc = specific_start_time_utc + timedelta(minutes=duration_minutes)
                
                # Check if this specific time slot is available
                conflicting_events = self.db.query(CalendarEvent).filter(
                    CalendarEvent.user_id == self.user_id,
                    CalendarEvent.start_time < specific_end_time_utc,
                    CalendarEvent.end_time > specific_start_time_utc
                ).all()
                
                if not conflicting_events:
                    # The requested time is available! Use it
                    best_slot = (specific_start_time_utc, specific_end_time_utc)
                else:
                    # Requested time is not available, fall back to finding best slot
                    best_slot = self.find_best_slot_in_week(
                        duration_minutes,
                        priority_number,
                        preferred_days,
                        exclude_weekends
                    )
            else:
                # Could not parse preferred time, find best slot
                best_slot = self.find_best_slot_in_week(
                    duration_minutes,
                    priority_number,
                    preferred_days,
                    exclude_weekends
                )
        else:
            # No preferred time, find best slot
            best_slot = self.find_best_slot_in_week(
                duration_minutes,
                priority_number,
                preferred_days,
                exclude_weekends
            )
        
        if best_slot:
            # Create the event
            new_event = CalendarEvent(
                task_title=task_title,
                description=description,
                start_time=best_slot[0],
                end_time=best_slot[0] + timedelta(minutes=duration_minutes),
                priority_number=priority_number,
                priority_tag=priority_tag,
                user_id=self.user_id
            )
            self.db.add(new_event)
            self.db.commit()
            self.db.refresh(new_event)
            
            # Convert times back to user's timezone for display in message
            start_time_user_tz = best_slot[0].astimezone(self.user_timezone)
            end_time_user_tz = (best_slot[0] + timedelta(minutes=duration_minutes)).astimezone(self.user_timezone)
            
            return {
                'success': True,
                'event': new_event.to_dict(),
                'message': f"Scheduled '{task_title}' from {start_time_user_tz.strftime('%a %b %d, %I:%M %p')} to {end_time_user_tz.strftime('%I:%M %p')}"
            }
        
        # No slot found - try rescheduling if allowed
        if self.preference.allow_auto_reschedule and priority_number is not None and (force_today or priority_number >= 7):
            return self.schedule_with_rescheduling(
                task_title,
                duration_minutes,
                priority_number,
                priority_tag,
                when,
                description
            )
        
        return {
            'success': False,
            'message': f"Could not find a suitable slot for '{task_title}' in the requested timeframe"
        }
    
    def schedule_with_rescheduling(
        self,
        task_title: str,
        duration_minutes: int,
        priority_number: int,
        priority_tag: PriorityTag,
        when: str,
        description: Optional[str] = None
    ) -> Dict:
        """Schedule with smart rescheduling across the week"""
        # Implementation similar to original but with week context
        # ... (keeping this shorter for now, can expand)
        return {
            'success': False,
            'message': "Rescheduling not yet implemented in smart scheduler"
        }
