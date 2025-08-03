# MCP (Model Context Protocol) Integration Documentation

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Quick Start Guide](#quick-start-guide)
4. [API Reference](#api-reference)
5. [User Guide](#user-guide)
6. [Developer Guide](#developer-guide)
7. [Troubleshooting](#troubleshooting)

## Overview

The Model Context Protocol (MCP) integration in Open WebUI enables seamless connection to external tool servers, allowing AI assistants to access and execute tools from various MCP-compatible servers.

### Key Features
- 🔌 **Multiple Transport Support**: STDIO, HTTP, and WebSocket connections
- 🛠️ **Dynamic Tool Discovery**: Automatic detection and registration of available tools
- 🎯 **Grouped Tool Selection**: Select all tools from a server with one click
- 🔒 **User Isolation**: Each user manages their own MCP servers
- ⚡ **Real-time Synchronization**: Keep tools updated with server changes

## Architecture

### System Components

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Frontend UI   │────▶│   Backend API    │────▶│   MCP Servers   │
│                 │     │                  │     │                 │
│ - ToolsSelector │     │ - MCPManager     │     │ - Smithery      │
│ - MCP Settings  │     │ - ToolAdapter    │     │ - Composio      │
│ - Server Cards  │     │ - ProtocolHandler│     │ - Custom        │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

### Core Components

#### 1. **Frontend Components**
- `ToolsSelector.svelte`: Enhanced tool selection with MCP server grouping
- `MCP.svelte`: MCP server management interface
- `MCPServerCard.svelte`: Individual server configuration
- `MCPMarketplace.svelte`: Server discovery (deprecated)

#### 2. **Backend Modules**
- `models/mcp.py`: Database models and business logic
- `routers/mcp.py`: REST API endpoints
- `utils/mcp.py`: MCP connection manager
- `utils/mcp_protocol_handler.py`: Official MCP protocol implementation
- `utils/mcp_tool_adapter.py`: Tool wrapper generation

#### 3. **Database Schema**
```sql
-- MCP Servers Table
CREATE TABLE mcp_servers (
    id VARCHAR PRIMARY KEY,
    user_id VARCHAR NOT NULL,
    name TEXT NOT NULL,
    transport_type VARCHAR NOT NULL,
    command TEXT,
    url TEXT,
    args JSON DEFAULT '[]',
    env JSON DEFAULT '{}',
    enabled BOOLEAN DEFAULT TRUE,
    meta JSON DEFAULT '{}',
    created_at BIGINT,
    updated_at BIGINT
);

-- MCP Tools Table
CREATE TABLE mcp_tools (
    id VARCHAR PRIMARY KEY,
    server_id VARCHAR NOT NULL,
    tool_name VARCHAR NOT NULL,
    description TEXT,
    parameters JSON DEFAULT '{}',
    enabled BOOLEAN DEFAULT TRUE,
    created_at BIGINT,
    FOREIGN KEY (server_id) REFERENCES mcp_servers(id) ON DELETE CASCADE
);
```

## Quick Start Guide

### 1. Adding an MCP Server

1. Navigate to **Settings** → **MCP**
2. Click **"+ Add MCP Server"**
3. Configure the server:
   - **Name**: Display name for the server
   - **Transport Type**: Select STDIO, HTTP, or WebSocket
   - **Configuration**: Provide command/URL based on transport type
4. Test connection and save

### 2. Syncing Tools

1. Open the MCP server card
2. Click **"Sync Tools"**
3. Tools will be automatically discovered and registered
4. Check the tool count indicator

### 3. Using MCP Tools in Models

1. Go to **Models** → Select/Create a model
2. In the **Tools** section, you'll see MCP servers listed separately
3. Click the checkbox next to an MCP server to select ALL its tools
4. Save the model configuration

## API Reference

### Endpoints

#### Server Management

**GET /api/v1/mcp/**
- Description: List all MCP servers for the current user
- Response: `MCPServer[]`

**POST /api/v1/mcp/**
- Description: Create a new MCP server
- Body: `MCPServerForm`
- Response: `MCPServer`

**PUT /api/v1/mcp/{server_id}**
- Description: Update an MCP server
- Body: `MCPServerForm`
- Response: `MCPServer`

**DELETE /api/v1/mcp/{server_id}**
- Description: Delete an MCP server
- Response: `{detail: string}`

**POST /api/v1/mcp/{server_id}/toggle**
- Description: Enable/disable an MCP server
- Body: `{enabled: boolean}`
- Response: `MCPServer`

#### Tool Operations

**GET /api/v1/mcp/{server_id}/tools**
- Description: List tools for an MCP server
- Response: `MCPTool[]`

**POST /api/v1/mcp/{server_id}/sync**
- Description: Sync tools from MCP server to Open WebUI
- Response: `{detail: string, count: number}`

**POST /api/v1/mcp/{server_id}/test**
- Description: Test connection to MCP server
- Response: `MCPConnectionStatus`

**GET /api/v1/mcp/with-tools-count**
- Description: Get servers with tool counts
- Response: `MCPServerWithCount[]`

### Data Models

#### MCPServerForm
```typescript
interface MCPServerForm {
    name: string;
    transport_type: 'stdio' | 'http' | 'websocket';
    command?: string;       // Required for stdio
    url?: string;          // Required for http/websocket
    args?: string[];       // Command arguments
    env?: Record<string, string>;  // Environment variables
    enabled: boolean;
    meta?: Record<string, any>;
}
```

#### MCPServer
```typescript
interface MCPServer extends MCPServerForm {
    id: string;
    user_id: string;
    created_at: number;
    updated_at: number;
}
```

#### MCPTool
```typescript
interface MCPTool {
    id: string;
    server_id: string;
    tool_name: string;
    description?: string;
    parameters: Record<string, any>;
    enabled: boolean;
    created_at: number;
}
```

## User Guide

### Managing MCP Servers

#### Adding a STDIO Server
```bash
# Example: Weather server
Name: Weather Tools
Transport: STDIO
Command: /usr/local/bin/mcp-weather
Args: ["--api-key", "your-key"]
```

#### Adding an HTTP Server
```
Name: Smithery Calculator
Transport: HTTP
URL: https://mcp.smithery.ai/calculator
```

#### Adding a WebSocket Server
```
Name: Custom WebSocket Server
Transport: WebSocket
URL: wss://example.com/mcp
```

### Tool Selection Best Practices

1. **Group Selection**: Use the MCP server checkbox to select all tools at once
2. **Selective Usage**: Only enable servers you actively use
3. **Regular Sync**: Sync tools periodically to get updates
4. **Testing**: Always test connection before saving

### Security Considerations

- MCP servers are user-specific - no sharing between users
- Environment variables can store sensitive data
- Use HTTPS/WSS for remote servers
- Validate server certificates

## Developer Guide

### Adding a New Transport Type

1. Update `MCPTransportType` enum in `models/mcp.py`
2. Implement connection method in `MCPManager`
3. Add UI support in `MCPServerModal.svelte`

### Creating Custom MCP Servers

Follow the official MCP specification:
```python
# Example MCP server implementation
async def handle_tools_list():
    return {
        "tools": [{
            "name": "my_tool",
            "description": "My custom tool",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "param": {"type": "string"}
                }
            }
        }]
    }
```

### Tool Wrapper Generation

The system automatically generates Python wrappers:
```python
# Generated wrapper example
async def my_tool(self, param):
    from open_webui.utils.mcp import mcp_manager
    result = await mcp_manager.call_tool(
        "server_id",
        "my_tool",
        {"param": param}
    )
    return {"status": "success", "result": result}
```

## Troubleshooting

### Common Issues

#### Connection Failed
- **STDIO**: Check command path and permissions
- **HTTP**: Verify URL accessibility and CORS settings
- **WebSocket**: Ensure WebSocket support and proper URL format

#### Tools Not Appearing
1. Check server is enabled
2. Verify successful sync
3. Check browser console for errors
4. Ensure tools have proper specifications

#### Execution Errors
- Check server logs for detailed errors
- Verify parameter formats match specifications
- Ensure server is running and accessible

### Debug Mode

Enable debug logging:
```python
# In your .env file
LOG_LEVEL=DEBUG
```

### Getting Help

1. Check server-specific documentation
2. Review Open WebUI logs
3. Test with official MCP tools first
4. Report issues with full error details

## Migration Guide

### From Individual Tool Selection

The new grouped selection maintains backward compatibility:
- Existing tool selections are preserved
- Individual MCP tools can still be selected
- Group selection is additive to existing selections

### Database Migration

The migration `20250801182305_add_mcp_tables.py` creates necessary tables automatically.

## Future Enhancements

- [ ] Custom server icons
- [ ] Tool usage analytics
- [ ] Batch server operations
- [ ] Tool favorites/pinning
- [ ] Server health monitoring
- [ ] Marketplace integration

## References

- [MCP Specification](https://github.com/anthropics/mcp)
- [Open WebUI Documentation](https://docs.openwebui.com)
- [Smithery MCP Tools](https://smithery.ai)
- [Composio MCP Integration](https://composio.dev)