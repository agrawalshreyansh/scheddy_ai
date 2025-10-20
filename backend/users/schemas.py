from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, Dict, List
from datetime import datetime, time
from uuid import UUID


class UserBase(BaseModel):
    """Base User schema with common attributes"""
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    email: EmailStr = Field(..., description="User email address")
    full_name: Optional[str] = Field(None, max_length=100, description="Full name of the user")


class UserCreate(UserBase):
    """Schema for creating a new user"""
    password: str = Field(..., min_length=8, description="User password (min 8 characters)")


class UserUpdate(BaseModel):
    """Schema for updating user information"""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=100)
    password: Optional[str] = Field(None, min_length=8)
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """Schema for user response (without password)"""
    id: UUID
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserInDB(UserResponse):
    """Schema for user in database (with hashed password)"""
    hashed_password: str


class LoginRequest(BaseModel):
    """Schema for login request"""
    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="User password")


class Token(BaseModel):
    """Schema for authentication token response"""
    access_token: str
    token_type: str
    user_id: UUID
    username: str
    email: str
    full_name: Optional[str] = None


class TokenData(BaseModel):
    """Schema for token data"""
    username: Optional[str] = None


class UserPreferenceResponse(BaseModel):
    """Schema for user preference response"""
    id: UUID
    user_id: UUID
    work_start_time: Optional[str]
    work_end_time: Optional[str]
    work_days: List[int]
    preferred_morning_tasks: List[str]
    preferred_afternoon_tasks: List[str]
    preferred_evening_tasks: List[str]
    lunch_break_start: Optional[str]
    lunch_break_duration: int
    min_break_between_tasks: int
    allow_auto_reschedule: bool
    max_tasks_per_day: int
    prefer_morning: bool
    weekly_goals: Dict[str, int]

    model_config = ConfigDict(from_attributes=True)


class PreferenceUpdate(BaseModel):
    """Schema for updating user preferences"""
    work_start_hour: Optional[int] = Field(None, ge=0, le=23, description="Work start hour (0-23)")
    work_start_minute: Optional[int] = Field(None, ge=0, le=59, description="Work start minute")
    work_end_hour: Optional[int] = Field(None, ge=0, le=23, description="Work end hour (0-23)")
    work_end_minute: Optional[int] = Field(None, ge=0, le=59, description="Work end minute")
    work_days: Optional[List[int]] = Field(None, description="Work days (0=Monday, 6=Sunday)")
    prefer_morning: Optional[bool] = Field(None, description="Prefer morning time slots")
    allow_auto_reschedule: Optional[bool] = Field(None, description="Allow automatic rescheduling")
    max_tasks_per_day: Optional[int] = Field(None, ge=1, le=20, description="Maximum tasks per day")
    lunch_break_hour: Optional[int] = Field(None, ge=0, le=23, description="Lunch break hour")
    lunch_break_minute: Optional[int] = Field(None, ge=0, le=59, description="Lunch break minute")
    lunch_break_duration: Optional[int] = Field(None, ge=0, le=120, description="Lunch break duration in minutes")
    min_break_between_tasks: Optional[int] = Field(None, ge=0, le=60, description="Minimum break between tasks in minutes")
    weekly_goals: Optional[Dict[str, int]] = Field(None, description="Weekly goals in hours per category")


class WeeklyGoalsUpdate(BaseModel):
    """Schema for updating weekly goals"""
    weekly_goals: Dict[str, int] = Field(..., description="Weekly goals in hours per category")


class WeeklyGoalTrackerResponse(BaseModel):
    """Schema for weekly goal tracker response"""
    id: UUID
    user_id: UUID
    week_identifier: str
    category: str
    goal_hours: float
    completed_hours: float
    progress_percentage: float
    is_complete: bool

    model_config = ConfigDict(from_attributes=True)
