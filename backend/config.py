"""
Configuration settings for the Scheddy AI Calendar Assistant
Modify these values to customize the behavior
"""
from datetime import time
from events.enums import PriorityTag
import os


class AuthConfig:
    """Configuration for authentication and security"""
    
    # JWT Configuration
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production-min-32-chars")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60  # 30 days


class CORSConfig:
    """Configuration for CORS (Cross-Origin Resource Sharing)"""
    
    # Allowed origins - frontend URLs that can access the API
    # Set FRONTEND_URL environment variable for production
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:4000")
    
    @classmethod
    def get_allowed_origins(cls):
        """Get list of allowed origins"""
        origins = [cls.FRONTEND_URL]
        # Also allow 127.0.0.1 variant of localhost
        if "localhost:3000" in cls.FRONTEND_URL:
            origins.append("http://127.0.0.1:3000")
        return origins


class SchedulingConfig:
    """Configuration for the scheduling engine"""
    
    # Working hours (24-hour format)
    WORK_START_HOUR = 9   # 9 AM
    WORK_END_HOUR = 18    # 6 PM
    
    # Scheduling preferences
    MIN_SLOT_DURATION_MINUTES = 15  # Minimum time slot duration
    DEFAULT_TASK_DURATION_MINUTES = 60  # Default duration if not specified
    MAX_DAYS_TO_SEARCH = 7  # How many days ahead to look for slots
    MAX_DAYS_TO_PUSH_TASKS = 30  # How far to push rescheduled tasks
    
    # Priority thresholds
    PRIORITY_THRESHOLD_AUTO_RESCHEDULE = 7  # Auto-reschedule if priority >= this
    
    # LLM Configuration
    LLM_MODEL = "meta-llama/llama-3.2-3b-instruct:free"
    LLM_DEFAULT_TEMPERATURE = 0.2  # Lower = more focused, higher = more creative
    LLM_MAX_RETRIES = 3
    
    # Time slot preferences (can be customized per user)
    PREFERRED_START_TIMES = [
        time(9, 0),   # 9:00 AM
        time(10, 0),  # 10:00 AM
        time(11, 0),  # 11:00 AM
        time(14, 0),  # 2:00 PM
        time(15, 0),  # 3:00 PM
        time(16, 0),  # 4:00 PM
    ]
    
    # Break time (automatically add buffer between meetings)
    AUTO_BUFFER_MINUTES = 0  # Set to 5-15 for automatic breaks
    
    # Priority mapping
    PRIORITY_MAP = {
        PriorityTag.URGENT: 10,
        PriorityTag.HIGH: 8,
        PriorityTag.MEDIUM: 5,
        PriorityTag.LOW: 3,
        PriorityTag.OPTIONAL: 1
    }
    
    # Natural language keywords for priority detection
    URGENT_KEYWORDS = [
        "urgent", "asap", "critical", "emergency", "must", "have to",
        "need to today", "right now", "immediately"
    ]
    
    HIGH_PRIORITY_KEYWORDS = [
        "important", "high priority", "need to", "should", "deadline"
    ]
    
    LOW_PRIORITY_KEYWORDS = [
        "when possible", "maybe", "if time", "whenever", "someday"
    ]
    
    OPTIONAL_KEYWORDS = [
        "optional", "nice to have", "if i can", "would like to"
    ]
    
    # Duration estimation by task type (in minutes)
    # Used when user doesn't specify duration
    DEFAULT_DURATIONS = {
        "meeting": 60,
        "call": 30,
        "workout": 60,
        "gym": 60,
        "review": 45,
        "planning": 90,
        "learning": 90,
        "study": 120,
        "break": 15,
        "lunch": 60,
        "reading": 60,
        "writing": 90,
        "coding": 120,
        "debugging": 60,
        "research": 90,
    }
    
    # Response messages
    MESSAGES = {
        "success_scheduled": "Successfully scheduled '{title}' from {start} to {end}",
        "success_with_reschedule": "Scheduled '{title}' from {start} to {end}. Rescheduled {count} lower-priority events.",
        "no_slot_found": "Could not find a suitable time slot for '{title}'. Calendar is fully booked.",
        "invalid_duration": "Could not parse duration '{duration}'. Using default duration.",
        "no_events": "No events scheduled for the requested period",
    }


