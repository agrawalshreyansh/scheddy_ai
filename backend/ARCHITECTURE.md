# SCHEDDY - AI CALENDAR ASSISTANT
## Complete Application Architecture & Flow Documentation

---

## TABLE OF CONTENTS

1. [System Overview](#system-overview)
2. [Application Flow](#application-flow)
3. [Database Schema](#database-schema)
4. [API Endpoints](#api-endpoints)
5. [Frontend Integration Guide](#frontend-integration-guide)
6. [Chat Message Types](#chat-message-types)
7. [Data Flow Diagrams](#data-flow-diagrams)
8. [Component Architecture](#component-architecture)
9. [Setup & Configuration](#setup--configuration)

---

## SYSTEM OVERVIEW

### Tech Stack
```
Backend:     FastAPI (Python 3.10+)
Database:    PostgreSQL + SQLAlchemy ORM
Vector DB:   Qdrant (Semantic Search & Embeddings)
LLM:         Meta Llama 3.2 (via OpenRouter API)
Embeddings:  sentence-transformers (via HuggingFace API)
```

### Core Capabilities
- Natural language task scheduling
- Semantic search over conversation history
- Pattern recognition for recurring tasks
- Multi-turn conversations with clarifications
- Auto-rescheduling based on priority
- Weekly goal tracking
- User preference management
- Weekend and week-aware scheduling

---

## APPLICATION FLOW

### 1. USER ONBOARDING FLOW

```
┌─────────────────────────────────────────────────────────────┐
│ STEP 1: Create User Account                                │
├─────────────────────────────────────────────────────────────┤
│ Frontend Action: User fills registration form              │
│ API Call: POST /users/                                     │
│ Input: { email, full_name }                                │
│ Response: { id, email, full_name, created_at }             │
│ ⚠️  IMPORTANT: Save user.id for all future requests        │
└─────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 2: Set User Preferences (Optional but Recommended)    │
├─────────────────────────────────────────────────────────────┤
│ Frontend Action: User configures work hours & preferences  │
│ API Call: PUT /preferences/{user_id}                       │
│ Input: {                                                    │
│   work_start_hour: 9,           # 0-23                     │
│   work_start_minute: 0,         # 0-59                     │
│   work_end_hour: 18,            # 0-23                     │
│   work_end_minute: 0,           # 0-59                     │
│   work_days: [0,1,2,3,4],       # 0=Mon, 6=Sun            │
│   prefer_morning: true,         # Prefer AM slots          │
│   lunch_break_hour: 12,                                    │
│   lunch_break_minute: 0,                                   │
│   lunch_break_duration: 60,     # minutes                  │
│   min_break_between_tasks: 5,   # minutes                  │
│   max_tasks_per_day: 10,                                   │
│   allow_auto_reschedule: true                              │
│ }                                                           │
│ Response: Updated preference object                         │
└─────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 3: Set Weekly Goals (Optional)                        │
├─────────────────────────────────────────────────────────────┤
│ Frontend Action: User sets weekly hour targets             │
│ API Call: PUT /preferences/{user_id}/weekly-goals          │
│ Input: {                                                    │
│   weekly_goals: {                                          │
│     learning: 5,      # hours per week                     │
│     exercise: 3,                                           │
│     meetings: 10,                                          │
│     coding: 15,                                            │
│     personal: 5,                                           │
│     planning: 3                                            │
│   }                                                         │
│ }                                                           │
│ Response: Updated preference with goals                     │
└─────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 4: Start Chatting                                     │
│ User can now interact via natural language                  │
└─────────────────────────────────────────────────────────────┘
```

### 2. CHAT INTERACTION FLOW

```
┌──────────────────────────────────────────────────────────────┐
│ USER SENDS MESSAGE                                           │
├──────────────────────────────────────────────────────────────┤
│ Frontend: User types in chat interface                       │
│ Example: "I want to learn React for 2 hours today"          │
└──────────────────────────────────────────────────────────────┘
         ↓
┌──────────────────────────────────────────────────────────────┐
│ FRONTEND → BACKEND                                           │
├──────────────────────────────────────────────────────────────┤
│ API Call: POST /chat/                                        │
│ Request Body: {                                              │
│   user_id: "uuid-of-user",                                  │
│   prompt: "I want to learn React for 2 hours today",        │
│   temperature: 0.2,  # Optional (0.0-2.0)                   │
│   conversation_id: null  # null for new, or ID for follow-up│
│ }                                                            │
└──────────────────────────────────────────────────────────────┘
         ↓
┌──────────────────────────────────────────────────────────────┐
│ BACKEND PROCESSING (Enhanced Orchestrator)                   │
├──────────────────────────────────────────────────────────────┤
│ STEP 1: Build Context from Qdrant                           │
│   - Search similar past conversations (top 2)               │
│   - Search similar scheduled tasks (top 2)                  │
│   - Detect recurring patterns                               │
│   - Get upcoming schedule summary                           │
│                                                              │
│ STEP 2: Call LLM with Context                               │
│   - Send user message + context to LLM                      │
│   - LLM extracts intent as JSON                             │
│                                                              │
│ STEP 3: Execute Action                                      │
│   - Parse intent JSON                                       │
│   - Route to appropriate handler                            │
│                                                              │
│ STEP 4: Store in Qdrant                                     │
│   - Store user message with embedding                       │
│   - Store assistant response with embedding                 │
│   - Store scheduled task (if created)                       │
└──────────────────────────────────────────────────────────────┘
         ↓
┌──────────────────────────────────────────────────────────────┐
│ BACKEND → FRONTEND                                           │
├──────────────────────────────────────────────────────────────┤
│ Response: {                                                  │
│   success: true,                                             │
│   message: "✅ Scheduled 'Learn React' from 2:00-4:00 PM",  │
│   action: "create_event",                                   │
│   conversation_id: "user_id_timestamp",                     │
│   requires_response: false,  # true if asking question      │
│   event: { /* event details */ },                           │
│   events: [ /* for queries */ ],                            │
│   rescheduled_events: [ /* if any moved */ ]                │
│ }                                                            │
└──────────────────────────────────────────────────────────────┘
         ↓
┌──────────────────────────────────────────────────────────────┐
│ FRONTEND DISPLAYS RESULT                                     │
├──────────────────────────────────────────────────────────────┤
│ - Show message to user                                       │
│ - Update calendar view if event created                     │
│ - Store conversation_id if requires_response = true          │
└──────────────────────────────────────────────────────────────┘
```

### 3. MULTI-TURN CONVERSATION FLOW

```
┌──────────────────────────────────────────────────────────────┐
│ TURN 1: Vague User Request                                  │
├──────────────────────────────────────────────────────────────┤
│ User: "Schedule something"                                   │
│                                                              │
│ POST /chat/                                                  │
│ {                                                            │
│   user_id: "uuid",                                          │
│   prompt: "Schedule something",                             │
│   conversation_id: null                                     │
│ }                                                            │
└──────────────────────────────────────────────────────────────┘
         ↓
┌──────────────────────────────────────────────────────────────┐
│ ASSISTANT ASKS CLARIFICATION                                 │
├──────────────────────────────────────────────────────────────┤
│ Response: {                                                  │
│   success: true,                                             │
│   message: "What would you like to schedule?",              │
│   action: "ask_clarification",                              │
│   conversation_id: "user_123_1697469234.123",  ⭐ SAVE THIS │
│   requires_response: true,  ⭐ IMPORTANT                     │
│   missing_info: ["title", "duration"]                       │
│ }                                                            │
│                                                              │
│ Frontend: Display message, keep chat input active           │
└──────────────────────────────────────────────────────────────┘
         ↓
┌──────────────────────────────────────────────────────────────┐
│ TURN 2: User Provides Details                               │
├──────────────────────────────────────────────────────────────┤
│ User: "A team meeting for 30 minutes"                        │
│                                                              │
│ POST /chat/                                                  │
│ {                                                            │
│   user_id: "uuid",                                          │
│   prompt: "A team meeting for 30 minutes",                  │
│   conversation_id: "user_123_1697469234.123"  ⭐ USE SAVED  │
│ }                                                            │
└──────────────────────────────────────────────────────────────┘
         ↓
┌──────────────────────────────────────────────────────────────┐
│ ASSISTANT CREATES EVENT                                      │
├──────────────────────────────────────────────────────────────┤
│ Response: {                                                  │
│   success: true,                                             │
│   message: "✅ Scheduled 'Team meeting'...",                │
│   action: "create_event",                                   │
│   conversation_id: "user_123_1697469234.123",               │
│   requires_response: false,  ⭐ Conversation complete        │
│   event: { /* event details */ }                            │
│ }                                                            │
│                                                              │
│ Frontend: Display result, clear conversation_id             │
└──────────────────────────────────────────────────────────────┘
```

---

## DATABASE SCHEMA

### PostgreSQL Tables

#### 1. **users** Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### 2. **user_preferences** Table
```sql
CREATE TABLE user_preferences (
    id SERIAL PRIMARY KEY,
    user_id UUID UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    work_start_hour INTEGER DEFAULT 9,
    work_start_minute INTEGER DEFAULT 0,
    work_end_hour INTEGER DEFAULT 18,
    work_end_minute INTEGER DEFAULT 0,
    work_days INTEGER[] DEFAULT ARRAY[0,1,2,3,4],  -- 0=Mon
    prefer_morning BOOLEAN DEFAULT true,
    lunch_break_hour INTEGER DEFAULT 12,
    lunch_break_minute INTEGER DEFAULT 0,
    lunch_break_duration INTEGER DEFAULT 60,
    min_break_between_tasks INTEGER DEFAULT 5,
    max_tasks_per_day INTEGER DEFAULT 10,
    allow_auto_reschedule BOOLEAN DEFAULT true,
    weekly_goals JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**weekly_goals JSON structure:**
```json
{
  "learning": 5,
  "exercise": 3,
  "meetings": 10,
  "coding": 15,
  "personal": 5,
  "planning": 3
}
```

#### 3. **calendar_events** Table
```sql
CREATE TABLE calendar_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    task_title VARCHAR(500) NOT NULL,
    description TEXT,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    priority_number INTEGER DEFAULT 5,
    priority_tag VARCHAR(50),  -- urgent, high, medium, low, optional
    category VARCHAR(100),  -- learning, exercise, meetings, etc.
    status VARCHAR(50) DEFAULT 'scheduled',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_user_events ON calendar_events(user_id, start_time);
CREATE INDEX idx_event_date_range ON calendar_events(start_time, end_time);
```

#### 4. **weekly_goal_trackers** Table
```sql
CREATE TABLE weekly_goal_trackers (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    week_identifier VARCHAR(20),  -- Format: "2024-W42"
    category VARCHAR(100),
    goal_hours FLOAT,
    completed_hours FLOAT DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, week_identifier, category)
);
```

### Qdrant Collections

#### 1. **conversations** Collection
```
Vector Dimension: 384 (sentence-transformers/all-MiniLM-L6-v2)
Distance Metric: Cosine

Payload Schema:
{
  user_id: string (UUID),
  role: string ("user" | "assistant"),
  content: string,
  timestamp: string (ISO datetime),
  conversation_id: string,
  intent_data: string (JSON stringified)
}
```

#### 2. **scheduled_tasks** Collection
```
Vector Dimension: 384
Distance Metric: Cosine

Payload Schema:
{
  user_id: string (UUID),
  event_id: string (UUID),
  title: string,
  description: string,
  category: string,
  priority: integer,
  start_time: string (ISO datetime),
  duration_minutes: integer,
  created_at: string (ISO datetime)
}
```

---

## API ENDPOINTS

### Base URL
```
http://localhost:8000
```

### 1. USER MANAGEMENT

#### Create User
```http
POST /users/

Request Body:
{
  "email": "user@example.com",
  "full_name": "John Doe"
}

Response: 201 Created
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "user@example.com",
  "full_name": "John Doe",
  "created_at": "2024-10-16T10:00:00"
}
```

#### Get User
```http
GET /users/{user_id}

Response: 200 OK
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "created_at": "2024-10-16T10:00:00"
}
```

### 2. USER PREFERENCES

#### Get Preferences
```http
GET /preferences/{user_id}

Response: 200 OK
{
  "id": 1,
  "user_id": "uuid",
  "work_start_hour": 9,
  "work_start_minute": 0,
  "work_end_hour": 18,
  "work_end_minute": 0,
  "work_days": [0, 1, 2, 3, 4],
  "prefer_morning": true,
  "lunch_break_hour": 12,
  "lunch_break_minute": 0,
  "lunch_break_duration": 60,
  "min_break_between_tasks": 5,
  "max_tasks_per_day": 10,
  "allow_auto_reschedule": true,
  "weekly_goals": {
    "learning": 5,
    "exercise": 3,
    "coding": 15
  },
  "created_at": "2024-10-16T10:00:00",
  "updated_at": "2024-10-16T10:00:00"
}
```

#### Update Preferences
```http
PUT /preferences/{user_id}

Request Body: (all fields optional)
{
  "work_start_hour": 9,
  "work_start_minute": 0,
  "work_end_hour": 18,
  "work_end_minute": 0,
  "work_days": [0, 1, 2, 3, 4],
  "prefer_morning": true,
  "lunch_break_hour": 12,
  "lunch_break_minute": 0,
  "lunch_break_duration": 60,
  "min_break_between_tasks": 5,
  "max_tasks_per_day": 10,
  "allow_auto_reschedule": true
}

Response: 200 OK
{
  /* updated preference object */
}
```

#### Set/Update Weekly Goals
```http
PUT /preferences/{user_id}/weekly-goals

Request Body:
{
  "weekly_goals": {
    "learning": 5,
    "exercise": 3,
    "meetings": 10,
    "coding": 15,
    "personal": 5,
    "planning": 3
  }
}

Response: 200 OK
{
  "user_id": "uuid",
  "weekly_goals": { /* goals */ },
  "updated_at": "2024-10-16T15:30:00"
}
```

#### Get Weekly Goal Progress
```http
GET /preferences/{user_id}/weekly-goals

Response: 200 OK
{
  "week_id": "2024-W42",
  "goals": {
    "learning": {
      "target_hours": 5,
      "completed_hours": 3.5,
      "remaining_hours": 1.5,
      "percentage": 70
    },
    "exercise": {
      "target_hours": 3,
      "completed_hours": 3,
      "remaining_hours": 0,
      "percentage": 100
    }
  },
  "total_scheduled_hours": 26.5,
  "last_synced": "2024-10-16T15:30:00"
}
```

### 3. CHAT INTERFACE (MAIN INTERACTION)

#### Chat with Assistant
```http
POST /chat/

Request Body:
{
  "user_id": "uuid",
  "prompt": "I want to learn React for 2 hours today",
  "temperature": 0.2,  // Optional: 0.0-2.0, default 0.2
  "conversation_id": null  // null for new, or ID for follow-up
}

Response Types - See "CHAT MESSAGE TYPES" section below
```

### 4. CALENDAR EVENTS

#### Get All Events
```http
GET /calendar/events/{user_id}?start_date=2024-10-14&end_date=2024-10-20

Query Parameters (optional):
- start_date: ISO date
- end_date: ISO date
- status: scheduled | completed | cancelled

Response: 200 OK
{
  "events": [
    {
      "id": "uuid",
      "user_id": "uuid",
      "task_title": "Learn React",
      "description": "Frontend framework",
      "start_time": "2024-10-16T14:00:00",
      "end_time": "2024-10-16T16:00:00",
      "priority_number": 5,
      "priority_tag": "medium",
      "category": "learning",
      "status": "scheduled",
      "created_at": "2024-10-16T10:00:00"
    }
  ],
  "total": 1
}
```

#### Get Single Event
```http
GET /calendar/events/{user_id}/{event_id}

Response: 200 OK
{
  "id": "uuid",
  "task_title": "Learn React",
  /* ... event details ... */
}
```

#### Create Event Manually
```http
POST /calendar/events/{user_id}

Request Body:
{
  "task_title": "Team meeting",
  "description": "Weekly sync",
  "start_time": "2024-10-16T14:00:00",
  "end_time": "2024-10-16T15:00:00",
  "priority_number": 5,
  "category": "meetings"
}

Response: 201 Created
{
  "id": "uuid",
  /* ... event details ... */
}
```

#### Update Event
```http
PUT /calendar/events/{user_id}/{event_id}

Request Body: (all optional)
{
  "task_title": "Updated title",
  "description": "Updated description",
  "start_time": "2024-10-16T15:00:00",
  "end_time": "2024-10-16T16:00:00",
  "priority_number": 8
}

Response: 200 OK
{
  /* updated event */
}
```

#### Delete Event
```http
DELETE /calendar/events/{user_id}/{event_id}

Response: 200 OK
{
  "success": true,
  "message": "Event deleted successfully"
}
```

---

## CHAT MESSAGE TYPES

### Request Schema
```typescript
{
  user_id: string (UUID, required),
  prompt: string (required),
  temperature: number (0.0-2.0, optional, default 0.2),
  conversation_id: string | null (optional, for multi-turn)
}
```

### Response Types

#### Type 1: CREATE EVENT (Success)
```json
{
  "success": true,
  "message": "✅ Scheduled 'Learn React' from Wed Oct 16, 2:00 PM to 4:00 PM",
  "action": "create_event",
  "conversation_id": "user_123_1697469234.123",
  "requires_response": false,
  "event": {
    "id": "event-uuid",
    "user_id": "user-uuid",
    "task_title": "Learn React",
    "description": "Frontend framework learning",
    "start_time": "2024-10-16T14:00:00",
    "end_time": "2024-10-16T16:00:00",
    "priority_number": 5,
    "priority_tag": "medium",
    "category": "learning",
    "status": "scheduled"
  },
  "rescheduled_events": [],
  "goal_updated": true,
  "category": "learning"
}
```

#### Type 2: CREATE EVENT WITH RESCHEDULING
```json
{
  "success": true,
  "message": "✅ Scheduled 'Urgent client call' from Mon Oct 14, 2:00 PM to 3:00 PM\n\nℹ️ Moved 1 lower-priority task:\n  • Watch YouTube: Mon 2:00 PM → Wed 10:00 AM",
  "action": "create_event",
  "conversation_id": "user_123_1697469234.123",
  "requires_response": false,
  "event": {
    "id": "event-uuid",
    "task_title": "Urgent client call",
    "start_time": "2024-10-14T14:00:00",
    "end_time": "2024-10-14T15:00:00",
    "priority_number": 10,
    "priority_tag": "urgent"
  },
  "rescheduled_events": [
    {
      "id": "old-event-uuid",
      "task_title": "Watch YouTube",
      "old_start": "2024-10-14T14:00:00",
      "new_start": "2024-10-16T10:00:00",
      "priority_number": 1
    }
  ]
}
```

#### Type 3: QUERY SCHEDULE
```json
{
  "success": true,
  "message": "📅 You have 3 event(s):\n\n• Team standup\n  Mon Oct 14, 09:00 AM - 10:00 AM | Priority: medium\n\n• Code review\n  Mon Oct 14, 11:00 AM - 12:00 PM | Priority: high\n\n• Client call\n  Mon Oct 14, 02:00 PM - 03:00 PM | Priority: urgent",
  "action": "query_schedule",
  "conversation_id": "user_123_1697469234.123",
  "requires_response": false,
  "events": [
    {
      "id": "uuid",
      "task_title": "Team standup",
      "start_time": "2024-10-14T09:00:00",
      "end_time": "2024-10-14T10:00:00",
      "priority_tag": "medium"
    }
    /* ... more events ... */
  ],
  "period": {
    "start": "2024-10-14T00:00:00",
    "end": "2024-10-14T23:59:59"
  }
}
```

#### Type 4: CHECK GOALS
```json
{
  "success": true,
  "message": "📊 Weekly Goals Progress:\n\n🔄 learning: 3h / 5h (60%)\n   Remaining: 2h\n\n✅ exercise: 3h / 3h (100%)\n\n🔄 coding: 8h / 15h (53%)\n   Remaining: 7h\n\n💡 To meet your goals, schedule:\n   • 2h of learning\n   • 7h of coding",
  "action": "check_goals",
  "conversation_id": "user_123_1697469234.123",
  "requires_response": false,
  "goals": {
    "learning": {
      "target": 5,
      "completed": 3,
      "remaining": 2,
      "percentage": 60
    },
    "exercise": {
      "target": 3,
      "completed": 3,
      "remaining": 0,
      "percentage": 100
    }
  }
}
```

#### Type 5: ASK CLARIFICATION (Multi-Turn)
```json
{
  "success": true,
  "message": "What would you like to schedule?",
  "action": "ask_clarification",
  "conversation_id": "user_123_1697469234.123",
  "requires_response": true,  // ⭐ IMPORTANT: Frontend should await user response
  "missing_info": ["title", "duration"]
}
```

**Frontend Action for Type 5:**
- Display the question
- Keep chat input active
- Store `conversation_id`
- When user responds, include `conversation_id` in next request

#### Type 6: ERROR
```json
{
  "success": false,
  "message": "Could not understand the request. Please try rephrasing.",
  "action": null,
  "conversation_id": "user_123_1697469234.123",
  "error": "JSON parse error: Expecting value"
}
```

---

## FRONTEND INTEGRATION GUIDE

### Initial Setup Page

#### Required Input Fields:
```html
<!-- User Registration -->
<form id="user-registration">
  <input name="email" type="email" required />
  <input name="full_name" type="text" required />
  <button type="submit">Create Account</button>
</form>

<!-- User Preferences (show after registration) -->
<form id="user-preferences">
  <h3>Work Schedule</h3>
  <select name="work_start_hour"><!-- 0-23 --></select>
  <select name="work_start_minute"><!-- 0,15,30,45 --></select>
  <select name="work_end_hour"><!-- 0-23 --></select>
  <select name="work_end_minute"><!-- 0,15,30,45 --></select>
  
  <h3>Work Days</h3>
  <input type="checkbox" name="work_days" value="0" checked /> Monday
  <input type="checkbox" name="work_days" value="1" checked /> Tuesday
  <input type="checkbox" name="work_days" value="2" checked /> Wednesday
  <input type="checkbox" name="work_days" value="3" checked /> Thursday
  <input type="checkbox" name="work_days" value="4" checked /> Friday
  <input type="checkbox" name="work_days" value="5" /> Saturday
  <input type="checkbox" name="work_days" value="6" /> Sunday
  
  <h3>Preferences</h3>
  <input type="checkbox" name="prefer_morning" checked /> Prefer morning slots
  <input type="number" name="max_tasks_per_day" value="10" min="1" max="20" />
  <input type="checkbox" name="allow_auto_reschedule" checked /> Allow auto-rescheduling
  
  <h3>Lunch Break</h3>
  <select name="lunch_break_hour"><!-- 0-23 --></select>
  <input type="number" name="lunch_break_duration" value="60" min="0" max="180" /> minutes
  
  <button type="submit">Save Preferences</button>
</form>

<!-- Weekly Goals -->
<form id="weekly-goals">
  <h3>Weekly Goals (hours per week)</h3>
  <label>Learning: <input type="number" name="learning" min="0" step="0.5" /></label>
  <label>Exercise: <input type="number" name="exercise" min="0" step="0.5" /></label>
  <label>Meetings: <input type="number" name="meetings" min="0" step="0.5" /></label>
  <label>Coding: <input type="number" name="coding" min="0" step="0.5" /></label>
  <label>Personal: <input type="number" name="personal" min="0" step="0.5" /></label>
  <label>Planning: <input type="number" name="planning" min="0" step="0.5" /></label>
  
  <button type="submit">Set Goals</button>
</form>
```

### Main Chat Interface

#### Required Components:
```html
<div id="app">
  <!-- Chat Messages Container -->
  <div id="chat-messages">
    <!-- Messages rendered here -->
  </div>
  
  <!-- Chat Input -->
  <div id="chat-input-container">
    <input 
      id="chat-input" 
      type="text" 
      placeholder="Type your message..."
      autocomplete="off"
    />
    <button id="send-btn">Send</button>
  </div>
  
  <!-- Calendar View (optional) -->
  <div id="calendar-view">
    <!-- Display events from GET /calendar/events -->
  </div>
  
  <!-- Goals Dashboard (optional) -->
  <div id="goals-dashboard">
    <!-- Display from GET /preferences/{user_id}/weekly-goals -->
  </div>
</div>
```

### JavaScript Implementation Example

```javascript
// Store user session
let currentUser = {
  id: null,
  conversationId: null,
  waitingForResponse: false
};

// 1. User Registration
async function registerUser(email, fullName) {
  const response = await fetch('http://localhost:8000/users/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, full_name: fullName })
  });
  
  const user = await response.json();
  currentUser.id = user.id;
  localStorage.setItem('userId', user.id);
  
  return user;
}

// 2. Set Preferences
async function setPreferences(preferences) {
  const response = await fetch(`http://localhost:8000/preferences/${currentUser.id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(preferences)
  });
  
  return await response.json();
}

// 3. Send Chat Message
async function sendMessage(message) {
  const payload = {
    user_id: currentUser.id,
    prompt: message,
    temperature: 0.2
  };
  
  // Include conversation_id if in multi-turn conversation
  if (currentUser.conversationId) {
    payload.conversation_id = currentUser.conversationId;
  }
  
  const response = await fetch('http://localhost:8000/chat/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  
  const result = await response.json();
  
  // Handle response
  handleChatResponse(result);
  
  return result;
}

// 4. Handle Chat Response
function handleChatResponse(response) {
  // Display message
  displayMessage('assistant', response.message);
  
  // Check if waiting for user response
  if (response.requires_response) {
    currentUser.conversationId = response.conversation_id;
    currentUser.waitingForResponse = true;
    // Keep input active, show typing indicator
  } else {
    // Conversation complete, clear conversation_id
    currentUser.conversationId = null;
    currentUser.waitingForResponse = false;
  }
  
  // Handle different action types
  switch (response.action) {
    case 'create_event':
      // Update calendar view
      if (response.event) {
        addEventToCalendar(response.event);
      }
      // Show rescheduled events if any
      if (response.rescheduled_events?.length > 0) {
        showRescheduledNotification(response.rescheduled_events);
      }
      break;
      
    case 'query_schedule':
      // Display events in calendar
      if (response.events) {
        displayEventsInCalendar(response.events);
      }
      break;
      
    case 'check_goals':
      // Update goals dashboard
      if (response.goals) {
        updateGoalsDashboard(response.goals);
      }
      break;
      
    case 'ask_clarification':
      // Show that assistant is waiting for answer
      showWaitingIndicator();
      break;
  }
}

// 5. Display Message
function displayMessage(role, content) {
  const messagesContainer = document.getElementById('chat-messages');
  const messageDiv = document.createElement('div');
  messageDiv.className = `message message-${role}`;
  messageDiv.textContent = content;
  messagesContainer.appendChild(messageDiv);
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// 6. Load Calendar Events
async function loadCalendarEvents(startDate, endDate) {
  const params = new URLSearchParams({
    start_date: startDate,
    end_date: endDate
  });
  
  const response = await fetch(
    `http://localhost:8000/calendar/events/${currentUser.id}?${params}`
  );
  
  const data = await response.json();
  displayEventsInCalendar(data.events);
}

// 7. Load Goal Progress
async function loadGoalProgress() {
  const response = await fetch(
    `http://localhost:8000/preferences/${currentUser.id}/weekly-goals`
  );
  
  const data = await response.json();
  updateGoalsDashboard(data.goals);
}

// Event Listeners
document.getElementById('send-btn').addEventListener('click', async () => {
  const input = document.getElementById('chat-input');
  const message = input.value.trim();
  
  if (message) {
    displayMessage('user', message);
    input.value = '';
    
    await sendMessage(message);
  }
});
```

### UI State Management

```javascript
// Application States
const APP_STATES = {
  ONBOARDING: 'onboarding',
  SETTING_PREFERENCES: 'setting_preferences',
  READY: 'ready',
  CHATTING: 'chatting',
  WAITING_RESPONSE: 'waiting_response'
};

let appState = APP_STATES.ONBOARDING;

function updateUIState(newState) {
  appState = newState;
  
  switch (newState) {
    case APP_STATES.ONBOARDING:
      // Show registration form
      break;
      
    case APP_STATES.SETTING_PREFERENCES:
      // Show preferences form
      break;
      
    case APP_STATES.READY:
      // Show main chat interface
      break;
      
    case APP_STATES.WAITING_RESPONSE:
      // Show typing indicator
      // Disable send button or show "waiting for your answer"
      break;
  }
}
```

---

## DATA FLOW DIAGRAMS

### Complete Request-Response Flow

```
┌─────────────┐
│   FRONTEND  │
└──────┬──────┘
       │ POST /chat/
       │ {user_id, prompt, conversation_id}
       ↓
┌──────────────────────────────────────────┐
│  CHAT ROUTER (chat/router.py)           │
├──────────────────────────────────────────┤
│  - Validate request                      │
│  - Create EnhancedCalendarOrchestrator   │
│  - Call process_user_request()           │
└──────┬───────────────────────────────────┘
       ↓
┌────────────────────────────────────────────────────────┐
│  ENHANCED ORCHESTRATOR (agents/enhanced_orchestrator)  │
├────────────────────────────────────────────────────────┤
│  STEP 1: Build Context                                 │
│    ├─→ ConversationMemory.get_conversation_context()  │
│    │   ├─→ search_similar_conversations()             │
│    │   ├─→ search_similar_tasks()                     │
│    │   ├─→ detect_recurring_pattern()                 │
│    │   └─→ get upcoming events                        │
│    │                                                    │
│  STEP 2: Call LLM                                      │
│    ├─→ ask_llm(prompt, context)                       │
│    │   └─→ OpenRouter API (Llama 3.2)                 │
│    │       Returns: JSON intent                        │
│    │                                                    │
│  STEP 3: Parse Intent & Execute                        │
│    ├─→ _handle_create_event()                         │
│    │   ├─→ SmartScheduler.schedule_with_context()     │
│    │   │   ├─→ Find best slot                         │
│    │   │   ├─→ Check conflicts                        │
│    │   │   └─→ Auto-reschedule if needed              │
│    │   └─→ Update weekly goals                        │
│    │                                                    │
│    ├─→ _handle_query_schedule()                       │
│    │   └─→ Get events from PostgreSQL                 │
│    │                                                    │
│    ├─→ _handle_check_goals()                          │
│    │   └─→ Sync and return goal progress              │
│    │                                                    │
│    └─→ _handle_update/delete_event()                  │
│                                                        │
│  STEP 4: Store in Qdrant                              │
│    ├─→ store_message(user, content)                   │
│    ├─→ store_message(assistant, response)             │
│    └─→ store_scheduled_task() [if created]            │
└──────┬─────────────────────────────────────────────────┘
       │
       ↓
┌──────────────┐
│  PostgreSQL  │ ← Events, Users, Preferences stored
└──────────────┘

┌──────────────┐
│   Qdrant     │ ← Conversations & Tasks with embeddings
└──────────────┘
       │
       ↓
┌──────────────────────────────────────┐
│  RESPONSE                            │
├──────────────────────────────────────┤
│  {                                   │
│    success: true,                    │
│    message: "...",                   │
│    action: "create_event",           │
│    conversation_id: "...",           │
│    requires_response: false,         │
│    event: {...}                      │
│  }                                   │
└──────┬───────────────────────────────┘
       │
       ↓
┌─────────────┐
│   FRONTEND  │ ← Display & Update UI
└─────────────┘
```

### Semantic Search Flow

```
User Message: "Gym workout"
       ↓
┌────────────────────────────────────────┐
│  ConversationMemory                    │
├────────────────────────────────────────┤
│  1. Generate Embedding                 │
│     ├─→ HuggingFace API                │
│     └─→ Returns 384-dim vector         │
│                                        │
│  2. Search Qdrant                      │
│     ├─→ conversations collection       │
│     │   (Find similar past chats)      │
│     │   Result: "gym for 1 hour"       │
│     │                                  │
│     └─→ scheduled_tasks collection     │
│         (Find similar tasks)           │
│         Result: 10 gym tasks, avg 1h   │
│                                        │
│  3. Detect Pattern                     │
│     ├─→ Filter >80% similarity         │
│     ├─→ Count: 10 occurrences          │
│     ├─→ Avg duration: 60min            │
│     └─→ Common priority: 5 (medium)    │
│                                        │
│  4. Build Context String               │
│     └─→ "Similar tasks: 'Gym workout'  │
│         done 10 times, usually 1h"     │
└────────┬───────────────────────────────┘
         │
         ↓
    Send to LLM with context
         ↓
    LLM uses pattern to suggest 1h duration
```

---

## COMPONENT ARCHITECTURE

### Backend Components

```
main.py
  ├─→ FastAPI app initialization
  ├─→ CORS middleware
  ├─→ Routers
  │   ├─→ /users (users/router.py)
  │   ├─→ /preferences (users/preference_router.py)
  │   ├─→ /chat (chat/router.py)
  │   └─→ /calendar (events/router.py)
  └─→ Database connection

chat/
  ├─→ router.py (Main chat endpoint)
  ├─→ schemas.py (Request/Response models)
  └─→ conversation_memory.py
      ├─→ ConversationMemory class
      ├─→ Qdrant integration
      ├─→ Embedding generation
      └─→ Semantic search functions

agents/
  ├─→ llm.py (LLM API calls)
  │   ├─→ ask_llm()
  │   └─→ ask_llm_for_clarification()
  ├─→ enhanced_orchestrator.py
  │   └─→ EnhancedCalendarOrchestrator
  │       ├─→ Context building
  │       ├─→ Intent execution
  │       └─→ Response generation
  └─→ smart_scheduler.py
      └─→ SmartScheduler
          ├─→ schedule_with_context()
          ├─→ find_best_slot_in_week()
          ├─→ reschedule_lower_priority_events()
          └─→ get_next_weekend()

users/
  ├─→ models.py (User, UserPreference)
  ├─→ preference_controllers.py
  │   ├─→ get_or_create_user_preference()
  │   ├─→ get_weekly_goal_status()
  │   └─→ sync_weekly_goals_with_events()
  └─→ preference_router.py

events/
  ├─→ models.py (CalendarEvent, WeeklyGoalTracker)
  ├─→ controllers.py
  │   ├─→ create_calendar_event()
  │   ├─→ get_events_by_date_range()
  │   └─→ update/delete functions
  └─→ router.py

db/
  ├─→ database.py (PostgreSQL connection)
  └─→ qdrant_client.py (Qdrant connection)
```

### Key Classes

#### 1. EnhancedCalendarOrchestrator
```python
class EnhancedCalendarOrchestrator:
    def __init__(self, db: Session)
    
    def process_user_request(
        user_id: UUID,
        user_message: str,
        temperature: float = 0.2,
        conversation_id: Optional[str] = None
    ) -> Dict
    
    def _handle_create_event(user_id, intent_data) -> Dict
    def _handle_query_schedule(user_id, intent_data) -> Dict
    def _handle_check_goals(user_id) -> Dict
    def _handle_update_event(user_id, intent_data) -> Dict
    def _handle_delete_event(user_id, intent_data) -> Dict
```

#### 2. ConversationMemory
```python
class ConversationMemory:
    def get_embedding(text: str) -> List[float]
    
    def store_message(
        user_id: UUID,
        role: str,
        content: str,
        intent_data: Optional[Dict] = None,
        conversation_id: Optional[str] = None
    ) -> str
    
    def store_scheduled_task(
        user_id: UUID,
        event_id: UUID,
        title: str,
        description: str,
        category: str,
        priority: int,
        start_time: datetime,
        duration_minutes: int
    )
    
    def search_similar_conversations(
        user_id: UUID,
        query: str,
        limit: int = 5
    ) -> List[Dict]
    
    def search_similar_tasks(
        user_id: UUID,
        query: str,
        limit: int = 5
    ) -> List[Dict]
    
    def detect_recurring_pattern(
        user_id: UUID,
        task_title: str,
        category: str
    ) -> Optional[Dict]
    
    def get_conversation_context(
        user_id: UUID,
        current_query: str,
        db: Session
    ) -> str
```

#### 3. SmartScheduler
```python
class SmartScheduler:
    def __init__(self, db: Session, user_id: UUID)
    
    def schedule_with_context(
        task_title: str,
        duration_minutes: int,
        priority_number: int,
        priority_tag: str,
        when: Optional[str] = None,
        description: Optional[str] = None,
        category: str = "general"
    ) -> Dict
    
    def find_best_slot_in_week(
        duration_minutes: int,
        priority_number: int,
        when: Optional[str] = None
    ) -> Optional[Tuple[datetime, datetime]]
    
    def reschedule_lower_priority_events(
        required_start: datetime,
        required_end: datetime,
        new_priority: int
    ) -> List[Dict]
```

---

## SETUP & CONFIGURATION

### Environment Variables (.env)
```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/scheddy_db

# OpenRouter (LLM)
OPENROUTER_API_KEY=sk-or-v1-xxxxx
OPENROUTER_MODEL=meta-llama/llama-3.2-3b-instruct:free

# HuggingFace (Embeddings)
HUGGINGFACE_API_KEY=hf_xxxxx

# Qdrant
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=  # Empty for local

# App Settings
APP_ENV=development
DEBUG=true
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8000
```

### Installation Steps

1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

2. **Start PostgreSQL**
```bash
# Using Docker
docker run -p 5432:5432 \
  -e POSTGRES_DB=scheddy_db \
  -e POSTGRES_USER=scheddy_user \
  -e POSTGRES_PASSWORD=password \
  postgres:14
```

3. **Start Qdrant**
```bash
# Using Docker
docker run -p 6333:6333 -p 6334:6334 \
  -v $(pwd)/qdrant_storage:/qdrant/storage \
  qdrant/qdrant
```

4. **Configure .env**
- Add DATABASE_URL
- Add OPENROUTER_API_KEY (get from openrouter.ai)
- Add HUGGINGFACE_API_KEY (get from huggingface.co/settings/tokens)

5. **Run Application**
```bash
uvicorn main:app --reload
```

6. **Access API**
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Qdrant Dashboard: http://localhost:6333/dashboard

### Priority Levels
```
10 = Urgent    (urgent, critical, emergency, must, asap)
8  = High      (important, need to, should, deadline)
5  = Medium    (default, regular tasks)
3  = Low       (when possible, maybe, if time)
1  = Optional  (optional, nice to have, would like)
```

### Task Categories (for Weekly Goals)
```
learning  - Study, courses, tutorials, reading
exercise  - Gym, workout, fitness, sports
meetings  - Meetings, calls, standups, discussions
coding    - Programming, development, debugging
personal  - Family, hobbies, personal time
planning  - Planning, organization, strategy
general   - Everything else
```

### Duration Formats
```
"1h"      = 1 hour
"30m"     = 30 minutes
"2h30m"   = 2 hours 30 minutes
"45m"     = 45 minutes
"1.5h"    = 1 hour 30 minutes
```

---

## CONFLICT DETECTION & RESCHEDULING RULES

### How Conflict Detection Works

When creating a new event, the system follows this process:

1. **Retrieve Day's Schedule**
   - Get all existing events for the target date
   - Get user preferences (work hours, breaks, etc.)

2. **Check Available Time Slots**
   - Respects work hours (e.g., 9 AM - 6 PM)
   - Excludes lunch breaks (e.g., 12-1 PM)
   - Respects minimum break time between tasks (e.g., 5 min)
   - Filters out conflicting events

3. **Conflict Resolution Strategy**
   
   **Case 1: Free Slot Available**
   ```
   ✅ Schedule immediately in best available slot
   ```
   
   **Case 2: No Free Slots + Auto-Reschedule Enabled**
   ```
   ✅ Move lower-priority tasks to future dates
   ✅ Schedule new task in freed slot
   ✅ Return list of rescheduled events
   ⚠️  NEVER reschedules Priority 9-10 (Urgent/Critical) tasks
   ```
   
   **Case 3: No Free Slots + Auto-Reschedule Disabled**
   ```
   ❌ Return error: "No available slots"
   💡 Suggest: "Try tomorrow or enable auto-reschedule"
   ```
   
   **Case 4: Must Be Today (Urgent)**
   ```
   ✅ Force reschedule lower-priority tasks
   ✅ Even if auto-reschedule is off
   ⚠️  NEVER reschedules Priority 9-10 tasks
   ```

### Protected Priority Rules

**CRITICAL PROTECTION:** Priority 9 and 10 tasks are **NEVER** rescheduled automatically.

| New Task Priority | Can Reschedule Priority | Protected Priorities |
|------------------|------------------------|---------------------|
| 10 (Critical)    | 0-8 only               | **9, 10** ❌ |
| 9 (Urgent)       | 0-8 only               | **9, 10** ❌ |
| 8 (High)         | 0-7 only               | **9, 10** ❌ |
| 7 (High)         | 0-6 only               | **9, 10** ❌ |
| 6 (Medium-High)  | 0-5 only               | **9, 10** ❌ |
| 5 (Medium)       | 0-4 only               | **9, 10** ❌ |
| 0-4 (Low)        | No auto-reschedule     | **9, 10** ❌ |

### Example Scenarios

#### Scenario 1: ❌ Cannot Reschedule Protected Task
```
Existing: "Board Meeting" (Priority 10) at 2 PM - 3 PM
Request:  "Code Review" (Priority 8) for 2 PM today

System Response:
  ❌ "No available slots. Board Meeting (Priority 10) cannot be moved."
  💡 Suggestion: "Try scheduling at 3 PM or later, or choose another day."
```

#### Scenario 2: ✅ Allowed Rescheduling  
```
Existing: "Email catchup" (Priority 3) at 2 PM - 3 PM
Request:  "Bug Fix" (Priority 9) for 2 PM today

System Response:
  ✅ "Scheduled 'Bug Fix' from 2:00 PM to 3:00 PM"
  ℹ️  "Moved 'Email catchup' to tomorrow at 2:00 PM"
```

#### Scenario 3: ❌ Low Priority Cannot Trigger Reschedule
```
Existing: "Team Meeting" (Priority 8) at 2 PM - 3 PM
Request:  "Watch YouTube" (Priority 1) for 2 PM today

System Response:
  ❌ "No available slots for low-priority task."
  💡 "Try scheduling at a different time or day."
```

#### Scenario 4: ⚠️ Multiple Protected Tasks Block Scheduling
```
Existing: 
  - "CEO Call" (Priority 10) at 10 AM - 11 AM
  - "Client Demo" (Priority 9) at 2 PM - 4 PM
  - "Board Meeting" (Priority 10) at 4 PM - 5 PM
Request: "Team Training" (Priority 7) must be scheduled today

System Response:
  ❌ "Cannot find suitable slot. Day is fully booked with urgent/critical tasks."
  ℹ️  "Protected tasks: CEO Call, Client Demo, Board Meeting"
  💡 Suggestion: "Schedule for tomorrow or next available day?"
```

### Implementation Details

**In `agents/scheduler.py` (CalendarScheduler):**
```python
# Protected priorities constant
PROTECTED_PRIORITIES = [9, 10]  # Urgent and Critical tasks

def reschedule_lower_priority_events(...):
    for event in conflicting_events:
        # Only reschedule if new event has higher priority
        if event.priority_number >= new_event_priority:
            continue
        
        # NEVER reschedule Priority 9-10 (Urgent/Critical) tasks
        if event.priority_number in self.PROTECTED_PRIORITIES:
            continue
        
        # ... proceed with rescheduling ...
```

**In `agents/smart_scheduler.py` (SmartScheduler):**
```python
# Protected priorities constant
PROTECTED_PRIORITIES = [9, 10]  # Urgent and Critical tasks

# Same protection logic applied to week-aware scheduling
```

---

## NATURAL LANGUAGE EXAMPLES

### Scheduling
```
✅ "I want to learn React for 2 hours today"
✅ "Schedule gym workout for 1 hour"
✅ "I need to code for 3 hours this week"
✅ "Plan a meeting tomorrow at 2 PM for 30 minutes"
✅ "Schedule Python learning this weekend"
```

### Queries
```
✅ "What's my schedule today?"
✅ "Show me what I have this weekend"
✅ "What do I have scheduled for tomorrow?"
✅ "Am I free at 3 PM today?"
```

### Goals
```
✅ "Show my weekly goals progress"
✅ "How am I doing with my goals?"
✅ "What goals haven't I completed?"
```

### Multi-Turn
```
User: "Schedule something"
Assistant: "What would you like to schedule?"
User: "A team meeting"
Assistant: "How long will the meeting be?"
User: "30 minutes"
Assistant: "Scheduled 'Team meeting' for 30 minutes..."
```

---

## ERROR HANDLING

### Common Error Codes
```
400 Bad Request       - Invalid input, missing fields
404 Not Found         - User/event doesn't exist
409 Conflict          - Time slot occupied, email exists
422 Validation Error  - Type mismatch, invalid format
500 Server Error      - Database error, unexpected failure
```

### Frontend Error Handling
```javascript
try {
  const response = await fetch('/chat/', {
    method: 'POST',
    body: JSON.stringify(payload)
  });
  
  const data = await response.json();
  
  if (!response.ok) {
    // Handle HTTP errors
    throw new Error(data.detail || 'Request failed');
  }
  
  if (!data.success) {
    // Handle application-level errors
    displayError(data.message);
  }
  
} catch (error) {
  console.error('Chat error:', error);
  displayError('Failed to process request. Please try again.');
}
```

---

## PERFORMANCE CONSIDERATIONS

### Expected Response Times
```
User Registration:     < 100ms
Set Preferences:       < 200ms
Chat (no context):     < 1000ms
Chat (with context):   < 1500ms
  - Qdrant search:     < 100ms
  - LLM call:          500-1000ms
  - DB operations:     < 200ms
Query Events:          < 100ms
```

### Optimization Tips
- Cache user preferences in frontend
- Debounce chat input (prevent spam)
- Use WebSocket for real-time updates (future)
- Lazy load calendar events (pagination)
- Implement request retries for LLM calls

---

## SECURITY CONSIDERATIONS

### Current Implementation
- No authentication (development only)
- User ID passed in requests
- No rate limiting

### Production Requirements
```
✅ Implement OAuth2 / JWT authentication
✅ Add rate limiting (per user)
✅ Validate all inputs server-side
✅ Use HTTPS only
✅ Sanitize LLM responses
✅ Implement CORS properly
✅ Add API key rotation
✅ Encrypt sensitive data in DB
```

---

## TESTING

### Test Script
```bash
# Located at: test_qdrant_integration.py
python test_qdrant_integration.py
```

### Manual Testing Checklist
```
□ Create user
□ Set preferences
□ Set weekly goals
□ Chat: Schedule simple task
□ Chat: Schedule urgent task (test auto-reschedule)
□ Chat: Schedule weekend task
□ Chat: Query schedule
□ Chat: Check goals
□ Chat: Multi-turn conversation
□ Verify Qdrant collections populated
□ Check pattern detection after multiple similar tasks
```

---

**END OF DOCUMENTATION**

This is the complete architecture and integration guide for Scheddy AI Calendar Assistant.
All API endpoints, data flows, schemas, and frontend integration details are documented above.
