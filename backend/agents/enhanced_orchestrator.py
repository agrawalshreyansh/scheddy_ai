"""
Enhanced Calendar Orchestrator with User Preferences and Weekly Goals
Now includes Qdrant-powered conversation memory and semantic search
"""
import json
from datetime import datetime, timedelta
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
        conversation_id: Optional[str] = None
    ) -> Dict:
        """
        Process natural language request with preferences, goals, and conversation context.
        
        Args:
            user_id: User UUID
            user_message: User's natural language message
            temperature: LLM temperature
            conversation_id: Optional conversation ID for multi-turn conversations
            
        Returns:
            Dict with success, message, action, and relevant data
        """
        try:
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
                result = self._handle_create_event(user_id, intent_data)
            elif action == 'update_event':
                result = self._handle_update_event(user_id, intent_data)
            elif action == 'delete_event':
                result = self._handle_delete_event(user_id, intent_data)
            elif action in ['list_events', 'query_schedule']:
                result = self._handle_query_schedule(user_id, intent_data)
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
    
    def _handle_create_event(self, user_id: UUID, intent_data: Dict) -> Dict:
        """Handle event creation with smart scheduling"""
        # Extract data from intent
        title = intent_data.get('title', 'Untitled Task')
        duration_str = intent_data.get('duration', '1h')
        priority_str = intent_data.get('priority', 'medium')
        when = intent_data.get('when')
        description = intent_data.get('description')
        category = intent_data.get('category', 'general')
        
        # Create smart scheduler instance
        scheduler = SmartScheduler(self.db, user_id)
        
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
            category=category
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
                self.memory.store_scheduled_task(
                    user_id=user_id,
                    event_id=UUID(event['id']),
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
    
    def _handle_update_event(self, user_id: UUID, intent_data: Dict) -> Dict:
        """Handle event updates"""
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
        scheduler = SmartScheduler(self.db, user_id)
        update_data = {}
        
        if 'title' in intent_data:
            update_data['task_title'] = intent_data['title']
        
        if 'description' in intent_data:
            update_data['description'] = intent_data['description']
        
        if 'priority' in intent_data:
            priority_number, priority_tag = scheduler.get_priority_number_from_tag(
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
    
    def _handle_delete_event(self, user_id: UUID, intent_data: Dict) -> Dict:
        """Handle event deletion"""
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
            # Resync goals
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
    
    def _handle_query_schedule(self, user_id: UUID, intent_data: Dict) -> Dict:
        """Handle schedule queries including weekend"""
        when = intent_data.get('when')
        scheduler = SmartScheduler(self.db, user_id)
        
        if when == 'today':
            start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=1)
        elif when == 'tomorrow':
            start_date = (datetime.now() + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
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
            current_week = get_week_identifier()
            year, week = current_week.split('-W')
            next_week_id = f"{year}-W{int(week)+1:02d}"
            from users.preference_controllers import get_week_start_end
            start_date, end_date = get_week_start_end(next_week_id)
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
            start_str = event.start_time.strftime('%a %b %d, %I:%M %p')
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
