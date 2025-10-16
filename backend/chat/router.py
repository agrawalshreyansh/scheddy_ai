from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from chat.schemas import ChatRequest, ChatResponse
from agents.enhanced_orchestrator import EnhancedCalendarOrchestrator
from db.database import get_db

router = APIRouter(
    prefix="/chat",
    tags=["chat"]
)

@router.post("/", response_model=ChatResponse)
async def chat_with_assistant(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Chat with the AI assistant for intelligent scheduling and task management.
    
    The assistant understands natural language and can:
    - Schedule tasks automatically finding the best time slots
    - Reschedule lower-priority tasks when needed
    - Handle priority-based scheduling
    - Schedule tasks for weekends
    - Track weekly goals
    - Manage work preferences
    - Query your calendar
    - Learn from past conversations and tasks (semantic search)
    - Ask clarifying questions when needed (multi-turn conversations)
    
    **New Features:**
    - **Semantic Search**: Finds similar past tasks and conversations
    - **Pattern Detection**: Recognizes recurring tasks and suggests durations
    - **Context-Aware**: Uses conversation history to make smarter suggestions
    - **Multi-Turn Conversations**: Can ask follow-up questions for clarity
    
    **Examples:**
    - "I want to watch Karpathy LLM video today for 1 hour"
    - "Schedule gym workout this weekend"
    - "I need to code for 3 hours this week"
    - "Show me my schedule for this weekend"
    - "What's my weekly goals progress?"
    
    **Multi-Turn Example:**
    1. User: "I want to learn something"
    2. Assistant: "What would you like to learn?" (returns conversation_id)
    3. User: "Python" (send same conversation_id)
    4. Assistant: Schedules "Learn Python"
    
    **Parameters:**
    - **prompt**: Your natural language instruction
    - **user_id**: Your user UUID
    - **temperature**: AI creativity level (0.0 = focused, 2.0 = creative, default: 0.2)
    - **conversation_id**: Optional, for continuing multi-turn conversations
    """
    try:
        # Create orchestrator instance
        orchestrator = EnhancedCalendarOrchestrator(db)
        
        # Process the user request with conversation context
        result = orchestrator.process_user_request(
            user_id=request.user_id,
            user_message=request.prompt,
            temperature=request.temperature,
            conversation_id=request.conversation_id
        )
        
        return ChatResponse(**result)
    
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error processing request: {str(e)}"
        )


