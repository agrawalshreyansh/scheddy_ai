#!/usr/bin/env python3
"""
Test script for the reschedule event feature.
Make sure the backend is running on http://localhost:8000

Usage:
    python test_reschedule.py <user_id>
"""

import requests
import sys
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_reschedule(user_id: str):
    """Test the reschedule event functionality"""
    
    print("🧪 Testing Reschedule Event Feature\n")
    print("=" * 60)
    
    # Test 1: Create an event first
    print("\n📝 Test 1: Creating a test event at 2pm...")
    create_response = requests.post(
        f"{BASE_URL}/chat/",
        json={
            "prompt": "Schedule a team meeting today at 2pm for 1 hour",
            "user_id": user_id,
            "temperature": 0.2
        }
    )
    
    if create_response.status_code == 200:
        result = create_response.json()
        print(f"✅ Created: {result.get('message', '')}")
    else:
        print(f"❌ Failed to create event: {create_response.text}")
        return
    
    # Wait a moment
    import time
    time.sleep(1)
    
    # Test 2: Reschedule by time
    print("\n📝 Test 2: Rescheduling 2pm meeting to 4pm...")
    reschedule_response = requests.post(
        f"{BASE_URL}/chat/",
        json={
            "prompt": "Reschedule my 2pm meeting to 4pm",
            "user_id": user_id,
            "temperature": 0.2
        }
    )
    
    if reschedule_response.status_code == 200:
        result = reschedule_response.json()
        print(f"✅ {result.get('message', '')}")
        if result.get('success'):
            print("   Event successfully rescheduled!")
        else:
            print(f"   ⚠️ Reschedule issue: {result.get('message')}")
    else:
        print(f"❌ Failed: {reschedule_response.text}")
    
    # Test 3: Create another event
    print("\n📝 Test 3: Creating a gym workout for today...")
    create_response2 = requests.post(
        f"{BASE_URL}/chat/",
        json={
            "prompt": "Schedule gym workout today for 1 hour",
            "user_id": user_id,
            "temperature": 0.2
        }
    )
    
    if create_response2.status_code == 200:
        result = create_response2.json()
        print(f"✅ Created: {result.get('message', '')}")
    else:
        print(f"❌ Failed to create event: {create_response2.text}")
    
    time.sleep(1)
    
    # Test 4: Reschedule by title
    print("\n📝 Test 4: Rescheduling gym workout to tomorrow...")
    reschedule_response2 = requests.post(
        f"{BASE_URL}/chat/",
        json={
            "prompt": "Move today's gym workout to tomorrow",
            "user_id": user_id,
            "temperature": 0.2
        }
    )
    
    if reschedule_response2.status_code == 200:
        result = reschedule_response2.json()
        print(f"✅ {result.get('message', '')}")
        if result.get('success'):
            print("   Event successfully rescheduled!")
        else:
            print(f"   ⚠️ Reschedule issue: {result.get('message')}")
    else:
        print(f"❌ Failed: {reschedule_response2.text}")
    
    # Test 5: Check schedule
    print("\n📝 Test 5: Checking today's schedule...")
    query_response = requests.post(
        f"{BASE_URL}/chat/",
        json={
            "prompt": "Show me today's schedule",
            "user_id": user_id,
            "temperature": 0.2
        }
    )
    
    if query_response.status_code == 200:
        result = query_response.json()
        print(f"📅 {result.get('message', '')}")
    else:
        print(f"❌ Failed to query schedule: {query_response.text}")
    
    # Test 6: Check tomorrow's schedule
    print("\n📝 Test 6: Checking tomorrow's schedule...")
    query_response2 = requests.post(
        f"{BASE_URL}/chat/",
        json={
            "prompt": "Show me tomorrow's schedule",
            "user_id": user_id,
            "temperature": 0.2
        }
    )
    
    if query_response2.status_code == 200:
        result = query_response2.json()
        print(f"📅 {result.get('message', '')}")
    else:
        print(f"❌ Failed to query schedule: {query_response2.text}")
    
    print("\n" + "=" * 60)
    print("✅ Test suite completed!\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_reschedule.py <user_id>")
        print("\nExample:")
        print("  python test_reschedule.py 123e4567-e89b-12d3-a456-426614174000")
        sys.exit(1)
    
    user_id = sys.argv[1]
    
    # Validate UUID format
    try:
        from uuid import UUID
        UUID(user_id)
    except ValueError:
        print(f"❌ Invalid user_id format: {user_id}")
        print("Please provide a valid UUID")
        sys.exit(1)
    
    test_reschedule(user_id)
