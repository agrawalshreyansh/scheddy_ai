"""
User Preferences and Weekly Goals Management
"""
from sqlalchemy import Column, String, Integer, Time, Boolean, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db.database import Base
import uuid
from datetime import time


class UserPreference(Base):
    """User preferences for scheduling behavior"""
    __tablename__ = "user_preferences"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    # Working hours
    work_start_time = Column(Time, default=time(9, 0), nullable=False)  # 9:00 AM
    work_end_time = Column(Time, default=time(18, 0), nullable=False)   # 6:00 PM
    
    # Work days (0=Monday, 6=Sunday)
    work_days = Column(JSON, default=[0, 1, 2, 3, 4])  # Monday-Friday by default
    
    # Preferred time slots (JSON array of times)
    preferred_morning_tasks = Column(JSON, default=["focus_work", "important_meetings"])
    preferred_afternoon_tasks = Column(JSON, default=["meetings", "calls"])
    preferred_evening_tasks = Column(JSON, default=["learning", "reading"])
    
    # Break preferences
    lunch_break_start = Column(Time, default=time(12, 0))
    lunch_break_duration = Column(Integer, default=60)  # minutes
    min_break_between_tasks = Column(Integer, default=0)  # minutes
    
    # Scheduling preferences
    allow_auto_reschedule = Column(Boolean, default=True)
    max_tasks_per_day = Column(Integer, default=10)
    prefer_morning = Column(Boolean, default=True)  # Prefer morning slots
    
    # Weekly goals (JSON)
    # Format: {"learning": 5, "meetings": 10, "exercise": 3} - hours per week
    weekly_goals = Column(JSON, default={})
    
    # Relationship
    user = relationship("User", back_populates="preference")
    
    def __repr__(self):
        return f"<UserPreference(user_id={self.user_id}, work_hours={self.work_start_time}-{self.work_end_time})>"
    
    def is_work_day(self, day_of_week: int) -> bool:
        """Check if a day is a work day (0=Monday, 6=Sunday)"""
        return day_of_week in self.work_days
    
    def is_weekend(self, day_of_week: int) -> bool:
        """Check if a day is weekend"""
        return day_of_week in [5, 6]  # Saturday, Sunday
    
    def get_work_hours(self):
        """Get work start and end hours as tuple"""
        # Ensure work times are not None
        start_hour = self.work_start_time.hour if self.work_start_time else 9
        end_hour = self.work_end_time.hour if self.work_end_time else 18
        return (start_hour, end_hour)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "work_start_time": self.work_start_time.isoformat() if self.work_start_time else None,
            "work_end_time": self.work_end_time.isoformat() if self.work_end_time else None,
            "work_days": self.work_days,
            "preferred_morning_tasks": self.preferred_morning_tasks,
            "preferred_afternoon_tasks": self.preferred_afternoon_tasks,
            "preferred_evening_tasks": self.preferred_evening_tasks,
            "lunch_break_start": self.lunch_break_start.isoformat() if self.lunch_break_start else None,
            "lunch_break_duration": self.lunch_break_duration,
            "min_break_between_tasks": self.min_break_between_tasks,
            "allow_auto_reschedule": self.allow_auto_reschedule,
            "max_tasks_per_day": self.max_tasks_per_day,
            "prefer_morning": self.prefer_morning,
            "weekly_goals": self.weekly_goals
        }


class WeeklyGoalTracker(Base):
    """Track weekly goal progress"""
    __tablename__ = "weekly_goal_trackers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Week identifier (e.g., "2024-W42")
    week_identifier = Column(String(20), nullable=False, index=True)
    
    # Goal category (e.g., "learning", "exercise", "meetings")
    category = Column(String(100), nullable=False, index=True)
    
    # Goal in hours
    goal_hours = Column(Integer, nullable=False)
    
    # Actual hours completed
    completed_hours = Column(Integer, default=0)
    
    # Relationship
    user = relationship("User")
    
    def __repr__(self):
        return f"<WeeklyGoalTracker(week={self.week_identifier}, category={self.category}, {self.completed_hours}/{self.goal_hours}h)>"
    
    def get_progress_percentage(self) -> float:
        """Get progress as percentage"""
        if self.goal_hours == 0:
            return 100.0
        return (self.completed_hours / self.goal_hours) * 100
    
    def is_complete(self) -> bool:
        """Check if goal is met"""
        return self.completed_hours >= self.goal_hours
    
    def remaining_hours(self) -> int:
        """Get remaining hours to reach goal"""
        return max(0, self.goal_hours - self.completed_hours)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "week_identifier": self.week_identifier,
            "category": self.category,
            "goal_hours": self.goal_hours,
            "completed_hours": self.completed_hours,
            "progress_percentage": self.get_progress_percentage(),
            "is_complete": self.is_complete(),
            "remaining_hours": self.remaining_hours()
        }
