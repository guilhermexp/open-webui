# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Open WebUI is an extensible, feature-rich, self-hosted AI platform designed to operate entirely offline. It's a full-stack application with:
- **Frontend**: SvelteKit-based web application (TypeScript, Svelte)
- **Backend**: FastAPI-based Python server with extensive AI integrations
- **Database**: SQLAlchemy with support for SQLite/PostgreSQL/MySQL
- **Real-time**: Socket.IO for collaborative features and live updates

## Development Commands

### Frontend Development
```bash
# Install dependencies
npm install

# Run frontend development server (port 5173)
npm run dev:frontend

# Build frontend
npm run build

# Run linting
npm run lint:frontend

# Run frontend tests
npm run test:frontend

# Parse i18n translations
npm run i18n:parse
```

### Backend Development
```bash
# Navigate to backend directory
cd backend

# Create/activate virtual environment and install dependencies
./dev.sh  # This script handles venv setup and runs the server on port 8082

# Or manually:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run backend server
python -m uvicorn open_webui.main:app --port 8082 --host 0.0.0.0 --reload

# Run backend tests
pytest

# Format Python code
black . --exclude ".venv/|/venv/"

# Lint Python code
pylint backend/
```

### Full Stack Development
```bash
# Run both frontend and backend concurrently
npm run dev
```

### Docker Commands
```bash
# Run with Docker (production)
docker run -d -p 3000:8080 -v open-webui:/app/backend/data --name open-webui ghcr.io/open-webui/open-webui:main

# With GPU support
docker run -d -p 3000:8080 --gpus all -v open-webui:/app/backend/data --name open-webui ghcr.io/open-webui/open-webui:cuda
```

## Architecture Overview

### Frontend Structure
- **`/src`**: Main frontend source code
  - **`/lib`**: Shared components and utilities
    - **`/apis`**: API client functions for backend communication
    - **`/components`**: Reusable Svelte components
      - **`/chat`**: Chat interface components
      - **`/workspace`**: Model and tool management
      - **`/admin`**: Admin settings and configuration
    - **`/stores`**: Svelte stores for state management
    - **`/utils`**: Utility functions
  - **`/routes`**: SvelteKit page routes

### Backend Structure
- **`/backend/open_webui`**: Main backend package
  - **`/routers`**: FastAPI route handlers
    - `chats.py`, `models.py`, `users.py`: Core functionality
    - `retrieval.py`: RAG and document processing
    - `mcp.py`: Model Context Protocol integration
  - **`/models`**: SQLAlchemy database models
  - **`/retrieval`**: Document loaders and vector databases
  - **`/utils`**: Utility modules
    - `mcp.py`, `mcp_protocol_handler.py`: MCP implementation
    - `auth.py`: Authentication and authorization
  - **`/socket`**: WebSocket handlers for real-time features

### Key Architectural Patterns

1. **API Communication**: Frontend communicates with backend via REST APIs at `/api/v1/*`
2. **Authentication**: JWT-based authentication with role-based access control
3. **Real-time Updates**: Socket.IO for collaborative editing and live chat updates
4. **Plugin System**: Extensible architecture supporting custom tools and functions
5. **MCP Integration**: Model Context Protocol for external tool integration

### Database Migrations
```bash
# Create new migration
cd backend
alembic revision -m "description"

# Apply migrations
alembic upgrade head

# Downgrade
alembic downgrade -1
```

### Important Configuration

Backend environment variables (set in `backend/dev.sh` or environment):
- `CORS_ALLOW_ORIGIN`: Frontend URL (default: http://localhost:5173)
- `ENABLE_WEB_SEARCH`: Enable web search features
- `YOUTUBE_LOADER_PROXY_URL`: Proxy for YouTube transcript extraction
- `PYTHONPATH`: Include backend directory

### Recent Modifications

1. **YouTube Extraction Enhancement**: 
   - Added fallback loader for rate-limited YouTube API
   - Improved error handling in `youtube.py` and `youtube_fallback.py`
   - Enhanced note formatting in `NoteEditor.svelte`

2. **MCP (Model Context Protocol) Integration**:
   - Full MCP server support (STDIO, HTTP, WebSocket)
   - Tool synchronization and management
   - UI components for server configuration

### Testing

```bash
# Run all backend tests
cd backend
pytest

# Run specific test file
pytest test/apps/webui/routers/test_users.py

# Run with coverage
pytest --cov=open_webui

# Run frontend tests
npm run test:frontend
```

### Key Dependencies

Frontend:
- SvelteKit 2.x
- TipTap editor
- Socket.IO client
- Chart.js
- Mermaid

Backend:
- FastAPI
- SQLAlchemy 2.0
- LangChain
- Various AI provider SDKs (OpenAI, Anthropic, Google)
- youtube-transcript-api
- MCP SDK

### Development Tips

1. The backend uses a virtual environment - always activate it before running
2. Frontend dev server proxies API calls to backend automatically
3. Database is created automatically on first run
4. Check `docs/` directory for detailed documentation on specific features
5. MCP servers are configured per-user and stored in the database
6. Tool IDs follow the pattern: `mcp_{server_id}_{tool_name}`