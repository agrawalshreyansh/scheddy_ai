"""
Enhanced Smart Scheduler with User Preferences and Weekly Context
"""
from datetime import datetime, timedelta, time
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
    
    def __init__(self, db: Session, user_id: UUID):
        self.db = db
        self.user_id = user_id
        self.preference = get_or_create_user_preference(db, user_id)
    
    def parse_duration(self, duration_str: str) -> int:
        """Parse duration string to minutes"""
        duration_str = duration_str.lower().strip()
        total_minutes = 0
        
        if 'h' in duration_str:
            parts = duration_str.split('h')
            try:
                hours = int(parts[0])
                total_minutes += hours * 60
                duration_str = parts[1] if len(parts) > 1 else ''
            except ValueError:
                pass
        
        if 'm' in duration_str:
            minutes_str = duration_str.replace('m', '').strip()
            if minutes_str:
                try:
                    total_minutes += int(minutes_str)
                except ValueError:
                    pass
        
        return total_minutes if total_minutes > 0 else 60
    
    def get_priority_number_from_tag(self, priority_tag: str) -> Tuple[int, PriorityTag]:
        """Convert priority tag string to priority number and enum"""
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
        Get the next weekend (Saturday and Sunday)
        
        Returns:
            Tuple of (saturday_start, sunday_end)
        """
        if from_date is None:
            from_date = datetime.now()
        
        # Find next Saturday
        days_until_saturday = (5 - from_date.weekday()) % 7
        if days_until_saturday == 0 and from_date.hour >= 18:
            # If it's Saturday evening, go to next weekend
            days_until_saturday = 7
        
        saturday = from_date + timedelta(days=days_until_saturday)
        saturday_start = saturday.replace(hour=10, minute=0, second=0, microsecond=0)
        
        sunday = saturday + timedelta(days=1)
        sunday_end = sunday.replace(hour=20, minute=0, second=0, microsecond=0)
        
        return (saturday_start, sunday_end)
    
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
            Tuple of (day_start, day_end)
        """
        work_start_hour, work_end_hour = self.preference.get_work_hours()
        
        # Weekend has different hours
        if self.is_weekend_day(date):
            day_start = datetime.combine(date.date(), time(10, 0))
            day_end = datetime.combine(date.date(), time(20, 0))
        else:
            day_start = datetime.combine(date.date(), time(work_start_hour, 0))
            day_end = datetime.combine(date.date(), time(work_end_hour, 0))
        
        return (day_start, day_end)
    
    def get_week_events(self, week_identifier: str = None) -> List[CalendarEvent]:
        """Get all events for the week"""
        week_start, week_end = get_week_start_end(week_identifier)
        
        return self.db.query(CalendarEvent).filter(
            CalendarEvent.user_id == self.user_id,
            CalendarEvent.start_time >= week_start,
            CalendarEvent.start_time < week_end
        ).order_by(CalendarEvent.start_time).all()
    
    def get_day_events(self, date: datetime) -> List[CalendarEvent]:
        """Get all events for a specific day"""
        day_start, day_end = self.get_available_hours_in_day(date)
        
        return self.db.query(CalendarEvent).filter(
            CalendarEvent.user_id == self.user_id,
            CalendarEvent.start_time >= day_start,
            CalendarEvent.start_time < day_end
        ).order_by(CalendarEvent.start_time).all()
    
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
        current_date = max(datetime.now(), week_start)
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
        current_time = max(day_start, datetime.now())
        
        # Add buffer for lunch break
        lunch_start = datetime.combine(date.date(), self.preference.lunch_break_start)
        lunch_end = lunch_start + timedelta(minutes=self.preference.lunch_break_duration)
        
        for event in events:
            # Check gap before this event
            if current_time < event.start_time:
                # Skip lunch break
                if not (current_time <= lunch_start < event.start_time):
                    gap_duration = (event.start_time - current_time).total_seconds() / 60
                    if gap_duration >= duration_minutes:
                        available_slots.append((current_time, event.start_time))
            
            current_time = max(current_time, event.end_time)
            
            # Add break time
            if self.preference.min_break_between_tasks > 0:
                current_time += timedelta(minutes=self.preference.min_break_between_tasks)
        
        # Check end of day
        if current_time < day_end:
            gap_duration = (day_end - current_time).total_seconds() / 60
            if gap_duration >= duration_minutes:
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
        day_events = [e for e in week_events if e.start_time.date() == slot_start.date()]
        day_load = len(day_events)
        
        if day_load < 3:
            score += 15
        elif day_load > 6:
            score -= 15
        
        # Prefer weekdays for high priority
        if priority_number >= 7 and not self.is_weekend_day(slot_start):
            score += 10
        
        # Slight penalty for weekend for non-leisure tasks
        if self.is_weekend_day(slot_start) and priority_number >= 7:
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
        category: Optional[str] = None
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
        
        Returns:
            Dict with scheduling result
        """
        # Determine preferred days based on 'when'
        preferred_days = None
        exclude_weekends = False
        force_today = False
        
        if when == "today":
            preferred_days = [datetime.now().strftime("%A")]
            force_today = True
        elif when == "tomorrow":
            tomorrow = datetime.now() + timedelta(days=1)
            preferred_days = [tomorrow.strftime("%A")]
        elif when == "weekend":
            preferred_days = ["weekend"]
        elif when == "this_week":
            # Any day this week
            pass
        
        # Find best slot
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
            
            return {
                'success': True,
                'event': new_event.to_dict(),
                'message': f"Scheduled '{task_title}' from {best_slot[0].strftime('%a %b %d, %I:%M %p')} to {(best_slot[0] + timedelta(minutes=duration_minutes)).strftime('%I:%M %p')}"
            }
        
        # No slot found - try rescheduling if allowed
        if self.preference.allow_auto_reschedule and (force_today or priority_number >= 7):
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
