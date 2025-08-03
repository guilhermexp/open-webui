# MCP Architecture Documentation

## Overview

The MCP (Model Context Protocol) integration in Open WebUI follows a modular architecture that separates concerns between transport management, protocol handling, tool adaptation, and user interface.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Open WebUI Frontend                              │
├─────────────────┬─────────────────┬─────────────────┬───────────────────────┤
│  ToolsSelector  │   MCP Settings   │  Model Config   │    Chat Interface     │
│   (Enhanced)    │   Management     │   Integration   │    Tool Execution     │
└────────┬────────┴────────┬─────────┴────────┬────────┴──────────┬───────────┘
         │                 │                   │                   │
         ▼                 ▼                   ▼                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           REST API Layer (/api/v1/mcp)                       │
├─────────────────┬─────────────────┬─────────────────┬───────────────────────┤
│  Server CRUD    │  Tool Sync      │  Connection Test │   Tool Execution      │
└────────┬────────┴────────┬─────────┴────────┬────────┴──────────┬───────────┘
         │                 │                   │                   │
         ▼                 ▼                   ▼                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Backend Core Services                            │
├─────────────────┬─────────────────┬─────────────────┬───────────────────────┤
│   MCPManager    │ ProtocolHandler │  ToolAdapter    │   Tool Registry       │
│ (Connection Mgr)│  (MCP Protocol) │ (Code Generator)│   (Open WebUI)       │
└────────┬────────┴────────┬─────────┴────────┬────────┴──────────┬───────────┘
         │                 │                   │                   │
         ▼                 ▼                   ▼                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            Transport Layer                                    │
├─────────────────┬─────────────────┬─────────────────────────────────────────┤
│      STDIO      │      HTTP       │            WebSocket                     │
│   (Process)     │   (REST API)    │         (Persistent)                     │
└────────┬────────┴────────┬─────────┴──────────┬─────────────────────────────┘
         │                 │                     │
         ▼                 ▼                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          External MCP Servers                                 │
├─────────────────┬─────────────────┬─────────────────────────────────────────┤
│    Smithery     │    Composio     │         Custom Servers                   │
│  (HTTP/MCP)     │   (HTTP/MCP)    │    (STDIO/HTTP/WebSocket)               │
└─────────────────┴─────────────────┴─────────────────────────────────────────┘
```

## Component Details

### 1. Frontend Layer

#### ToolsSelector.svelte (Enhanced)
```javascript
// Key Features:
- MCP server grouping
- Batch tool selection
- Real-time server status
- Tool count display

// Data Flow:
1. Load MCP servers via API
2. Group tools by server_id prefix
3. Handle batch selection/deselection
4. Update selectedToolIds array
```

#### MCP Settings Components
- `MCP.svelte`: Main settings interface
- `MCPServerCard.svelte`: Individual server management
- `MCPServerModal.svelte`: Server configuration dialog
- `MCPConnectModal.svelte`: Quick connection wizard

### 2. API Layer

#### Endpoints Structure
```python
/api/v1/mcp/
├── GET    /                    # List user's servers
├── POST   /                    # Create server
├── GET    /{id}               # Get server details
├── PUT    /{id}               # Update server
├── DELETE /{id}               # Delete server
├── POST   /{id}/toggle        # Enable/disable
├── POST   /{id}/test          # Test connection
├── GET    /{id}/tools         # List tools
├── POST   /{id}/sync          # Sync tools
└── GET    /with-tools-count   # Servers with counts
```

### 3. Backend Services

#### MCPManager (utils/mcp.py)
```python
class MCPManager:
    """Central connection manager"""
    
    connections: Dict[str, MCPConnection]  # Active connections
    
    async def connect(server: MCPServerModel) -> MCPConnection
    async def get_available_tools(server_id: str) -> List[Dict]
    async def call_tool(server_id: str, tool_name: str, args: Dict) -> Any
    async def disconnect(server_id: str) -> None
```

#### MCPProtocolHandler (utils/mcp_protocol_handler.py)
```python
class MCPProtocolHandler:
    """Official MCP protocol implementation"""
    
    async def connect_server(url: str, type: str) -> Tuple[bool, Optional[str]]
    async def list_tools(url: str, type: str) -> List[Dict]
    async def execute_tool(url: str, type: str, tool: str, args: Dict) -> MCPToolResult
```

#### MCPToolAdapter (utils/mcp_tool_adapter.py)
```python
class MCPToolAdapter:
    """Bridges MCP tools to Open WebUI"""
    
    @staticmethod
    async def sync_server_tools(server: MCPServerModel, user_id: str) -> Dict
    
    @staticmethod
    def _generate_tool_content(server_id: str, tool: Dict) -> str
        """Generates Python wrapper code"""
