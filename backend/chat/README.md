# Chat Module

This module provides an API endpoint for interacting with the AI assistant powered by Mistral AI through OpenRouter.

## Endpoints

### POST `/chat/`

Chat with the AI scheduling assistant.

**Request Body:**
```json
{
  "prompt": "Schedule a meeting for tomorrow at 3pm",
  "max_tokens": 200,
  "temperature": 0.2
}
```

**Parameters:**
- `prompt` (required): Your message to the assistant
- `max_tokens` (optional): Maximum tokens in response (default: 200)
- `temperature` (optional): Response creativity level 0.0-2.0 (default: 0.2)

**Response:**
```json
{
  "role": "assistant",
  "content": "I'll help you schedule a meeting for tomorrow at 3pm..."
}
```

## Usage Example

```bash
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "What are the benefits of using a personal assistant app?",
    "max_tokens": 200,
    "temperature": 0.2
  }'
```

## Environment Setup

Make sure you have the `OPENROUTER_API_KEY` set in your `.env` file:

```env
OPENROUTER_API_KEY=your_api_key_here
```

## Testing

You can test the endpoint by running the FastAPI server:

```bash
uvicorn main:app --reload
```

Then visit `http://localhost:8000/docs` to access the interactive API documentation.