class UserPreferences:
    """Per-user preferences (can be extended to database)"""
    
    def __init__(self):
        # Working hours can vary per user
        self.work_start_hour = SchedulingConfig.WORK_START_HOUR
        self.work_end_hour = SchedulingConfig.WORK_END_HOUR
        
        # Some users prefer early morning, others late afternoon
        self.preferred_time_of_day = "morning"  # "morning", "afternoon", "evening"
        
        # Auto-scheduling preferences
        self.allow_auto_reschedule = True
        self.min_priority_to_reschedule_others = 7
        
        # Notification preferences
        self.notify_on_reschedule = True
        self.notify_before_event_minutes = 15
    
    def get_working_hours(self):
        """Get user's working hours"""
        return (self.work_start_hour, self.work_end_hour)


# Export singleton config
config = SchedulingConfig()


def get_estimated_duration(task_description: str) -> int:
    """
    Estimate task duration based on keywords in description
    
    Args:
        task_description: The task title or description
    
    Returns:
        Estimated duration in minutes
    """
    task_lower = task_description.lower()
    
    for keyword, duration in config.DEFAULT_DURATIONS.items():
        if keyword in task_lower:
            return duration
    
    return config.DEFAULT_TASK_DURATION_MINUTES


def detect_priority_from_text(text: str) -> str:
    """
    Detect priority level from text based on keywords
    
    Args:
        text: The text to analyze
    
    Returns:
        Priority level string: "urgent", "high", "medium", "low", or "optional"
    """
    text_lower = text.lower()
    
    # Check for urgent keywords
    if any(keyword in text_lower for keyword in config.URGENT_KEYWORDS):
        return "urgent"
    
    # Check for high priority keywords
    if any(keyword in text_lower for keyword in config.HIGH_PRIORITY_KEYWORDS):
        return "high"
    
    # Check for low priority keywords
    if any(keyword in text_lower for keyword in config.LOW_PRIORITY_KEYWORDS):
        return "low"
    
    # Check for optional keywords
    if any(keyword in text_lower for keyword in config.OPTIONAL_KEYWORDS):
        return "optional"
    
    # Default to medium
    return "medium"


# Example usage:
if __name__ == "__main__":
    print("Scheddy Configuration Settings")
    print("=" * 50)
    print(f"Working Hours: {config.WORK_START_HOUR}:00 - {config.WORK_END_HOUR}:00")
    print(f"Default Task Duration: {config.DEFAULT_TASK_DURATION_MINUTES} minutes")
    print(f"Max Days to Search: {config.MAX_DAYS_TO_SEARCH}")
    print(f"LLM Model: {config.LLM_MODEL}")
    print("\nPriority Levels:")
    for tag, value in config.PRIORITY_MAP.items():
        print(f"  {tag.value}: {value}")
    print("\nDefault Task Durations:")
    for task_type, duration in config.DEFAULT_DURATIONS.items():
        print(f"  {task_type}: {duration} minutes")
    
    # Test priority detection
    print("\n" + "=" * 50)
    print("Testing Priority Detection:")
    test_phrases = [
        "This is urgent and critical",
        "Important meeting with client",
        "Maybe watch a video when possible",
        "Optional reading if I have time",
        "Regular task for tomorrow"
    ]
    for phrase in test_phrases:
        priority = detect_priority_from_text(phrase)
        print(f"  '{phrase}' → {priority}")
    
    # Test duration estimation
    print("\n" + "=" * 50)
    print("Testing Duration Estimation:")
    test_tasks = [
        "Team meeting",
        "Gym workout",
        "Quick call with client",
        "Study for exam",
        "Some random task"
    ]
    for task in test_tasks:
        duration = get_estimated_duration(task)
        print(f"  '{task}' → {duration} minutes")
