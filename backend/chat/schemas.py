from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from uuid import UUID


class ChatRequest(BaseModel):
    prompt: str = Field(..., description="The user's message to the AI assistant")
    user_id: UUID = Field(..., description="UUID of the user making the request")
    temperature: Optional[float] = Field(default=0.2, ge=0.0, le=2.0, description="Temperature for response generation")
    conversation_id: Optional[str] = Field(default=None, description="Optional conversation ID for multi-turn conversations")

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "I want to learn Python today for about 2 hours",
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "temperature": 0.2,
                "conversation_id": None
            }
        }

class ChatResponse(BaseModel):
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Human-readable response message")
    action: Optional[str] = Field(None, description="The action that was performed")
    event: Optional[Dict[str, Any]] = Field(None, description="Event data if an event was created/updated")
    events: Optional[List[Dict[str, Any]]] = Field(None, description="List of events for query operations")
    rescheduled_events: Optional[List[Dict[str, Any]]] = Field(None, description="Events that were rescheduled")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for multi-turn conversations")
    requires_response: Optional[bool] = Field(None, description="True if LLM is asking a clarifying question")
    missing_info: Optional[List[str]] = Field(None, description="Information needed from user")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Successfully scheduled 'Learn Python' from 2024-10-16 14:00 to 16:00",
                "action": "create_event",
                "event": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "task_title": "Learn Python",
                    "start_time": "2024-10-16T14:00:00",
                    "end_time": "2024-10-16T16:00:00"
                },
                "conversation_id": "1_1697469234.123",
                "requires_response": False
            }
        }

