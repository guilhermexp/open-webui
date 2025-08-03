# MCP Troubleshooting Guide

This guide helps you diagnose and fix common issues with MCP servers in Open WebUI.

## Common Issues and Solutions

### 1. Connection Issues

#### Problem: "Connection Failed" Error

**For STDIO Servers:**

✅ **Check Command Availability**
```bash
# Verify the command exists
which npx
which node
```

✅ **Test Command Manually**
```bash
# Try running the command directly
npx @modelcontextprotocol/server-weather
```

✅ **Check Permissions**
```bash
# Ensure execute permissions
ls -la $(which npx)
```

✅ **Environment Variables**
```javascript
// Ensure PATH includes node/npm
Environment Variables:
  PATH: /usr/local/bin:/usr/bin:/bin
```

**For HTTP Servers:**

✅ **Test URL Accessibility**
```bash
# Test with curl
curl -I https://mcp.smithery.ai/calculator
```

✅ **Check CORS Headers**
```bash
# Look for Access-Control headers
curl -I -H "Origin: http://localhost:3000" https://your-mcp-server.com
```

✅ **Verify MCP Protocol**
```bash
# Test MCP endpoint
curl -X POST https://your-server/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}'
```

**For WebSocket Servers:**

✅ **Test WebSocket Connection**
```javascript
// In browser console
const ws = new WebSocket('wss://your-server/mcp');
ws.onopen = () => console.log('Connected');
ws.onerror = (e) => console.error('Error:', e);
```

### 2. Tool Sync Issues

#### Problem: "No tools found" after sync

**Check Server Response:**
1. Enable debug logging
2. Check Open WebUI logs
3. Look for tool list response

**Verify Tool Format:**
```javascript
// Tools should have this structure:
{
  "name": "tool_name",
  "description": "Tool description",
  "inputSchema": {
    "type": "object",
    "properties": {
      "param": {"type": "string"}
    }
  }
}
```

**Force Resync:**
1. Disable the server (toggle off)
2. Enable the server (toggle on)
3. Click "Sync Tools" again

### 3. Tool Execution Failures

#### Problem: "Tool execution failed"

**Check Parameters:**
```javascript
// Ensure parameters match schema
Tool expects: {"text": "string"}
You provided: {"message": "string"}  // Wrong parameter name!
```

**Verify Authentication:**
```javascript
// For authenticated servers
Environment Variables:
  API_KEY: your-actual-api-key  // Not a placeholder!
```

**Check Rate Limits:**
- Some servers have rate limits
- Wait and retry
- Check server documentation

### 4. UI/Selection Issues

#### Problem: Tools not appearing in model configuration

**Steps to Fix:**
1. Refresh the page (F5)
2. Clear browser cache
3. Check browser console for errors
4. Verify tools are synced (check count)

#### Problem: Can't select MCP server checkbox

**Possible Causes:**
- No tools synced yet
- Server is disabled
- Browser JavaScript error

**Solution:**
1. Sync tools first
2. Enable the server
3. Check browser console (F12)

### 5. Performance Issues

#### Problem: Slow tool execution

**Optimize Connection:**
```javascript
// For HTTP servers, check latency
ping your-server.com

// For STDIO, check process resources
top | grep mcp
```

**Reduce Server Load:**
- Disable unused servers
- Limit concurrent executions
- Use caching when available

## Debugging Techniques

### 1. Enable Debug Logging

**Backend Logging:**
```bash
# In your .env file
LOG_LEVEL=DEBUG

# Or set environment variable
export LOG_LEVEL=DEBUG
```

**Frontend Logging:**
```javascript
// In browser console
localStorage.setItem('debug', 'true');
```

### 2. Check Browser Console

Press F12 and look for:
- Network errors (red entries)
- JavaScript errors
- Failed API calls

### 3. Inspect Network Traffic

In browser DevTools:
1. Go to Network tab
2. Filter by "mcp"
3. Check request/response details

### 4. Server Logs

**For STDIO servers:**
```bash
# Run manually to see output
npx @modelcontextprotocol/server-weather 2>&1 | tee debug.log
```

**For Docker deployment:**
```bash
docker logs open-webui
```

### 5. Database Inspection

