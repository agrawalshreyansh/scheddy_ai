# Calendar Events Module

This module handles calendar events/tasks and dates for the Scheddy application.

## Features

- Create, read, update, and delete calendar events
- Priority system with numeric (1-10) and tag-based (urgent, high, medium, low, optional) prioritization
- Multi-date support for recurring or multi-day events
- Events are linked to users via UUID
- Query events by date range, priority, and user
- Full CRUD operations for calendar dates

## Models

### CalendarEvent
- `id`: UUID - Unique identifier
- `task_title`: String(200) - Title of the task/event
- `description`: Text - Detailed description (optional)
- `start_time`: DateTime(TZ) - When the event starts
- `end_time`: DateTime(TZ) - When the event ends
- `priority_number`: Integer(1-10) - Numeric priority (default: 5)
- `priority_tag`: Enum - Priority tag: urgent, high, medium, low, optional (default: medium)
- `user_id`: UUID - Foreign key to the user who owns this event
- `created_at`: DateTime(TZ) - Timestamp when the event was created
- `updated_at`: DateTime(TZ) - Timestamp when the event was last updated
- `dates`: Relationship - One-to-many relationship with CalendarDate

### CalendarDate
- `id`: UUID - Unique identifier
- `event_date`: Date - Specific date for the event occurrence
- `event_uuid`: UUID - Foreign key to the calendar event
- `created_at`: DateTime(TZ) - Timestamp when the date was created
- `updated_at`: DateTime(TZ) - Timestamp when the date was last updated
- `calendar_event`: Relationship - Many-to-one relationship with CalendarEvent

### PriorityTag Enum
- `URGENT` - "urgent" - Critical tasks requiring immediate attention
- `HIGH` - "high" - Important tasks with high priority
- `MEDIUM` - "medium" - Normal priority tasks (default)
- `LOW` - "low" - Lower priority tasks that can wait
- `OPTIONAL` - "optional" - Nice to have, lowest priority

---

## API Endpoints

All endpoints are prefixed with `/calendar`

### Calendar Event Endpoints

#### Create Event
```http
POST /calendar/events
```
**Request Body:**
```json
{
  "task_title": "Team Meeting",
  "description": "Weekly standup",
  "start_time": "2025-10-20T09:00:00Z",
  "end_time": "2025-10-20T09:30:00Z",
  "priority_number": 5,
  "priority_tag": "medium",
  "user_id": "123e4567-e89b-12d3-a456-426614174000"
}
```
**Response:** `201 Created` - CalendarEventResponse

---

#### Get Event by ID
```http
GET /calendar/events/{event_id}
```
**Parameters:**
- `event_id` (path, UUID) - Event ID

**Response:** `200 OK` - CalendarEventResponse

---

#### Get All Events
```http
GET /calendar/events
```
**Query Parameters:**
- `skip` (optional, integer, default: 0) - Number of records to skip
- `limit` (optional, integer, default: 100) - Maximum records to return
- `user_id` (optional, UUID) - Filter by user ID

**Response:** `200 OK` - List of CalendarEventResponse

---

#### Get Events by Date Range
```http
GET /calendar/events/range/
```
**Query Parameters:**
- `start_date` (required, datetime) - Start of date range
- `end_date` (required, datetime) - End of date range
- `user_id` (optional, UUID) - Filter by user ID

**Response:** `200 OK` - List of CalendarEventResponse

---

#### Get Events by Priority Tag
```http
GET /calendar/events/priority/{priority_tag}
```
**Parameters:**
- `priority_tag` (path, enum) - One of: urgent, high, medium, low, optional

**Query Parameters:**
- `user_id` (optional, UUID) - Filter by user ID

**Response:** `200 OK` - List of CalendarEventResponse

**Example:**
```bash
GET /calendar/events/priority/urgent
GET /calendar/events/priority/high?user_id=123e4567-e89b-12d3-a456-426614174000
```

---

#### Get Event with Related Dates
```http
GET /calendar/events/{event_id}/with-dates
```
**Parameters:**
- `event_id` (path, UUID) - Event ID

**Response:** `200 OK` - CalendarEventWithDatesResponse (includes all related dates)

---

#### Update Event
```http
PUT /calendar/events/{event_id}
```
**Parameters:**
- `event_id` (path, UUID) - Event ID

**Request Body (all fields optional):**
```json
{
  "task_title": "Updated Title",
  "description": "Updated description",
  "start_time": "2025-10-20T10:00:00Z",
  "end_time": "2025-10-20T11:00:00Z",
  "priority_number": 8,
  "priority_tag": "high"
}
```
**Response:** `200 OK` - CalendarEventResponse

---

#### Delete Event
```http
DELETE /calendar/events/{event_id}
```
**Parameters:**
- `event_id` (path, UUID) - Event ID

**Response:** `204 No Content`

---

### Calendar Date Endpoints

#### Create Date
```http
POST /calendar/dates
```
**Request Body:**
```json
{
  "event_date": "2025-10-20",
  "event_uuid": "550e8400-e29b-41d4-a716-446655440000"
}
```
**Response:** `201 Created` - CalendarDateResponse

---

#### Get Date by ID
```http
GET /calendar/dates/{date_id}
```
**Parameters:**
- `date_id` (path, UUID) - Date ID

**Response:** `200 OK` - CalendarDateResponse

---

#### Get All Dates for an Event
```http
GET /calendar/events/{event_id}/dates
```
**Parameters:**
- `event_id` (path, UUID) - Event ID

**Response:** `200 OK` - List of CalendarDateResponse

---

