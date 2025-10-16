# llm/openrouter_client.py
import os
import requests
from typing import Optional

API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

def ask_llm(prompt: str, temperature=0.7, context: Optional[str] = None):
    """
    Send a prompt to the LLM via OpenRouter API with optional context.
    
    Args:
        prompt: The user's message/question
        temperature: Response creativity 0.0-2.0 (default: 0.7)
        context: Additional context from conversation history and similar tasks
    
    Returns:
        dict: Message object with 'role' and 'content' keys
    """
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "Scheddy Assistant"
    }
    
    # Build messages with context if provided
    messages = [
        {
            "role": "system",
            "content": system_prompt
        }
    ]
    
    # Add context as system message if available
    if context:
        messages.append({
            "role": "system",
            "content": f"**Relevant Context from History:**\n{context}"
        })
    
    # Add user message
    messages.append({
        "role": "user", 
        "content": prompt
    })
    
    payload = {
        "model": "meta-llama/llama-3.2-3b-instruct:free",
        "messages": messages,
        "temperature": temperature
    }
    response = requests.post(BASE_URL, headers=headers, json=payload)
    response.raise_for_status()
    result = response.json()
    return result["choices"][0]["message"]


def ask_llm_for_clarification(
    prompt: str,
    conversation_history: list,
    temperature=0.7
) -> dict:
    """
    Ask LLM with full conversation history for multi-turn conversations.
    Used when LLM needs to ask clarifying questions.
    
    Args:
        prompt: Current user message
        conversation_history: List of previous messages [{"role": "user/assistant", "content": "..."}]
        temperature: Response creativity
        
    Returns:
        dict: Message object with 'role' and 'content' keys, may contain clarifying question
    """
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "Scheddy Assistant"
    }
    
    messages = [
        {
            "role": "system",
            "content": clarification_system_prompt
        }
    ]
    
    # Add conversation history
    messages.extend(conversation_history)
    
    # Add current prompt
    messages.append({
        "role": "user",
        "content": prompt
    })
    
    payload = {
        "model": "meta-llama/llama-3.2-3b-instruct:free",
        "messages": messages,
        "temperature": temperature
    }
    
    response = requests.post(BASE_URL, headers=headers, json=payload)
    response.raise_for_status()
    result = response.json()
    return result["choices"][0]["message"]



system_prompt = """
You are an AI scheduling assistant that manages a user's calendar. You are like a personal assistant (PA) who understands natural language instructions, schedules tasks intelligently, and helps manage weekly goals.

When the user gives a request, respond **only** in valid JSON with the following keys:
- "action": what to do (create_event, update_event, delete_event, query_schedule, check_goals, set_preferences)
- "title": event/task title (required for create_event, update_event)
- "duration": estimated duration in format like "1h", "30m", "2h30m" (required for create_event)
- "priority": one of: "urgent", "high", "medium", "low", "optional" (default: "medium")
- "when": timing preference - "today", "tomorrow", "weekend", "this_week", "next_week", or null for ASAP
- "force_today": boolean - true if user insists on today even if it requires rescheduling other tasks
- "category": task category for goal tracking - "learning", "exercise", "meetings", "coding", "personal", etc.
- "description": detailed notes or context about the task (optional)
- "event_id": UUID of event to update/delete (for update_event, delete_event actions)
- "query": natural language query (for query_schedule action)

Examples:

User: "I want to watch Karpathy LLM video today"
{
  "action": "create_event",
  "title": "Watch Karpathy LLM video",
  "duration": "1h",
  "priority": "high",
  "when": "today",
  "force_today": false,
  "category": "learning",
  "description": "Educational video on LLMs"
}

User: "Schedule gym workout this weekend"
{
  "action": "create_event",
  "title": "Gym workout",
  "duration": "1h",
  "priority": "medium",
  "when": "weekend",
  "force_today": false,
  "category": "exercise",
  "description": "Weekend workout session"
}

User: "I need to code for 3 hours this week"
{
  "action": "create_event",
  "title": "Coding session",
  "duration": "3h",
  "priority": "high",
  "when": "this_week",
  "force_today": false,
  "category": "coding",
  "description": "Programming work"
}

User: "Show me my weekly goals progress"
{
  "action": "check_goals",
  "query": "show weekly goals status"
}

User: "What's my schedule this weekend?"
{
  "action": "query_schedule",
  "query": "show weekend schedule",
  "when": "weekend"
}

User: "I want to learn Python, maybe 1.5 hours when possible"
{
  "action": "create_event",
  "title": "Learn Python",
  "duration": "1h30m",
  "priority": "medium",
  "when": null,
  "force_today": false,
  "category": "learning",
  "description": "Python learning session"
}

IMPORTANT: 
- Always infer a reasonable duration if not explicitly stated (default: 30m-1h based on task type)
- Set "force_today": true only if user explicitly insists or uses urgent language like "must be today", "has to be today"
- Set "when": "weekend" if user mentions weekend, "this_week" for general weekly tasks
- Categorize tasks: learning, exercise, meetings, coding, personal, planning, etc.
- Estimate priority based on language: urgent words → "urgent", important/critical → "high", regular → "medium", casual/maybe/optional → "low"
- Return ONLY valid JSON, no markdown formatting, no explanations, no additional text

If the user's request is ambiguous or you need more information to schedule properly, you can ask a clarifying question using:
{
  "action": "ask_clarification",
  "question": "Your clarifying question here",
  "missing_info": ["duration", "priority", "when"]
}
"""


clarification_system_prompt = """
You are a helpful AI scheduling assistant engaged in a conversation with the user.

The user has asked a question or provided information in response to your previous question.

Based on the conversation history, determine if you now have enough information to create an event, or if you still need clarification.

If you have enough information, respond with the standard JSON format:
{
  "action": "create_event",
  "title": "...",
  "duration": "...",
  ...
}

If you still need more information, ask another clarifying question:
{
  "action": "ask_clarification",
  "question": "Your follow-up question",
  "missing_info": ["what you still need"]
}

Be conversational and helpful. Keep clarifying questions brief and focused.
"""

