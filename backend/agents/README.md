# Agents Module

This module handles LLM (Large Language Model) interactions for the Scheddy application.

## Overview

The module provides an interface to OpenRouter API for conversational AI capabilities.

## Current Model

**Model**: `meta-llama/llama-3.2-3b-instruct:free`
- Provider: Meta
- Cost: Free tier
- Use case: General scheduling assistance and conversational queries

### Why Llama instead of Mistral?

The Mistral free tier models on OpenRouter were returning empty responses. Llama 3.2 3B provides:
- Reliable responses
- Good quality for scheduling tasks
- Fast inference
- Free tier availability

## Functions

### `ask_llm(prompt, max_tokens=500, temperature=0.7)`

Main function for LLM interactions.

**Parameters:**
- `prompt` (str): The user's question or message
- `max_tokens` (int): Maximum tokens in response (default: 500)
- `temperature` (float): Response creativity 0.0-2.0 (default: 0.7)

**Returns:**
- dict with keys: `role`, `content`

**Example:**
```python
from agents.llm import ask_llm

response = ask_llm("What time should I schedule my morning meeting?")
print(response['content'])
```

### `ask_mistral()`

Backward compatibility alias for `ask_llm()`.

## Configuration

Requires `OPENROUTER_API_KEY` in `.env` file:

```env
OPENROUTER_API_KEY=your_key_here
```

Get your API key from: https://openrouter.ai/keys

## API Headers

The function includes required OpenRouter headers:
- `HTTP-Referer`: For API tracking
- `X-Title`: Application identifier

## Troubleshooting

### Empty Responses

If you get empty responses, check:
1. API key is valid
2. Model name is correct
3. Required headers are included
4. Using a working model (not all free tier models work reliably)

### Model Changes

To switch models, update the `model` field in the payload:
```python
"model": "meta-llama/llama-3.2-3b-instruct:free"
```

See available models at: https://openrouter.ai/models