#### Get Dates by Date Range
```http
GET /calendar/dates/range/
```
**Query Parameters:**
- `start_date` (required, date) - Start of date range (format: YYYY-MM-DD)
- `end_date` (required, date) - End of date range (format: YYYY-MM-DD)
- `event_uuid` (optional, UUID) - Filter by specific event

**Response:** `200 OK` - List of CalendarDateResponse

**Example:**
```bash
GET /calendar/dates/range/?start_date=2025-10-01&end_date=2025-10-31
GET /calendar/dates/range/?start_date=2025-10-01&end_date=2025-10-31&event_uuid=550e8400-e29b-41d4-a716-446655440000
```

---

#### Update Date
```http
PUT /calendar/dates/{date_id}
```
**Parameters:**
- `date_id` (path, UUID) - Date ID

**Request Body:**
```json
{
  "event_date": "2025-10-21"
}
```
**Response:** `200 OK` - CalendarDateResponse

---

#### Delete Date
```http
DELETE /calendar/dates/{date_id}
```
**Parameters:**
- `date_id` (path, UUID) - Date ID

**Response:** `204 No Content`

---

## Response Schemas

### CalendarEventResponse
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "task_title": "Team Meeting",
  "description": "Weekly standup",
  "start_time": "2025-10-20T09:00:00Z",
  "end_time": "2025-10-20T09:30:00Z",
  "priority_number": 5,
  "priority_tag": "medium",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "created_at": "2025-10-16T10:00:00Z",
  "updated_at": "2025-10-16T10:00:00Z"
}
```

### CalendarDateResponse
```json
{
  "id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
  "event_date": "2025-10-20",
  "event_uuid": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2025-10-16T10:30:00Z",
  "updated_at": "2025-10-16T10:30:00Z"
}
```

### CalendarEventWithDatesResponse
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "task_title": "Team Meeting",
  "description": "Weekly standup",
  "start_time": "2025-10-20T09:00:00Z",
  "end_time": "2025-10-20T09:30:00Z",
  "priority_number": 5,
  "priority_tag": "medium",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "created_at": "2025-10-16T10:00:00Z",
  "updated_at": "2025-10-16T10:00:00Z",
  "dates": [
    {
      "id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
      "event_date": "2025-10-20",
      "event_uuid": "550e8400-e29b-41d4-a716-446655440000",
      "created_at": "2025-10-16T10:30:00Z",
      "updated_at": "2025-10-16T10:30:00Z"
    }
  ]
}
```

---

## Usage Examples

### Example 1: Create Recurring Weekly Meeting
```bash
# 1. Create the event
curl -X POST "http://localhost:8000/calendar/events" \
  -H "Content-Type: application/json" \
  -d '{
    "task_title": "Weekly Team Standup",
    "description": "Monday and Wednesday standups",
    "start_time": "2025-10-20T09:00:00Z",
    "end_time": "2025-10-20T09:30:00Z",
    "priority_number": 6,
    "priority_tag": "high",
    "user_id": "123e4567-e89b-12d3-a456-426614174000"
  }'

# 2. Add specific dates
curl -X POST "http://localhost:8000/calendar/dates" \
  -H "Content-Type: application/json" \
  -d '{
    "event_date": "2025-10-20",
    "event_uuid": "550e8400-e29b-41d4-a716-446655440000"
  }'

curl -X POST "http://localhost:8000/calendar/dates" \
  -H "Content-Type: application/json" \
  -d '{
    "event_date": "2025-10-22",
    "event_uuid": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

### Example 2: Get All Urgent Tasks
```bash
curl "http://localhost:8000/calendar/events/priority/urgent"
```

### Example 3: Get Events for This Month
```bash
curl "http://localhost:8000/calendar/events/range/?start_date=2025-10-01T00:00:00Z&end_date=2025-10-31T23:59:59Z"
```

### Example 4: Update Event Priority
```bash
curl -X PUT "http://localhost:8000/calendar/events/{event_id}" \
  -H "Content-Type: application/json" \
  -d '{
    "priority_number": 10,
    "priority_tag": "urgent"
  }'
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "End time must be after start time"
}
```

### 404 Not Found
```json
{
  "detail": "Calendar event not found"
}
```

### 422 Unprocessable Entity
```json
{
  "detail": [
    {
      "loc": ["body", "priority_number"],
      "msg": "ensure this value is less than or equal to 10",
      "type": "value_error.number.not_le"
    }
  ]
}
```

---

## Validation Rules

### CalendarEvent
- `task_title`: 1-200 characters, required
- `description`: Optional text
- `start_time`: Required, must be valid datetime
- `end_time`: Required, must be after start_time
- `priority_number`: Integer 1-10, default: 5
- `priority_tag`: One of [urgent, high, medium, low, optional], default: medium
- `user_id`: Valid UUID, required

### CalendarDate
- `event_date`: Valid date, required
- `event_uuid`: Valid UUID of existing event, required

---

## Database Relationships

```
User (1) ────< (Many) CalendarEvent
                      │
                      └────< (Many) CalendarDate

- One User can have many CalendarEvents
- One CalendarEvent can have many CalendarDates
- Deleting a User cascades to delete their CalendarEvents
- Deleting a CalendarEvent cascades to delete its CalendarDates
```

---

## Testing with Swagger UI

Visit `http://localhost:8000/docs` to access the interactive API documentation where you can:
- View all available endpoints
- Test API calls directly from the browser
- See request/response schemas
- Try different parameter combinations

---

## Future Enhancements

- ✅ ~~Integration with dates table for recurring events~~ (Implemented)
- ✅ ~~Priority system for events~~ (Implemented)
- Event reminders and notifications
- Event sharing between users
- Event categories/tags
- Attachment support
- Calendar view API (monthly, weekly, daily)
- Conflict detection for overlapping events
- Time zone support and conversion
