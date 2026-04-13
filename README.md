# AI Agent Project

This is an AI Agent project with FastAPI as the access layer and Redis for persistence, used for rate limiting, session quota management, and updates.

## Project Structure

```
ai-agent/
├── common/           # Common utilities and configuration
│   ├── config/       # Application configuration
│   │   └── config.py
│   └── constants/    # Constants
│       └── field/    # Field constants
│           ├── redis.py
│           └── response.py
├── core/             # Core functionality
│   ├── __init__.py
│   └── redis.py      # Redis client, rate limiter, session quota manager
├── resources/        # Lua scripts
│   ├── rate_limit.lua
│   └── session_quota.lua
├── web/              # Web layer
│   ├── __init__.py
│   ├── fastapi_app.py # FastAPI application
│   ├── router/       # API routers
│   │   ├── __init__.py
│   │   ├── chat.py   # Chat related endpoints
│   │   ├── conversation.py # Conversation related endpoints
│   │   └── message.py # Message related endpoints
│   └── dto/          # Data transfer objects
│       ├── __init__.py
│       ├── chat.py
│       ├── conversation.py
│       └── message.py
├── main.py           # Application entry point
├── pyproject.toml    # Project dependencies
└── README.md         # This file
```

## Installation

1. Install dependencies:

```bash
pip install fastapi uvicorn redis pydantic pydantic-settings
```

2. Start Redis server:

```bash
# If using Docker
docker run -d -p 6379:6379 redis

# Or use local Redis installation
```

## Running the Application

```bash
python main.py
```

The application will run on `http://localhost:8000`.

## API Endpoints

### Chat
- `POST /api/chat/` - Send a chat message (SSE protocol)
- `GET /api/chat/history/{session_id}` - Get chat history

### Conversation
- `POST /api/conversation/` - Create a new conversation
- `GET /api/conversation/` - Get all conversations
- `GET /api/conversation/{session_id}` - Get conversation details
- `PUT /api/conversation/{session_id}` - Update conversation
- `DELETE /api/conversation/{session_id}` - Delete a conversation

### Message
- `POST /api/message/feedback` - Submit message feedback
- `POST /api/message/favorite` - Toggle message favorite status
- `GET /api/message/favorites` - Get favorite messages

### Health Check
- `GET /health` - Check application health

## Redis Usage

- **Rate Limiting**: Limits the number of requests per user per hour (separate limits for chat and API endpoints)
- **Session Quota**: Tracks and manages the quota for each conversation session

## Configuration

The application uses the following default configuration:
- Redis: localhost:6379, db 0
- Chat rate limit: 100 requests per hour per user
- API rate limit: 1000 requests per hour per user
- Initial session quota: 100

## SSE Protocol

The chat endpoint uses Server-Sent Events (SSE) protocol. The response is a stream of events with the following format:

```
data: <message part>

data: [DONE]

```

Where `<message part>` is a chunk of the AI's response, and `[DONE]` indicates the end of the response.