```

### 4. Database Schema

#### Tables Structure
```sql
mcp_servers
├── id (VARCHAR, PK)
├── user_id (VARCHAR, NOT NULL)
├── name (TEXT, NOT NULL)
├── transport_type (VARCHAR)
├── command (TEXT, nullable)
├── url (TEXT, nullable)
├── args (JSON)
├── env (JSON)
├── enabled (BOOLEAN)
├── meta (JSON)
├── created_at (BIGINT)
└── updated_at (BIGINT)

mcp_tools
├── id (VARCHAR, PK)
├── server_id (VARCHAR, FK)
├── tool_name (VARCHAR)
├── description (TEXT)
├── parameters (JSON)
├── enabled (BOOLEAN)
└── created_at (BIGINT)
```

## Data Flow Patterns

### 1. Server Configuration Flow
```
User Input → Frontend Validation → API Request → 
Backend Validation → Database Storage → Response
```

### 2. Tool Discovery Flow
```
Sync Request → MCPManager.connect() → 
Protocol Detection → Tool List Request → 
Tool Registration → Database Storage → 
Wrapper Generation → UI Update
```

### 3. Tool Execution Flow
```
Assistant Request → Tool Resolution → 
Wrapper Function Call → MCPManager.call_tool() → 
Protocol Translation → Server Execution → 
Result Processing → Assistant Response
```

## Protocol Detection Logic

The system automatically detects the appropriate protocol:

```python
# In MCPManager.connect()
if "smithery.ai" in server.url or "mcp.sh" in server.url:
    # Use MCPProtocolHandler (official MCP protocol)
    connection.use_protocol_handler = True
elif server.transport_type == MCPTransportType.STDIO:
    # Standard JSON-RPC over stdio
    connection = await self._connect_stdio(connection)
elif server.transport_type == MCPTransportType.HTTP:
    # HTTP with automatic protocol detection
    connection = await self._connect_http(connection)
```

## Tool ID Convention

MCP tools follow a specific ID pattern:
```
mcp_{server_id}_{tool_name}

Example:
mcp_abc123def_tweet
│   │        └─── Tool name
│   └──────────── Server UUID
└──────────────── MCP prefix
```

## Security Architecture

### 1. User Isolation
- Each user has separate MCP server configurations
- No cross-user server access
- Tool permissions tied to user context

### 2. Connection Security
- HTTPS/WSS recommended for remote servers
- Environment variables for sensitive data
- No credential storage in plain text

### 3. Execution Sandboxing
- Tool execution through controlled wrappers
- Parameter validation before execution
- Result sanitization

## Performance Considerations

### 1. Connection Pooling
- Persistent connections reused when possible
- Automatic reconnection on failure
- Connection health checks

### 2. Caching Strategy
- Tool specifications cached per session
- Server metadata cached
- No result caching (real-time execution)

### 3. Async Architecture
- All I/O operations are async
- Concurrent tool execution support
- Non-blocking UI updates

## Extension Points

### 1. Adding New Transport Types
1. Update `MCPTransportType` enum
2. Implement `_connect_<type>` method in MCPManager
3. Add UI support in frontend
4. Update validation logic

### 2. Custom Protocol Handlers
1. Implement protocol detection logic
2. Create handler class
3. Register in MCPManager
4. Add connection routing

### 3. Tool Enhancement
1. Modify wrapper generation template
2. Add pre/post processing hooks
3. Implement custom result handlers
4. Extend parameter validation

## Error Handling Strategy

### 1. Connection Errors
- Retry with exponential backoff
- Graceful degradation
- User-friendly error messages

### 2. Tool Execution Errors
- Capture and wrap exceptions
- Preserve error context
- Return standardized error format

### 3. Sync Errors
- Partial sync support
- Rollback on critical failures
- Detailed error reporting

## Monitoring and Debugging

### 1. Logging Points
- Connection establishment
- Tool discovery
- Execution requests
- Error conditions

### 2. Debug Information
```python
# Enable debug logging
LOG_LEVEL=DEBUG

# Key log points:
- MCPManager operations
- Protocol handler communication
- Tool wrapper execution
- Database operations
```

### 3. Health Checks
- Connection status endpoint
- Tool availability verification
- Server responsiveness metrics

## Future Architecture Considerations

### 1. Scalability
- Connection pool limits
- Rate limiting per server
- Distributed connection management

### 2. Extensibility
- Plugin architecture for protocols
- Custom tool transformers
- Webhook support for events

### 3. Observability
- Metrics collection
- Distributed tracing
- Performance profiling

## Best Practices

### 1. Connection Management
- Lazy connection establishment
- Proper cleanup on shutdown
- Connection timeout handling

### 2. Error Propagation
- Preserve error context
- Standardize error formats
- User-actionable messages

### 3. Testing Strategy
- Unit tests for components
- Integration tests for protocols
- E2E tests for user flows