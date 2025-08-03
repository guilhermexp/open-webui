# MCP User Guide - Open WebUI

This guide will help you get started with MCP (Model Context Protocol) servers in Open WebUI.

## What is MCP?

MCP (Model Context Protocol) is a standard protocol that allows AI assistants to connect to external tool servers. These servers can provide various capabilities like:
- 🐦 Social media integration (Twitter/X)
- 📁 File system access
- 🌐 Web scraping
- 📊 Data analysis
- 🔧 System utilities
- And much more!

## Getting Started

### Step 1: Access MCP Settings

1. Click on your profile icon in the top-right corner
2. Select **Settings**
3. Navigate to the **MCP** tab

### Step 2: Add Your First MCP Server

Let's add a simple MCP server:

1. Click **"+ Add MCP Server"**
2. Fill in the configuration:

#### Example: Weather Server (STDIO)
```
Name: Weather Tools
Transport Type: STDIO
Command: npx
Arguments: @modelcontextprotocol/server-weather
```

#### Example: Smithery Calculator (HTTP)
```
Name: Calculator
Transport Type: HTTP
URL: https://mcp.smithery.ai/calculator
```

3. Click **"Test Connection"** to verify it works
4. Click **"Save"** to add the server

### Step 3: Sync Tools

After adding a server:

1. Find your server in the MCP servers list
2. Click the **"Sync Tools"** button
3. Wait for the success message showing tool count

### Step 4: Enable Tools in Your Model

1. Go to **Models** section
2. Select or create a model
3. Scroll to the **Tools** section
4. You'll see your MCP servers listed with their icon
5. Click the checkbox next to the MCP server name
   - This automatically selects ALL tools from that server!
6. Save your model

### Step 5: Use the Tools

Now you can ask your AI assistant to use the tools:

```
"What's the weather in New York?"
"Calculate the square root of 144"
"Post a tweet saying 'Hello from Open WebUI!'"
```

## Popular MCP Servers

### Official Servers

#### 1. File System Access
```
Name: File System
Transport: STDIO
Command: npx
Arguments: @modelcontextprotocol/server-filesystem
Environment Variables:
  ALLOWED_DIRECTORIES: /path/to/allowed/folder
```

#### 2. Google Drive
```
Name: Google Drive
Transport: STDIO
Command: npx
Arguments: @modelcontextprotocol/server-gdrive
```

#### 3. GitHub
```
Name: GitHub
Transport: STDIO
Command: npx
Arguments: @modelcontextprotocol/server-github
Environment Variables:
  GITHUB_TOKEN: your_github_token
```

### Smithery Servers (HTTP)

Smithery provides ready-to-use MCP servers:

1. **Calculator**: `https://mcp.smithery.ai/calculator`
2. **Web Scraper**: `https://mcp.smithery.ai/web-scraper`
3. **JSON Tools**: `https://mcp.smithery.ai/json`

### Custom Servers

You can also connect to your own MCP servers:

```
Name: My Custom Server
Transport: HTTP
URL: http://localhost:3000/mcp
```

## Managing MCP Servers

### Enable/Disable Servers

Toggle the switch on each server card to enable or disable without deleting.

### Update Configuration

1. Click the edit icon on the server card
2. Modify settings
3. Save changes

### Delete Servers

1. Click the trash icon on the server card
2. Confirm deletion

## Tips and Best Practices

### 1. **Group Selection is Powerful**
Instead of selecting individual tools, use the MCP server checkbox to select all tools at once. This ensures you don't miss any functionality.

### 2. **Test Before Production**
Always use the "Test Connection" button before saving a new server configuration.

### 3. **Security Considerations**
- Only add servers you trust
- Use environment variables for sensitive data like API keys
- Be cautious with file system access permissions

### 4. **Regular Syncing**
Sync tools periodically to get new tools or updates from the server.

### 5. **Performance**
- Only enable servers you actively use
- Disable unused servers to improve performance
- Some servers may have rate limits

## Troubleshooting

### Connection Failed

**For STDIO servers:**
- Check if the command is installed (`which npx`)
- Verify the package name is correct
- Check environment variables

**For HTTP servers:**
- Verify the URL is accessible
- Check for CORS issues
- Ensure the server supports MCP protocol

**For WebSocket servers:**
- Check WebSocket URL format (wss:// or ws://)
- Verify network connectivity

### Tools Not Appearing

1. Make sure the server is enabled
2. Click "Sync Tools" again
3. Check if tools were found during sync
4. Refresh the page

### Tools Not Working

1. Check server logs (if available)
2. Verify tool parameters in the request
3. Check for authentication issues
4. Try the tool with simpler inputs

### Can't Select Tools

1. Ensure tools are synced first
2. Check that the model supports tools
3. Try refreshing the model configuration page

## Advanced Usage

### Environment Variables

For servers requiring authentication:

```
Environment Variables:
  API_KEY: your-api-key
  SECRET: your-secret
```

### Command Arguments

For complex commands:

```
Arguments: ["--port", "3000", "--verbose"]
```

### Custom Headers (HTTP)

Some HTTP servers may require custom headers:
- Currently configured through server metadata
- Contact server documentation for requirements

## Security Notes

1. **User Isolation**: Each user has their own MCP servers
2. **No Sharing**: MCP servers are not shared between users
3. **Local Execution**: STDIO servers run on the Open WebUI server
4. **Network Access**: HTTP/WebSocket servers require network access

## Getting Help

1. Check the server's documentation
2. Look for error messages in:
   - Browser console (F12)
   - Open WebUI logs
   - Server logs
3. Test with official MCP servers first
4. Join the Open WebUI Discord community

## Next Steps

- Explore the [MCP Registry](https://github.com/modelcontextprotocol/servers) for more servers
- Learn to [create your own MCP server](https://modelcontextprotocol.io/docs)
- Share your experience in the community!

---

Happy tool using! 🚀