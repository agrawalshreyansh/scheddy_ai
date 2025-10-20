"""
Enhanced Calendar Orchestrator with User Preferences and Weekly Goals
Now includes Qdrant-powered conversation memory and semantic search
"""
import json
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional
from sqlalchemy.orm import Session
from uuid import UUID
from agents.llm import ask_llm, ask_llm_for_clarification
from agents.smart_scheduler import SmartScheduler
from chat.conversation_memory import ConversationMemory
from users.preference_controllers import (
    get_or_create_user_preference,
    get_weekly_goal_status,
    get_remaining_goal_tasks,
    sync_weekly_goals_with_events,
    update_weekly_goal_progress,
    categorize_task
)
from events.controllers import (
    get_calendar_events,
    get_events_by_date_range,
    delete_calendar_event,
    update_calendar_event
)
from events.schemas import CalendarEventUpdate


class EnhancedCalendarOrchestrator:
    """
    Enhanced orchestrator with:
    - User preferences support
    - Weekly goal tracking
    - Smart scheduling with week context
    - Weekend scheduling
    - Qdrant-powered conversation memory
    - Semantic search over past conversations and tasks
    - Multi-turn conversation support
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.memory = ConversationMemory()
    
    def process_user_request(
        self,
        user_id: UUID,
        user_message: str,
        temperature: float = 0.2,
        conversation_id: Optional[str] = None,
        user_datetime: Optional[datetime] = None,
        user_timezone: Optional[str] = None
    ) -> Dict:
        """
        Process natural language request with preferences, goals, and conversation context.
        
        Args:
            user_id: User UUID
            user_message: User's natural language message
            temperature: LLM temperature
            conversation_id: Optional conversation ID for multi-turn conversations
            user_datetime: Current datetime from user's timezone (defaults to UTC now if not provided)
            user_timezone: User's timezone name (e.g., 'Asia/Kolkata', 'America/New_York')
            
        Returns:
            Dict with success, message, action, and relevant data
        """
        try:
            # Use user-provided datetime or fallback to UTC now
            if user_datetime is None:
                user_datetime = datetime.now(timezone.utc)
            # Ensure user_datetime is timezone-aware
            elif user_datetime.tzinfo is None:
                user_datetime = user_datetime.replace(tzinfo=timezone.utc)
            
            # Store user_datetime and user_timezone in instance for use in other methods
            self.user_datetime = user_datetime
            self.user_timezone = user_timezone
            # Build rich context from conversation history and similar tasks
            context = self.memory.get_conversation_context(
                user_id=user_id,
                current_query=user_message,
                db=self.db
            )
            
            # Check for recurring patterns
            pattern = self.memory.detect_recurring_pattern(
                user_id=user_id,
                task_title=user_message,
                category="general"
            )
            
            # Add pattern info to context if detected
            if pattern and pattern['is_recurring']:
                context += f"\n\n💡 **Suggestion**: This appears to be a recurring task (done {pattern['occurrences']} times). Consider: {pattern['suggested_duration_minutes']}min duration."
            
            # If conversation_id provided, get recent conversation for multi-turn
            conversation_history = []
            if conversation_id:
                recent_messages = self.memory.get_recent_conversation(
                    user_id=user_id,
                    conversation_id=conversation_id,
                    limit=5
                )
                conversation_history = [
                    {"role": msg["role"], "content": msg["content"]}
                    for msg in recent_messages
                ]
            
            # Extract intent using LLM with context
            if conversation_history:
                # Multi-turn conversation
                llm_response = ask_llm_for_clarification(
                    prompt=user_message,
                    conversation_history=conversation_history,
                    temperature=temperature
                )
            else:
                # First message or standalone query
                llm_response = ask_llm(
                    prompt=user_message,
                    temperature=temperature,
                    context=context if context else None
                )
            
            # Store user message in Qdrant
            conv_id = conversation_id or self.memory.store_message(
                user_id=user_id,
                role="user",
                content=user_message,
                conversation_id=None
            )
            
            # Parse JSON response
            try:
                intent_data = json.loads(llm_response['content'])
            except json.JSONDecodeError as e:
                # Store assistant error response
                error_msg = f"Could not understand the request. Please try rephrasing."
                self.memory.store_message(
                    user_id=user_id,
                    role="assistant",
                    content=error_msg,
                    conversation_id=conv_id
                )
                return {
                    'success': False,
                    'message': error_msg,
                    'error': f"JSON parse error: {str(e)}",
                    'llm_response': llm_response['content'],
                    'conversation_id': conv_id
                }
            
            # Check if LLM is asking for clarification
            action = intent_data.get('action', '').lower()
            
            if action == 'ask_clarification':
                question = intent_data.get('question', 'Could you provide more details?')
                # Store clarification question
                self.memory.store_message(
                    user_id=user_id,
                    role="assistant",
                    content=question,
                    intent_data=intent_data,
                    conversation_id=conv_id
                )
                return {
                    'success': True,
                    'message': question,
                    'action': 'ask_clarification',
                    'missing_info': intent_data.get('missing_info', []),
                    'conversation_id': conv_id,
                    'requires_response': True
                }
            
            # Store intent data with user message
            self.memory.store_message(
                user_id=user_id,
                role="user",
                content=user_message,
                intent_data=intent_data,
                conversation_id=conv_id
            )
            
            # Execute action based on intent
            if action == 'create_event':
                result = self._handle_create_event(user_id, intent_data, self.user_datetime)
            elif action == 'update_event':
                result = self._handle_update_event(user_id, intent_data, self.user_datetime)
            elif action == 'reschedule_event':
                result = self._handle_reschedule_event(user_id, intent_data, self.user_datetime)
            elif action in ['delete_event', 'remove_events', 'remove_event', 'delete_events']:
                result = self._handle_delete_event(user_id, intent_data, self.user_datetime)
            elif action in ['list_events', 'query_schedule']:
                result = self._handle_query_schedule(user_id, intent_data, self.user_datetime)
            elif action == 'check_goals':
                result = self._handle_check_goals(user_id)
            elif action == 'set_preferences':
                result = self._handle_set_preferences(user_id, intent_data)
            else:
                result = {
                    'success': False,
                    'message': f"Unknown action: {action}",
                    'intent_data': intent_data
                }
            
            # Store assistant response in Qdrant
            self.memory.store_message(
                user_id=user_id,
                role="assistant",
                content=result.get('message', ''),
                intent_data=result,
                conversation_id=conv_id
            )
            
            # Add conversation_id to result
            result['conversation_id'] = conv_id
            
            return result
        
        except Exception as e:
            error_msg = f"Error processing request: {str(e)}"
            return {
                'success': False,
                'message': error_msg,
                'error': str(e)
            }
    
    def _handle_create_event(self, user_id: UUID, intent_data: Dict, user_datetime: datetime) -> Dict:
        """Handle event creation with smart scheduling"""
        # Extract data from intent with type safety
        title = str(intent_data.get('title', 'Untitled Task'))
        duration_str = str(intent_data.get('duration', '1h'))
        priority_str = str(intent_data.get('priority', 'medium'))
        when = intent_data.get('when')
        description = intent_data.get('description')
        category = str(intent_data.get('category', 'general'))
        preferred_time = intent_data.get('preferred_time')
        
        # Ensure when is also properly typed
        if when is not None and not isinstance(when, str):
            when = str(when)
        
        # Ensure description is string or None
        if description is not None and not isinstance(description, str):
            description = str(description)
        
        # Ensure preferred_time is string or None
        if preferred_time is not None and not isinstance(preferred_time, str):
            preferred_time = str(preferred_time)
        
        # Create smart scheduler instance with user_datetime and user_timezone
        scheduler = SmartScheduler(self.db, user_id, user_datetime, self.user_timezone)
        
        # Parse duration
        duration_minutes = scheduler.parse_duration(duration_str)
        
        # Get priority
        priority_number, priority_tag = scheduler.get_priority_number_from_tag(priority_str)
        
        # Auto-detect category if not provided
        if category == 'general':
            category = categorize_task(title, description)
        
        # Schedule the task
        result = scheduler.schedule_with_context(
            task_title=title,
            duration_minutes=duration_minutes,
            priority_number=priority_number,
            priority_tag=priority_tag,
            when=when,
            description=description,
            category=category,
            preferred_time=preferred_time
        )
        
        if result['success']:
            # Update weekly goal progress
            hours = duration_minutes / 60
            update_weekly_goal_progress(self.db, user_id, category, hours)
            
            # Sync goals with actual events
            sync_weekly_goals_with_events(self.db, user_id)
            
            # Store scheduled task in Qdrant for future similarity search
            if result.get('event'):
                event = result['event']
                # Ensure event_id is properly converted
                event_id_val = event['id']
                if isinstance(event_id_val, UUID):
                    event_uuid = event_id_val
                else:
                    event_uuid = UUID(str(event_id_val))
                
                self.memory.store_scheduled_task(
                    user_id=user_id,
                    event_id=event_uuid,
                    title=title,
                    description=description,
                    category=category,
                    priority=priority_number,
                    start_time=datetime.fromisoformat(event['start_time']),
                    duration_minutes=duration_minutes
                )
            
            # Add goal progress info to response
            result['goal_updated'] = True
            result['category'] = category
        
        result['action'] = 'create_event'
        return result
    
    def _handle_update_event(self, user_id: UUID, intent_data: Dict, user_datetime: datetime) -> Dict:
        """Handle event updates"""
        event_id_str = intent_data.get('event_id')
        if not event_id_str:
            return {
                'success': False,
                'message': "No event ID provided for update",
                'action': 'update_event'
            }
        
        try:
            # Ensure event_id_str is properly typed
            event_id = UUID(str(event_id_str))
        except (ValueError, AttributeError) as e:
            return {
                'success': False,
                'message': f"Invalid event ID: {event_id_str}",
                'action': 'update_event'
            }
        
        # Build update data
        scheduler = SmartScheduler(self.db, user_id, user_datetime, self.user_timezone)
        update_data = {}
        
        if 'title' in intent_data:
            update_data['task_title'] = str(intent_data['title'])
        
        if 'description' in intent_data:
            update_data['description'] = str(intent_data['description'])
        
        if 'priority' in intent_data:
            priority_number, priority_tag = scheduler.get_priority_number_from_tag(
                str(intent_data['priority'])
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
            # Resync goals
            sync_weekly_goals_with_events(self.db, user_id)
            
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
    
    def _handle_reschedule_event(self, user_id: UUID, intent_data: Dict, user_datetime: datetime) -> Dict:
        """
        Handle event rescheduling by finding the event based on title and/or time,
        then rescheduling it to a new time.
        """
        title = intent_data.get('title')
        original_time = intent_data.get('original_time')
        new_time = intent_data.get('new_time')
        when = intent_data.get('when')
        
        # Ensure parameters are properly typed
        if title is not None and not isinstance(title, str):
            title = str(title)
        if original_time is not None and not isinstance(original_time, str):
            original_time = str(original_time)
        if new_time is not None and not isinstance(new_time, str):
            new_time = str(new_time)
        if when is not None and not isinstance(when, str):
            when = str(when)
        
        if not title and not original_time:
            return {
                'success': False,
                'message': "Please specify which event to reschedule (by title or time)",
                'action': 'reschedule_event'
            }
        
        if not new_time:
            return {
                'success': False,
                'message': "Please specify when to reschedule to",
                'action': 'reschedule_event'
            }
        
        # Find the event(s) to reschedule
        scheduler = SmartScheduler(self.db, user_id, user_datetime, self.user_timezone)
        
        # Determine search date range based on original_time
        if original_time:
            if 'today' in original_time.lower() or when == 'today':
                start_date = user_datetime.replace(hour=0, minute=0, second=0, microsecond=0)
                end_date = start_date + timedelta(days=1)
            elif 'tomorrow' in original_time.lower() or when == 'tomorrow':
                start_date = (user_datetime + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
                end_date = start_date + timedelta(days=1)
            elif 'morning' in original_time.lower():
                start_date = user_datetime.replace(hour=0, minute=0, second=0, microsecond=0)
                end_date = user_datetime.replace(hour=12, minute=0, second=0, microsecond=0)
            elif 'afternoon' in original_time.lower():
                start_date = user_datetime.replace(hour=12, minute=0, second=0, microsecond=0)
                end_date = user_datetime.replace(hour=17, minute=0, second=0, microsecond=0)
            elif 'evening' in original_time.lower():
                start_date = user_datetime.replace(hour=17, minute=0, second=0, microsecond=0)
                end_date = user_datetime.replace(hour=23, minute=59, second=59, microsecond=0)
            else:
                # Try to parse specific time (e.g., "2pm", "14:00")
                try:
                    temp_scheduler = SmartScheduler(self.db, user_id, user_datetime, self.user_timezone)
                    specific_time = temp_scheduler.parse_time_string(original_time, user_datetime)
                    if specific_time:
                        # Search within ±30 minutes of the specified time
                        start_date = specific_time - timedelta(minutes=30)
                        end_date = specific_time + timedelta(minutes=30)
                    else:
                        # Default to today
                        start_date = user_datetime.replace(hour=0, minute=0, second=0, microsecond=0)
                        end_date = start_date + timedelta(days=1)
                except Exception as e:
                    # Default to today
                    start_date = user_datetime.replace(hour=0, minute=0, second=0, microsecond=0)
                    end_date = start_date + timedelta(days=1)
        else:
            # Default to today if no time specified
            start_date = user_datetime.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=7)
        
        # Get events in the range
        events = get_events_by_date_range(self.db, start_date, end_date, user_id=user_id)
        
        # Filter by title if provided
        if title:
            events = [e for e in events if title.lower() in e.task_title.lower()]
        
        if not events:
            return {
                'success': False,
                'message': f"No event found matching '{title}' at '{original_time}'",
                'action': 'reschedule_event'
            }
        
        if len(events) > 1:
            # Multiple matches - ask user to be more specific
            event_list = "\n".join([f"• {e.task_title} at {e.start_time.strftime('%I:%M %p')}" for e in events[:5]])
            return {
                'success': False,
                'message': f"Found {len(events)} events matching your criteria:\n{event_list}\n\nPlease be more specific.",
                'events': [e.to_dict() for e in events[:5]],
                'action': 'reschedule_event'
            }
        
        # Found exactly one event - reschedule it
        event_to_reschedule = events[0]
        original_duration = (event_to_reschedule.end_time - event_to_reschedule.start_time).total_seconds() / 60
        
        # Parse the new time and schedule
        # Determine new preferred time and when
        new_preferred_time = None
        new_when = None
        
        if 'tomorrow' in new_time.lower():
            new_when = 'tomorrow'
        elif 'today' in new_time.lower():
            new_when = 'today'
        elif 'weekend' in new_time.lower():
            new_when = 'weekend'
        elif 'next week' in new_time.lower() or 'next_week' in new_time.lower():
            new_when = 'next_week'
        elif 'this week' in new_time.lower() or 'this_week' in new_time.lower():
            new_when = 'this_week'
        else:
            # Try to parse as specific time
            try:
                new_preferred_time = new_time
                new_when = 'today'  # Default to today if specific time given
            except:
                new_when = None
        
        # Delete the old event
        delete_calendar_event(self.db, event_to_reschedule.id)
        
        # Create new event with same details but new time
        result = scheduler.schedule_with_context(
            task_title=event_to_reschedule.task_title,
            duration_minutes=int(original_duration),
            priority_number=event_to_reschedule.priority_number,
            priority_tag=event_to_reschedule.priority_tag.value if hasattr(event_to_reschedule.priority_tag, 'value') else str(event_to_reschedule.priority_tag),
            when=new_when,
            description=event_to_reschedule.description,
            category=intent_data.get('category', 'general'),
            preferred_time=new_preferred_time
        )
        
        if result['success']:
            # Store rescheduled task in Qdrant
            if result.get('event'):
                event = result['event']
                event_id_val = event['id']
                if isinstance(event_id_val, UUID):
                    event_uuid = event_id_val
                else:
                    event_uuid = UUID(str(event_id_val))
                
                self.memory.store_scheduled_task(
                    user_id=user_id,
                    event_id=event_uuid,
                    title=event_to_reschedule.task_title,
                    description=event_to_reschedule.description,
                    category=intent_data.get('category', 'general'),
                    priority=event_to_reschedule.priority_number,
                    start_time=datetime.fromisoformat(event['start_time']),
                    duration_minutes=int(original_duration)
                )
            
            result['message'] = f"✅ Rescheduled '{event_to_reschedule.task_title}' to {result.get('message', 'new time')}"
            result['action'] = 'reschedule_event'
            return result
        else:
            # If rescheduling failed, restore the original event
            from events.schemas import CalendarEventCreate
            restore_event = CalendarEventCreate(
                task_title=event_to_reschedule.task_title,
                description=event_to_reschedule.description,
                start_time=event_to_reschedule.start_time,
                end_time=event_to_reschedule.end_time,
                priority_number=event_to_reschedule.priority_number,
                priority_tag=event_to_reschedule.priority_tag,
                user_id=user_id
            )
            from events.controllers import create_calendar_event
            create_calendar_event(self.db, restore_event)
            
            return {
                'success': False,
                'message': f"Could not reschedule '{event_to_reschedule.task_title}'. {result.get('message', 'No available slots found.')}",
                'action': 'reschedule_event'
            }
    
    def _handle_delete_event(self, user_id: UUID, intent_data: Dict, user_datetime: datetime) -> Dict:
        """Handle event deletion"""
        event_id_str = intent_data.get('event_id')
        task_title = intent_data.get('title')
        when = intent_data.get('when')
        
        # Ensure task_title and when are properly typed if present
        if task_title is not None and not isinstance(task_title, str):
            task_title = str(task_title)
        if when is not None and not isinstance(when, str):
            when = str(when)
        
        # Case 1: Specific event ID provided
        if event_id_str:
            try:
                # Ensure event_id_str is properly typed
                event_id = UUID(str(event_id_str))
            except (ValueError, AttributeError) as e:
                return {
                    'success': False,
                    'message': f"Invalid event ID: {event_id_str}",
                    'action': 'delete_event'
                }
            
            success = delete_calendar_event(self.db, event_id)
            
            if success:
                sync_weekly_goals_with_events(self.db, user_id)
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
        
        # Case 2: Delete by title or time range
        elif task_title or when:
            # Get events to delete
            if when:
                scheduler = SmartScheduler(self.db, user_id, user_datetime, self.user_timezone)
                if when == 'today':
                    start_date = user_datetime.replace(hour=0, minute=0, second=0, microsecond=0)
                    end_date = start_date + timedelta(days=1)
                elif when == 'tomorrow':
                    start_date = (user_datetime + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
                    end_date = start_date + timedelta(days=1)
                else:
                    start_date = user_datetime.replace(hour=0, minute=0, second=0, microsecond=0)
                    end_date = start_date + timedelta(days=7)
                
                events = get_events_by_date_range(self.db, start_date, end_date, user_id=user_id)
            else:
                # Get all user events
                events = get_calendar_events(self.db, user_id=user_id)
            
            # Filter by title if provided
            if task_title:
                events = [e for e in events if task_title.lower() in e.task_title.lower()]
            
            if not events:
                return {
                    'success': False,
                    'message': f"No events found matching your criteria",
                    'action': 'delete_event'
                }
            
            # Delete all matching events
            deleted_count = 0
            for event in events:
                if delete_calendar_event(self.db, event.id):
                    deleted_count += 1
            
            sync_weekly_goals_with_events(self.db, user_id)
            
            return {
                'success': True,
                'message': f"Successfully deleted {deleted_count} event(s)",
                'action': 'delete_event',
                'deleted_count': deleted_count
            }
        
        # Case 3: No identifiable information provided
        else:
            return {
                'success': False,
                'message': "Please specify which event(s) to delete (by title, time, or event ID)",
                'action': 'delete_event'
            }
    
    def _handle_query_schedule(self, user_id: UUID, intent_data: Dict, user_datetime: datetime) -> Dict:
        """Handle schedule queries including weekend"""
        when = intent_data.get('when')
        # Ensure when is properly typed
        if when is not None and not isinstance(when, str):
            when = str(when)
        
        scheduler = SmartScheduler(self.db, user_id, user_datetime, self.user_timezone)
        
        if when == 'today':
            start_date = user_datetime.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=1)
        elif when == 'tomorrow':
            start_date = (user_datetime + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=1)
        elif when == 'weekend':
            weekend_start, weekend_end = scheduler.get_next_weekend()
            start_date = weekend_start.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = weekend_end.replace(hour=23, minute=59, second=59)
        elif when == 'this_week':
            from users.preference_controllers import get_week_start_end
            start_date, end_date = get_week_start_end()
        elif when == 'next_week':
            from users.preference_controllers import get_week_identifier
            current_week = get_week_identifier(user_datetime)
            year, week = current_week.split('-W')
            next_week_id = f"{year}-W{int(week)+1:02d}"
            from users.preference_controllers import get_week_start_end
            start_date, end_date = get_week_start_end(next_week_id)
        else:
            # Default: next 7 days
            start_date = user_datetime.replace(hour=0, minute=0, second=0, microsecond=0)
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
        
        # Create a human-readable summary with times in user's timezone
        summary = f"You have {len(events)} event(s):\n\n"
        for event in events:
            # Convert event times from UTC to user's timezone for display
            start_time_user_tz = event.start_time.astimezone(scheduler.user_timezone)
            end_time_user_tz = event.end_time.astimezone(scheduler.user_timezone)
            
            start_str = start_time_user_tz.strftime('%a %b %d, %I:%M %p')
            end_str = end_time_user_tz.strftime('%I:%M %p')
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
    
    def _handle_check_goals(self, user_id: UUID) -> Dict:
        """Handle weekly goals check"""
        # Sync goals with current events first
        sync_weekly_goals_with_events(self.db, user_id)
        
        # Get goal status
        goal_trackers = get_weekly_goal_status(self.db, user_id)
        
        if not goal_trackers:
            return {
                'success': True,
                'message': "No weekly goals set. You can set goals in your preferences.",
                'goals': [],
                'action': 'check_goals'
            }
        
        # Format goals
        goals_data = [tracker.to_dict() for tracker in goal_trackers]
        
        # Create summary
        summary = "📊 Weekly Goals Progress:\n\n"
        for tracker in goal_trackers:
            progress = tracker.get_progress_percentage()
            status_emoji = "✅" if tracker.is_complete() else "🔄"
            
            summary += f"{status_emoji} {tracker.category.title()}: "
            summary += f"{tracker.completed_hours}h / {tracker.goal_hours}h ({progress:.0f}%)\n"
            
            if not tracker.is_complete():
                summary += f"   Remaining: {tracker.remaining_hours()}h\n"
            summary += "\n"
        
        # Add remaining tasks suggestions
        remaining = get_remaining_goal_tasks(self.db, user_id)
        if remaining:
            summary += "\n💡 To meet your goals, schedule:\n"
            for item in remaining:
                summary += f"   • {item['remaining_hours']}h of {item['category']}\n"
        
        return {
            'success': True,
            'message': summary,
            'goals': goals_data,
            'action': 'check_goals'
        }
    
    def _handle_set_preferences(self, user_id: UUID, intent_data: Dict) -> Dict:
        """Handle setting user preferences"""
        # This would be implemented to update user preferences
        # For now, return a message
        return {
            'success': True,
            'message': "Preference setting via chat is coming soon. Please use the API endpoints.",
            'action': 'set_preferences'
        }
