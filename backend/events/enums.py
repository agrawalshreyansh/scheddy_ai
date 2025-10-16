"""
Enums for the events module
"""
import enum


class PriorityTag(str, enum.Enum):
    """Priority tags for calendar events"""
    URGENT = "urgent"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    OPTIONAL = "optional"
