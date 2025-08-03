# Example MCP Server for Open WebUI

This is a simple example of an MCP (Model Context Protocol) server that can be connected to Open WebUI.

## Setup

1. Install dependencies:
```bash
cd mcp-example
npm install
```

2. Test the server locally:
```bash
node example-mcp-server.js
```

## Connecting to Open WebUI

To connect this local MCP server to Open WebUI:

1. Go to Settings -> Admin -> MCP
2. Click "Add Server"
3. Configure as follows:
   - **Name**: Local Example Server
   - **Transport Type**: stdio
   - **Command**: `node`
   - **Arguments**: `/Users/guilhermevarela/Documents/Repositorios/open-webui/mcp-example/example-mcp-server.js`
   - **Enabled**: ✅

4. Click "Save"
5. Click "Test Connection" to verify it works
6. Click "Sync Tools" to import the tools

## Available Tools

This example server provides 3 simple tools:

1. **hello_world** - Says hello to someone
   - Input: `name` (string)
   - Example: `{"name": "Alice"}`

2. **add_numbers** - Adds two numbers
   - Input: `a` (number), `b` (number)
   - Example: `{"a": 5, "b": 3}`

3. **get_current_time** - Gets the current time
   - No inputs required

## Creating Your Own MCP Server

To create your own MCP server, follow the pattern in `example-mcp-server.js`:

1. Import the MCP SDK
2. Create a server instance
3. Define your tools in the `tools/list` handler
4. Implement tool logic in the `tools/call` handler
5. Start the server with stdio transport

## Troubleshooting

If the connection fails:
- Make sure Node.js is installed and in your PATH
- Check that the full path to the script is correct
- Ensure the script has execute permissions
- Check the Open WebUI logs for detailed error messages