"""
MCP Smithery Integration
Handles Smithery-specific MCP server connections
"""
import asyncio
import logging
from typing import Dict, List, Any, Optional
from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession

log = logging.getLogger(__name__)


class SmitheryMCPClient:
    """Client for Smithery MCP servers"""
    
    def __init__(self, url: str):
        self.url = url
        self.session = None
        self.read_stream = None
        self.write_stream = None
        self._context = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()
    
    async def connect(self):
        """Connect to Smithery server"""
        try:
            # Create the streamable HTTP connection
            self._context = streamablehttp_client(self.url)
            streams = await self._context.__aenter__()
            self.read_stream, self.write_stream, _ = streams
            
            # Create client session
            self.session = ClientSession(self.read_stream, self.write_stream)
            await self.session.__aenter__()
            
            # Initialize the session
            await self.session.initialize()
            log.info(f"Connected to Smithery server: {self.url}")
            
        except Exception as e:
            log.error(f"Failed to connect to Smithery server: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from Smithery server"""
        try:
            if self.session:
                await self.session.__aexit__(None, None, None)
            if self._context:
                await self._context.__aexit__(None, None, None)
            log.info("Disconnected from Smithery server")
        except Exception as e:
            log.error(f"Error disconnecting: {e}")
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools"""
        if not self.session:
            raise ValueError("Not connected to server")
        
        try:
            result = await self.session.list_tools()
            tools = []
            
            for tool in result.tools:
                tools.append({
                    "name": tool.name,
                    "description": tool.description,
                    "inputSchema": tool.inputSchema
                })
            
            return tools
            
        except Exception as e:
            log.error(f"Failed to list tools: {e}")
            raise
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call a tool"""
        if not self.session:
            raise ValueError("Not connected to server")
        
        try:
            result = await self.session.call_tool(tool_name, arguments)
            
            # Process result based on content type
            if hasattr(result, 'content'):
                content_items = []
                for item in result.content:
                    if hasattr(item, 'type') and item.type == 'text':
                        content_items.append(item.text)
                    else:
                        content_items.append(str(item))
                
                return {
                    "content": content_items,
                    "type": "success"
                }
            
            return result
            
        except Exception as e:
            log.error(f"Failed to call tool {tool_name}: {e}")
            raise


async def test_smithery_connection(url: str) -> Dict[str, Any]:
    """Test connection to a Smithery server"""
    try:
        async with SmitheryMCPClient(url) as client:
            tools = await client.list_tools()
            return {
                "status": "success",
                "tools_count": len(tools),
                "tools": tools
            }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }