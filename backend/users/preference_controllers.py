"""
Controllers for managing user preferences and weekly goals
"""
from sqlalchemy.orm import Session
from typing import Optional, Dict, List
from datetime import datetime, timedelta, timezone
from uuid import UUID
from users.preferences import UserPreference, WeeklyGoalTracker
from events.models import CalendarEvent


def get_or_create_user_preference(db: Session, user_id: UUID) -> UserPreference:
    """
    Get user preference or create default if doesn't exist
    
    Args:
        db: Database session
        user_id: User UUID
    
    Returns:
        UserPreference object
    """
    preference = db.query(UserPreference).filter(UserPreference.user_id == user_id).first()
    
    if not preference:
        # Create default preference
        preference = UserPreference(user_id=user_id)
        db.add(preference)
        db.commit()
        db.refresh(preference)
    
    return preference


def update_user_preference(
    db: Session,
    user_id: UUID,
    updates: Dict
) -> UserPreference:
    """
    Update user preferences
    
    Args:
        db: Database session
        user_id: User UUID
        updates: Dictionary of fields to update
    
    Returns:
        Updated UserPreference object
    """
    preference = get_or_create_user_preference(db, user_id)
    
    for field, value in updates.items():
        if hasattr(preference, field):
            setattr(preference, field, value)
    
    db.commit()
    db.refresh(preference)
    return preference


def get_week_identifier(date: datetime = None) -> str:
    """
    Get week identifier for a date (format: YYYY-Wxx)
    
    Args:
        date: Date to get week for (defaults to now)
    
    Returns:
        Week identifier string like "2024-W42"
    """
    if date is None:
        date = datetime.now(timezone.utc)
    
    year, week, _ = date.isocalendar()
    return f"{year}-W{week:02d}"


def get_week_start_end(week_identifier: str = None) -> tuple[datetime, datetime]:
    """
    Get start and end datetime for a week
    
    Args:
        week_identifier: Week identifier like "2024-W42" (defaults to current week)
    
    Returns:
        Tuple of (start_datetime, end_datetime)
    """
    if week_identifier is None:
        week_identifier = get_week_identifier()
    
    year, week = week_identifier.split('-W')
    year = int(year)
    week = int(week)
    
    # Get first day of week (Monday) - timezone-aware
    jan_4 = datetime(year, 1, 4, tzinfo=timezone.utc)
    week_start = jan_4 - timedelta(days=jan_4.weekday()) + timedelta(weeks=week - 1)
    week_end = week_start + timedelta(days=7)
    
    return (week_start, week_end)


def initialize_weekly_goals(db: Session, user_id: UUID, week_identifier: str = None):
    """
    Initialize weekly goals for a user based on their preferences
    
    Args:
        db: Database session
        user_id: User UUID
        week_identifier: Week identifier (defaults to current week)
    """
    if week_identifier is None:
        week_identifier = get_week_identifier()
    
    preference = get_or_create_user_preference(db, user_id)
    
    if not preference.weekly_goals:
        return
    
    # Create goal trackers for each category
    for category, goal_hours in preference.weekly_goals.items():
        # Check if already exists
        existing = db.query(WeeklyGoalTracker).filter(
            WeeklyGoalTracker.user_id == user_id,
            WeeklyGoalTracker.week_identifier == week_identifier,
            WeeklyGoalTracker.category == category
        ).first()
        
        if not existing:
            tracker = WeeklyGoalTracker(
                user_id=user_id,
                week_identifier=week_identifier,
                category=category,
                goal_hours=goal_hours,
                completed_hours=0
            )
            db.add(tracker)
    
    db.commit()


def update_weekly_goal_progress(
    db: Session,
    user_id: UUID,
    category: str,
    hours_to_add: float,
    week_identifier: str = None
):
    """
    Update progress on a weekly goal
    
    Args:
        db: Database session
        user_id: User UUID
        category: Goal category
        hours_to_add: Hours to add to progress
        week_identifier: Week identifier (defaults to current week)
    """
    if week_identifier is None:
        week_identifier = get_week_identifier()
    
    # Ensure weekly goals are initialized
    initialize_weekly_goals(db, user_id, week_identifier)
    
    tracker = db.query(WeeklyGoalTracker).filter(
        WeeklyGoalTracker.user_id == user_id,
        WeeklyGoalTracker.week_identifier == week_identifier,
        WeeklyGoalTracker.category == category
    ).first()
    
    if tracker:
        tracker.completed_hours += int(hours_to_add)
        db.commit()
        db.refresh(tracker)
        return tracker
    
    return None


