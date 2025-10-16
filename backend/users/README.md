# Scheddy - User Management API

A FastAPI application with PostgreSQL database and user management functionality.

## Database Schema

### Users Table

The `users` table includes the following fields:

- `id` (Integer, Primary Key): Auto-incrementing user ID
- `username` (String, 50 chars): Unique username, indexed
- `email` (String, 100 chars): Unique email address, indexed
- `full_name` (String, 100 chars): Optional full name
- `hashed_password` (String, 255 chars): Bcrypt hashed password
- `is_active` (Boolean): Whether the user account is active (default: True)
- `is_superuser` (Boolean): Whether the user has admin privileges (default: False)
- `created_at` (DateTime): Timestamp when user was created
- `updated_at` (DateTime): Timestamp when user was last updated

## Setup

1. **Configure Database**
   
   Update the `.env` file with your PostgreSQL credentials:
   ```env
   DATABASE_URL=postgresql://username:password@localhost:5432/scheddy
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application**
   ```bash
   uvicorn main:app --reload
   ```

   The tables will be created automatically on startup.

## API Endpoints

### Test Database Connection
```http
GET /db-test
```

### Create a New User
```http
POST /users/
Content-Type: application/json

{
  "username": "johndoe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "password": "securepassword123"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2025-10-15T10:30:00Z",
  "updated_at": "2025-10-15T10:30:00Z"
}
```

### Get All Users
```http
GET /users/?skip=0&limit=100
```

### Get User by ID
```http
GET /users/{user_id}
```

### Update User
```http
PUT /users/{user_id}
Content-Type: application/json

{
  "full_name": "John Updated Doe",
  "email": "newemail@example.com"
}
```

### Delete User
```http
DELETE /users/{user_id}
```

**Response:** 204 No Content

## Testing with cURL

### Create a user:
```bash
curl -X POST "http://localhost:8000/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "full_name": "Test User",
    "password": "testpassword123"
  }'
```

### Get all users:
```bash
curl "http://localhost:8000/users/"
```

### Get specific user:
```bash
curl "http://localhost:8000/users/1"
```

### Update user:
```bash
curl -X PUT "http://localhost:8000/users/1" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Updated Name"
  }'
```

### Delete user:
```bash
curl -X DELETE "http://localhost:8000/users/1"
```

## Interactive API Documentation

FastAPI provides automatic interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Project Structure

```
scheddy/
├── main.py              # FastAPI application entry point
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (not in git)
├── .env.example        # Environment variables template
├── .gitignore          # Git ignore rules
├── db/
│   └── database.py     # Database connection and session management
└── users/
    ├── __init__.py     # Users module initialization
    ├── models.py       # User SQLAlchemy model
    ├── schemas.py      # User Pydantic schemas for validation
    ├── crud.py         # User database operations (CRUD functions)
    └── router.py       # User API endpoints/routes
```

## Security Notes

- Passwords are hashed using bcrypt before storing
- Never store plain text passwords
- The `.env` file is in `.gitignore` to prevent committing credentials
- Use strong passwords (minimum 8 characters enforced)

## Development

To enable SQL query logging for debugging, update `db/database.py`:
```python
engine = create_engine(
    DATABASE_URL,
    echo=True  # Change to True to see SQL queries
)
```
