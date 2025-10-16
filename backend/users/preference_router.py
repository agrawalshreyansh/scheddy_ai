"""
Router for user preferences and weekly goals
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field
from datetime import time
from db.database import get_db
from users.preference_controllers import (
    get_or_create_user_preference,
    update_user_preference,
    get_weekly_goal_status,
    initialize_weekly_goals,
    sync_weekly_goals_with_events
)

router = APIRouter(
    prefix="/preferences",
    tags=["preferences"]
)


class PreferenceUpdate(BaseModel):
    """Schema for updating user preferences"""
    work_start_hour: int | None = Field(None, ge=0, le=23, description="Work start hour (0-23)")
    work_start_minute: int | None = Field(None, ge=0, le=59, description="Work start minute")
    work_end_hour: int | None = Field(None, ge=0, le=23, description="Work end hour (0-23)")
    work_end_minute: int | None = Field(None, ge=0, le=59, description="Work end minute")
    work_days: list[int] | None = Field(None, description="Work days (0=Monday, 6=Sunday)")
    prefer_morning: bool | None = Field(None, description="Prefer morning time slots")
    allow_auto_reschedule: bool | None = Field(None, description="Allow automatic rescheduling")
    max_tasks_per_day: int | None = Field(None, ge=1, le=20, description="Maximum tasks per day")
    lunch_break_hour: int | None = Field(None, ge=0, le=23, description="Lunch break hour")
    lunch_break_minute: int | None = Field(None, ge=0, le=59, description="Lunch break minute")
    lunch_break_duration: int | None = Field(None, ge=0, le=120, description="Lunch break duration in minutes")
    min_break_between_tasks: int | None = Field(None, ge=0, le=60, description="Minimum break between tasks in minutes")
    weekly_goals: Dict[str, int] | None = Field(None, description="Weekly goals in hours per category")


class WeeklyGoalsUpdate(BaseModel):
    """Schema for updating weekly goals"""
    weekly_goals: Dict[str, int] = Field(..., description="Weekly goals in hours per category")


@router.get("/{user_id}")
async def get_user_preferences(user_id: UUID, db: Session = Depends(get_db)):
    """
    Get user preferences
    
    Returns user's scheduling preferences including:
    - Work hours
    - Work days
    - Scheduling preferences
    - Weekly goals
    """
    try:
        preference = get_or_create_user_preference(db, user_id)
        return {
            "success": True,
            "preferences": preference.to_dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{user_id}")
async def update_preferences(
    user_id: UUID,
    updates: PreferenceUpdate,
    db: Session = Depends(get_db)
):
    """
    Update user preferences
    
    You can update:
    - Work hours (work_start_hour, work_end_hour)
    - Work days (0=Monday, 6=Sunday)
    - Scheduling preferences
    - Weekly goals
    
    Example:
    ```json
    {
      "work_start_hour": 9,
      "work_end_hour": 17,
      "work_days": [0, 1, 2, 3, 4],
      "prefer_morning": true,
      "weekly_goals": {
        "learning": 5,
        "exercise": 3,
        "meetings": 10
      }
    }
    ```
    """
    try:
        # Convert updates to dict
        update_dict = {}
        
        if updates.work_start_hour is not None:
            work_start_minute = updates.work_start_minute or 0
            update_dict['work_start_time'] = time(updates.work_start_hour, work_start_minute)
        
        if updates.work_end_hour is not None:
            work_end_minute = updates.work_end_minute or 0
            update_dict['work_end_time'] = time(updates.work_end_hour, work_end_minute)
        
        if updates.lunch_break_hour is not None:
            lunch_break_minute = updates.lunch_break_minute or 0
            update_dict['lunch_break_start'] = time(updates.lunch_break_hour, lunch_break_minute)
        
        if updates.work_days is not None:
            update_dict['work_days'] = updates.work_days
        
        if updates.prefer_morning is not None:
            update_dict['prefer_morning'] = updates.prefer_morning
        
        if updates.allow_auto_reschedule is not None:
            update_dict['allow_auto_reschedule'] = updates.allow_auto_reschedule
        
        if updates.max_tasks_per_day is not None:
            update_dict['max_tasks_per_day'] = updates.max_tasks_per_day
        
        if updates.lunch_break_duration is not None:
            update_dict['lunch_break_duration'] = updates.lunch_break_duration
        
        if updates.min_break_between_tasks is not None:
            update_dict['min_break_between_tasks'] = updates.min_break_between_tasks
        
        if updates.weekly_goals is not None:
            update_dict['weekly_goals'] = updates.weekly_goals
            # Initialize trackers for this week
            initialize_weekly_goals(db, user_id)
        
        # Update preferences
        preference = update_user_preference(db, user_id, update_dict)
        
        return {
            "success": True,
            "message": "Preferences updated successfully",
            "preferences": preference.to_dict()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}/weekly-goals")
async def get_weekly_goals(user_id: UUID, db: Session = Depends(get_db)):
    """
    Get weekly goals status
    
    Returns:
    - Goal categories
    - Target hours
    - Completed hours
    - Progress percentage
    - Remaining hours
    """
    try:
        # Sync goals with actual events first
        sync_weekly_goals_with_events(db, user_id)
        
        # Get goal status
        goal_trackers = get_weekly_goal_status(db, user_id)
        
        goals_data = [tracker.to_dict() for tracker in goal_trackers]
        
        # Calculate summary stats
        total_goal_hours = sum(g['goal_hours'] for g in goals_data)
        total_completed_hours = sum(g['completed_hours'] for g in goals_data)
        overall_progress = (total_completed_hours / total_goal_hours * 100) if total_goal_hours > 0 else 0
        
        return {
            "success": True,
            "goals": goals_data,
            "summary": {
                "total_goal_hours": total_goal_hours,
                "total_completed_hours": total_completed_hours,
                "overall_progress": round(overall_progress, 1),
                "goals_completed": sum(1 for g in goals_data if g['is_complete']),
                "total_goals": len(goals_data)
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{user_id}/weekly-goals")
async def set_weekly_goals(
    user_id: UUID,
    goals: WeeklyGoalsUpdate,
    db: Session = Depends(get_db)
):
    """
    Set or update weekly goals
    
    Example:
    ```json
    {
      "weekly_goals": {
        "learning": 5,
        "exercise": 3,
        "meetings": 10,
        "coding": 15
      }
    }
    ```
    
    Categories can be: learning, exercise, meetings, coding, personal, planning, etc.
    """
    try:
        # Update preferences with new goals
        preference = update_user_preference(db, user_id, {
            'weekly_goals': goals.weekly_goals
        })
        
        # Initialize trackers for current week
        initialize_weekly_goals(db, user_id)
        
        # Sync with existing events
        sync_weekly_goals_with_events(db, user_id)
        
        return {
            "success": True,
            "message": "Weekly goals updated successfully",
            "weekly_goals": preference.weekly_goals
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