def get_weekly_goal_status(
    db: Session,
    user_id: UUID,
    week_identifier: str = None
) -> List[WeeklyGoalTracker]:
    """
    Get status of all weekly goals
    
    Args:
        db: Database session
        user_id: User UUID
        week_identifier: Week identifier (defaults to current week)
    
    Returns:
        List of WeeklyGoalTracker objects
    """
    if week_identifier is None:
        week_identifier = get_week_identifier()
    
    # Ensure weekly goals are initialized
    initialize_weekly_goals(db, user_id, week_identifier)
    
    return db.query(WeeklyGoalTracker).filter(
        WeeklyGoalTracker.user_id == user_id,
        WeeklyGoalTracker.week_identifier == week_identifier
    ).all()


def calculate_weekly_hours_by_category(
    db: Session,
    user_id: UUID,
    week_identifier: str = None
) -> Dict[str, float]:
    """
    Calculate actual hours spent per category this week based on calendar events
    
    Args:
        db: Database session
        user_id: User UUID
        week_identifier: Week identifier (defaults to current week)
    
    Returns:
        Dictionary of category -> hours
    """
    if week_identifier is None:
        week_identifier = get_week_identifier()
    
    week_start, week_end = get_week_start_end(week_identifier)
    
    # Get all events in this week
    events = db.query(CalendarEvent).filter(
        CalendarEvent.user_id == user_id,
        CalendarEvent.start_time >= week_start,
        CalendarEvent.start_time < week_end
    ).all()
    
    # Calculate hours per category
    category_hours = {}
    for event in events:
        duration_hours = (event.end_time - event.start_time).total_seconds() / 3600
        
        # Extract category from task title or description
        # You can enhance this with better categorization logic
        category = categorize_task(event.task_title, event.description)
        
        if category in category_hours:
            category_hours[category] += duration_hours
        else:
            category_hours[category] = duration_hours
    
    return category_hours


def categorize_task(title: str, description: str = None) -> str:
    """
    Categorize a task based on keywords
    
    Args:
        title: Task title
        description: Task description
    
    Returns:
        Category string
    """
    text = (title + ' ' + (description or '')).lower()
    
    # Define category keywords
    categories = {
        "learning": ["learn", "study", "course", "tutorial", "read", "book", "education"],
        "exercise": ["gym", "workout", "exercise", "run", "yoga", "fitness"],
        "meetings": ["meeting", "call", "standup", "sync", "discussion"],
        "coding": ["code", "develop", "programming", "debug", "implement"],
        "planning": ["plan", "organize", "strategy", "roadmap"],
        "personal": ["personal", "family", "friends", "hobby"],
    }
    
    for category, keywords in categories.items():
        if any(keyword in text for keyword in keywords):
            return category
    
    return "general"


def get_remaining_goal_tasks(
    db: Session,
    user_id: UUID,
    week_identifier: str = None
) -> List[Dict]:
    """
    Get remaining tasks needed to meet weekly goals
    
    Args:
        db: Database session
        user_id: User UUID
        week_identifier: Week identifier (defaults to current week)
    
    Returns:
        List of dicts with category and remaining hours
    """
    trackers = get_weekly_goal_status(db, user_id, week_identifier)
    
    remaining = []
    for tracker in trackers:
        if not tracker.is_complete():
            remaining.append({
                "category": tracker.category,
                "remaining_hours": tracker.remaining_hours(),
                "goal_hours": tracker.goal_hours,
                "completed_hours": tracker.completed_hours,
                "progress_percentage": tracker.get_progress_percentage()
            })
    
    return remaining


def sync_weekly_goals_with_events(
    db: Session,
    user_id: UUID,
    week_identifier: str = None
):
    """
    Sync weekly goal progress with actual calendar events
    
    Args:
        db: Database session
        user_id: User UUID
        week_identifier: Week identifier (defaults to current week)
    """
    if week_identifier is None:
        week_identifier = get_week_identifier()
    
    # Calculate actual hours
    actual_hours = calculate_weekly_hours_by_category(db, user_id, week_identifier)
    
    # Update trackers
    for category, hours in actual_hours.items():
        tracker = db.query(WeeklyGoalTracker).filter(
            WeeklyGoalTracker.user_id == user_id,
            WeeklyGoalTracker.week_identifier == week_identifier,
            WeeklyGoalTracker.category == category
        ).first()
        
        if tracker:
            tracker.completed_hours = int(hours)
            db.commit()
