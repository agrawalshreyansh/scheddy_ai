"""
Example usage script for the Scheddy AI Calendar Assistant
Run this after starting the server to test the functionality
"""
import requests
import json
from uuid import uuid4

# Configuration
BASE_URL = "http://localhost:8000"
USER_EMAIL = "test@example.com"
USER_NAME = "Test User"

def create_user():
    """Create a test user"""
    response = requests.post(
        f"{BASE_URL}/users/",
        json={
            "email": USER_EMAIL,
            "full_name": USER_NAME
        }
    )
    if response.status_code == 200:
        user = response.json()
        print(f"✅ Created user: {user['full_name']} (ID: {user['id']})")
        return user['id']
    else:
        print(f"❌ Failed to create user: {response.text}")
        return None

def chat_with_assistant(user_id, prompt):
    """Send a chat request to the assistant"""
    print(f"\n💬 User: {prompt}")
    print("-" * 60)
    
    response = requests.post(
        f"{BASE_URL}/chat/",
        json={
            "prompt": prompt,
            "user_id": user_id,
            "temperature": 0.2
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"🤖 Assistant: {result['message']}")
        
        if result.get('event'):
            event = result['event']
            print(f"\n📅 Event Details:")
            print(f"   Title: {event['task_title']}")
            print(f"   Time: {event['start_time']} to {event['end_time']}")
            print(f"   Priority: {event['priority_tag']} ({event['priority_number']})")
        
        if result.get('rescheduled_events'):
            print(f"\n🔄 Rescheduled Events:")
            for re in result['rescheduled_events']:
                print(f"   • {re['event_title']}")
                print(f"     {re['old_start']} → {re['new_start']}")
        
        return result
    else:
        print(f"❌ Error: {response.text}")
        return None

def main():
    """Run example scenarios"""
    print("=" * 60)
    print("🚀 Scheddy AI Calendar Assistant - Example Usage")
    print("=" * 60)
    
    # Create a user
    user_id = create_user()
    if not user_id:
        print("Failed to create user. Exiting.")
        return
    
    print("\n" + "=" * 60)
    print("📝 Example Scenarios")
    print("=" * 60)
    
    # Scenario 1: Schedule a regular task
    chat_with_assistant(
        user_id,
        "I want to watch Karpathy LLM video today for 1 hour"
    )
    
    # Scenario 2: Schedule a task for tomorrow
    chat_with_assistant(
        user_id,
        "I need to prepare for the meeting tomorrow, about 2 hours"
    )
    
    # Scenario 3: Schedule an urgent task
    chat_with_assistant(
        user_id,
        "Schedule a gym workout for 45 minutes, it's urgent and must be today"
    )
    
    # Scenario 4: Flexible scheduling
    chat_with_assistant(
        user_id,
        "I want to learn Python, maybe 1.5 hours when possible"
    )
    
    # Scenario 5: Another task today (might trigger rescheduling)
    chat_with_assistant(
        user_id,
        "I have to finish the report today, it will take 2 hours and it's high priority"
    )
    
    # Scenario 6: Query the schedule
    chat_with_assistant(
        user_id,
        "Show me my schedule for today"
    )
    
    # Scenario 7: Query tomorrow's schedule
    chat_with_assistant(
        user_id,
        "What do I have scheduled for tomorrow?"
    )
    
    print("\n" + "=" * 60)
    print("✨ Examples completed!")
    print("=" * 60)
    print(f"\n💡 Your user ID: {user_id}")
    print("You can now use this user ID to interact with the API.")

if __name__ == "__main__":
    main()