**Check server configuration:**
```sql
SELECT * FROM mcp_servers WHERE user_id = 'your-user-id';
```

**Check synced tools:**
```sql
SELECT * FROM mcp_tools WHERE server_id = 'server-id';
```

## Error Messages Explained

### "Failed to connect to MCP server"
- **Cause**: Server unreachable or wrong configuration
- **Fix**: Verify server details and network connectivity

### "No matching route found for operationId"
- **Cause**: Tool name mismatch or protocol error
- **Fix**: Resync tools or check server implementation

### "Request timeout"
- **Cause**: Server took too long to respond
- **Fix**: Check server performance or increase timeout

### "Invalid JSON response"
- **Cause**: Server returned malformed data
- **Fix**: Check server logs for errors

### "Permission denied"
- **Cause**: Insufficient permissions for STDIO command
- **Fix**: Check file permissions and user context

## Platform-Specific Issues

### Docker Deployment

**Container Networking:**
```yaml
# Ensure MCP servers are accessible
services:
  open-webui:
    extra_hosts:
      - "host.docker.internal:host-gateway"
```

**Volume Permissions:**
```bash
# Fix permission issues
docker exec open-webui chown -R user:user /app/data
```

### Kubernetes Deployment

**Service Discovery:**
```yaml
# Ensure DNS resolution works
apiVersion: v1
kind: Service
metadata:
  name: mcp-server
spec:
  type: ClusterIP
```

### Windows Issues

**Path Formatting:**
```javascript
// Use forward slashes or escaped backslashes
Command: C:/Program Files/nodejs/npx.cmd
// or
Command: C:\\Program Files\\nodejs\\npx.cmd
```

**PowerShell Execution:**
```powershell
# Allow script execution
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Recovery Procedures

### 1. Complete Reset

If nothing works:
1. Delete all MCP servers
2. Clear browser cache
3. Restart Open WebUI
4. Re-add servers one by one

### 2. Database Cleanup

```sql
-- Remove orphaned tools
DELETE FROM mcp_tools 
WHERE server_id NOT IN (SELECT id FROM mcp_servers);

-- Reset sync status
UPDATE mcp_servers SET updated_at = 0 WHERE id = 'server-id';
```

### 3. Manual Tool Registration

If sync fails but server works:
1. Use test connection to get tools
2. Manually create tool entries
3. Report issue with logs

## Getting Help

### Information to Collect

When reporting issues, include:

1. **Environment:**
   - Open WebUI version
   - Deployment method (Docker/pip/etc)
   - Operating system
   - Browser and version

2. **Configuration:**
   - Server type and transport
   - Sanitized server configuration
   - Tool specifications

3. **Logs:**
   - Browser console errors
   - Backend logs (with debug enabled)
   - Network traces

4. **Steps to Reproduce:**
   - Exact steps taken
   - Expected behavior
   - Actual behavior

### Where to Get Help

1. **Documentation:**
   - This guide
   - MCP server documentation
   - Open WebUI docs

2. **Community:**
   - Open WebUI Discord
   - GitHub Issues
   - MCP community

3. **Debugging Tools:**
   - MCP protocol validator
   - Server test utilities
   - Log analyzers

## Prevention Tips

### 1. Test Before Production
- Always test new servers in development
- Verify tools work as expected
- Document working configurations

### 2. Monitor Performance
- Track execution times
- Watch for errors
- Set up alerts

### 3. Regular Maintenance
- Update servers periodically
- Clean up unused servers
- Review logs monthly

### 4. Security Best Practices
- Use HTTPS for remote servers
- Rotate API keys regularly
- Limit server permissions
- Audit access logs

## FAQ

**Q: Can I use MCP servers behind a proxy?**
A: Yes, configure proxy settings in environment variables.

**Q: How many servers can I add?**
A: No hard limit, but performance may degrade with many servers.

**Q: Can I share MCP servers between users?**
A: No, each user must configure their own servers.

**Q: Do MCP tools work offline?**
A: STDIO servers can work offline, HTTP/WebSocket need network.

**Q: Can I create custom MCP servers?**
A: Yes, follow the MCP protocol specification.

---

Still having issues? Join our Discord community for help!