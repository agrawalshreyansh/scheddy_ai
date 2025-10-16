"""
Calendar Orchestrator
Coordinates between LLM intent extraction and scheduling engine to execute user commands
"""
import json
from datetime import datetime, timedelta
from typing import Dict, Optional
from sqlalchemy.orm import Session
from uuid import UUID
from agents.llm import ask_llm
from agents.scheduler import SchedulingEngine
from events.controllers import (
    get_calendar_events,
    get_events_by_date_range,
    delete_calendar_event,
    update_calendar_event
)
from events.schemas import CalendarEventUpdate


class CalendarOrchestrator:
    """
    Orchestrates the interaction between:
    1. Natural language understanding (LLM)
    2. Scheduling engine (finding slots, rescheduling)
    3. Database operations (CRUD)
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.scheduler = SchedulingEngine(db)
    
    def process_user_request(
        self,
        user_id: UUID,
        user_message: str,
        temperature: float = 0.2
    ) -> Dict:
        """
        Process a natural language request from the user
        
        Args:
            user_id: UUID of the user making the request
            user_message: Natural language message from user
            temperature: LLM temperature for response creativity
        
        Returns:
            Dictionary with success status, message, and any relevant data
        """
        try:
            # Step 1: Extract intent using LLM
            llm_response = ask_llm(user_message, temperature=temperature)
            
            # Parse the JSON response
            try:
                intent_data = json.loads(llm_response['content'])
            except json.JSONDecodeError as e:
                return {
                    'success': False,
                    'message': f"Could not understand the request. Please try rephrasing.",
                    'error': f"JSON parse error: {str(e)}",
                    'llm_response': llm_response['content']
                }
            
            # Step 2: Execute the action based on intent
            action = intent_data.get('action', '').lower()
            
            if action == 'create_event':
                return self._handle_create_event(user_id, intent_data)
            
            elif action == 'update_event':
                return self._handle_update_event(user_id, intent_data)
            
            elif action == 'delete_event':
                return self._handle_delete_event(user_id, intent_data)
            
            elif action == 'list_events' or action == 'query_schedule':
                return self._handle_query_schedule(user_id, intent_data)
            
            else:
                return {
                    'success': False,
                    'message': f"Unknown action: {action}",
                    'intent_data': intent_data
                }
        
        except Exception as e:
            return {
                'success': False,
                'message': f"Error processing request: {str(e)}",
                'error': str(e)
            }
    
    def _handle_create_event(self, user_id: UUID, intent_data: Dict) -> Dict:
        """
        Handle event creation with intelligent scheduling
        """
        # Extract data from intent
        title = intent_data.get('title', 'Untitled Task')
        duration_str = intent_data.get('duration', '30m')
        priority_str = intent_data.get('priority', 'medium')
        when = intent_data.get('when')
        force_today = intent_data.get('force_today', False)
        description = intent_data.get('description')
        
        # Parse duration
        duration_minutes = self.scheduler.parse_duration(duration_str)
        
        # Get priority
        priority_number, priority_tag = self.scheduler.get_priority_number_from_tag(priority_str)
        
        # Determine preferred date
        preferred_date = self._parse_when(when)
        
        # Use the scheduling engine to schedule with auto-rescheduling
        result = self.scheduler.schedule_with_auto_reschedule(
            user_id=user_id,
            task_title=title,
            duration_minutes=duration_minutes,
            priority_number=priority_number,
            priority_tag=priority_tag,
            preferred_date=preferred_date,
            description=description,
            force_today=force_today or (when == 'today' and priority_number >= 7)
        )
        
        # Format the response
        if result['success']:
            response = {
                'success': True,
                'message': result['message'],
                'event': result['event'],
                'action': 'create_event'
            }
            
            if result['rescheduled_events']:
                response['rescheduled_events'] = result['rescheduled_events']
                response['message'] += f"\n\nℹ️ Moved {len(result['rescheduled_events'])} lower-priority tasks to make room:"
                for re in result['rescheduled_events']:
                    old_time = datetime.fromisoformat(re['old_start']).strftime('%b %d, %I:%M %p')
                    new_time = datetime.fromisoformat(re['new_start']).strftime('%b %d, %I:%M %p')
                    response['message'] += f"\n  • {re['event_title']}: {old_time} → {new_time}"
            
            return response
        else:
            return {
                'success': False,
                'message': result['message'],
                'action': 'create_event'
            }
    
    def _handle_update_event(self, user_id: UUID, intent_data: Dict) -> Dict:
        """
        Handle event updates
        """
        event_id_str = intent_data.get('event_id')
        if not event_id_str:
            return {
                'success': False,
                'message': "No event ID provided for update",
                'action': 'update_event'
            }
        
        try:
            event_id = UUID(event_id_str)
        except ValueError:
            return {
                'success': False,
                'message': f"Invalid event ID: {event_id_str}",
                'action': 'update_event'
            }
        
        # Build update data
        update_data = {}
        
        if 'title' in intent_data:
            update_data['task_title'] = intent_data['title']
        
        if 'description' in intent_data:
            update_data['description'] = intent_data['description']
        
        if 'priority' in intent_data:
            priority_number, priority_tag = self.scheduler.get_priority_number_from_tag(
                intent_data['priority']
            )
            update_data['priority_number'] = priority_number
            update_data['priority_tag'] = priority_tag
        
        if not update_data:
            return {
                'success': False,
                'message': "No fields to update",
                'action': 'update_event'
            }
        
        # Perform the update
        event_update = CalendarEventUpdate(**update_data)
        updated_event = update_calendar_event(self.db, event_id, event_update)
        
        if updated_event:
            return {
                'success': True,
                'message': f"Successfully updated event: {updated_event.task_title}",
                'event': updated_event.to_dict(),
                'action': 'update_event'
            }
        else:
            return {
                'success': False,
                'message': f"Event not found: {event_id}",
                'action': 'update_event'
            }
    
    def _handle_delete_event(self, user_id: UUID, intent_data: Dict) -> Dict:
        """
        Handle event deletion
        """
        event_id_str = intent_data.get('event_id')
        if not event_id_str:
            return {
                'success': False,
                'message': "No event ID provided for deletion",
                'action': 'delete_event'
            }
        
        try:
            event_id = UUID(event_id_str)
        except ValueError:
            return {
                'success': False,
                'message': f"Invalid event ID: {event_id_str}",
                'action': 'delete_event'
            }
        
        success = delete_calendar_event(self.db, event_id)
        
        if success:
            return {
                'success': True,
                'message': f"Successfully deleted event",
                'action': 'delete_event'
            }
        else:
            return {
                'success': False,
                'message': f"Event not found: {event_id}",
                'action': 'delete_event'
            }
    
    def _handle_query_schedule(self, user_id: UUID, intent_data: Dict) -> Dict:
        """
        Handle schedule queries (list events, show calendar, etc.)
        """
        when = intent_data.get('when')
        
        if when == 'today':
            start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=1)
        elif when == 'tomorrow':
            start_date = (datetime.now() + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=1)
        elif when == 'this_week':
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            # Get Monday of this week
            days_since_monday = today.weekday()
            start_date = today - timedelta(days=days_since_monday)
            end_date = start_date + timedelta(days=7)
        elif when == 'next_week':
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            days_since_monday = today.weekday()
            start_date = today - timedelta(days=days_since_monday) + timedelta(days=7)
            end_date = start_date + timedelta(days=7)
        else:
            # Default: next 7 days
            start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=7)
        
        events = get_events_by_date_range(self.db, start_date, end_date, user_id=user_id)
        
        if not events:
            return {
                'success': True,
                'message': f"No events scheduled for the requested period",
                'events': [],
                'action': 'query_schedule'
            }
        
        # Format events for response
        events_data = [event.to_dict() for event in events]
        
        # Create a human-readable summary
        summary = f"You have {len(events)} event(s):\n\n"
        for event in events:
            start_str = event.start_time.strftime('%b %d, %I:%M %p')
            end_str = event.end_time.strftime('%I:%M %p')
            summary += f"• {event.task_title}\n"
            summary += f"  {start_str} - {end_str} | Priority: {event.priority_tag.value}\n"
            if event.description:
                summary += f"  Note: {event.description}\n"
            summary += "\n"
        
        return {
            'success': True,
            'message': summary,
            'events': events_data,
            'action': 'query_schedule',
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            }
        }
    
    def _parse_when(self, when: Optional[str]) -> datetime:
        """
        Parse 'when' string to a datetime object
        
        Args:
            when: String like "today", "tomorrow", "this_week", etc.
        
        Returns:
            Datetime object representing the preferred date
        """
        now = datetime.now()
        
        if when == 'today':
            return now
        elif when == 'tomorrow':
            return now + timedelta(days=1)
        elif when == 'this_week':
            return now
        elif when == 'next_week':
            return now + timedelta(days=7)
        else:
            # Default to ASAP (now)
            return now
