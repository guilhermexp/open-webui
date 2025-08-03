"""
MCP Protocol Handler
Handles different MCP server types using the official MCP client library
Inspired by Suna's implementation
"""
import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from mcp import ClientSession
from mcp.client.sse import sse_client
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.streamable_http import streamablehttp_client

log = logging.getLogger(__name__)


@dataclass
class MCPToolResult:
    """Result from MCP tool execution"""
    success: bool
    content: Any
    error: Optional[str] = None


class MCPProtocolHandler:
    """Handles MCP protocol connections and tool execution"""
    
    def __init__(self):
        self.active_sessions: Dict[str, ClientSession] = {}
    
    async def connect_server(self, server_url: str, server_type: str = "http", headers: Optional[Dict] = None) -> Tuple[bool, Optional[str]]:
        """Connect to an MCP server based on type"""
        try:
            if server_type == "http":
                return await self._connect_http(server_url)
            elif server_type == "sse":
                return await self._connect_sse(server_url, headers)
            elif server_type == "stdio":
                # For stdio, server_url should be a JSON string with command info
                import json
                config = json.loads(server_url) if isinstance(server_url, str) else server_url
                return await self._connect_stdio(config)
            else:
                return False, f"Unsupported server type: {server_type}"
        except Exception as e:
            log.error(f"Failed to connect to MCP server: {e}")
            return False, str(e)
    
    async def _connect_http(self, url: str) -> Tuple[bool, Optional[str]]:
        """Connect to HTTP MCP server"""
        try:
            async with asyncio.timeout(30):
                # Create connection but don't store it yet
                # We'll establish a persistent connection when needed
                async with streamablehttp_client(url) as (read_stream, write_stream, _):
                    async with ClientSession(read_stream, write_stream) as session:
                        await session.initialize()
                        # Connection successful
                        return True, None
        except Exception as e:
            return False, str(e)
    
    async def _connect_sse(self, url: str, headers: Optional[Dict] = None) -> Tuple[bool, Optional[str]]:
        """Connect to SSE MCP server"""
        try:
            async with asyncio.timeout(30):
                if headers:
                    async with sse_client(url, headers=headers) as (read_stream, write_stream):
                        async with ClientSession(read_stream, write_stream) as session:
                            await session.initialize()
                            return True, None
                else:
                    async with sse_client(url) as (read_stream, write_stream):
                        async with ClientSession(read_stream, write_stream) as session:
                            await session.initialize()
                            return True, None
        except Exception as e:
            return False, str(e)
    
    async def _connect_stdio(self, config: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Connect to stdio MCP server"""
        try:
            server_params = StdioServerParameters(
                command=config["command"],
                args=config.get("args", []),
                env=config.get("env", {})
            )
            
            async with asyncio.timeout(30):
                async with stdio_client(server_params) as (read_stream, write_stream):
                    async with ClientSession(read_stream, write_stream) as session:
                        await session.initialize()
                        return True, None
        except Exception as e:
            return False, str(e)
    
    async def list_tools(self, server_url: str, server_type: str = "http", headers: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """List available tools from an MCP server"""
        tools = []
        
        try:
            if server_type == "http":
                async with streamablehttp_client(server_url) as (read_stream, write_stream, _):
                    async with ClientSession(read_stream, write_stream) as session:
                        await session.initialize()
                        tool_result = await session.list_tools()
                        
                        for tool in tool_result.tools:
                            tools.append({
                                "name": tool.name,
                                "description": tool.description,
                                "inputSchema": tool.inputSchema
                            })
            
            elif server_type == "sse":
                client_context = sse_client(server_url, headers=headers) if headers else sse_client(server_url)
                async with client_context as (read_stream, write_stream):
                    async with ClientSession(read_stream, write_stream) as session:
                        await session.initialize()
                        tool_result = await session.list_tools()
                        
                        for tool in tool_result.tools:
                            tools.append({
                                "name": tool.name,
                                "description": tool.description,
                                "inputSchema": tool.inputSchema
                            })
            
            return tools
            
        except Exception as e:
            log.error(f"Failed to list tools: {e}")
            return []
    
    async def execute_tool(self, server_url: str, server_type: str, tool_name: str, 
                          arguments: Dict[str, Any], headers: Optional[Dict] = None) -> MCPToolResult:
        """Execute a tool on an MCP server"""
        try:
            if server_type == "http":
                return await self._execute_http_tool(server_url, tool_name, arguments)
            elif server_type == "sse":
                return await self._execute_sse_tool(server_url, tool_name, arguments, headers)
            else:
                return MCPToolResult(
                    success=False,
                    content=None,
                    error=f"Unsupported server type: {server_type}"
                )
        except Exception as e:
            log.error(f"Tool execution failed: {e}")
            return MCPToolResult(
                success=False,
                content=None,
                error=str(e)
            )
    
    async def _execute_http_tool(self, url: str, tool_name: str, arguments: Dict[str, Any]) -> MCPToolResult:
        """Execute tool on HTTP MCP server"""
        try:
            async with asyncio.timeout(30):
                async with streamablehttp_client(url) as (read_stream, write_stream, _):
                    async with ClientSession(read_stream, write_stream) as session:
                        await session.initialize()
                        result = await session.call_tool(tool_name, arguments)
                        
                        content = self._extract_content(result)
                        return MCPToolResult(success=True, content=content)
                        
        except Exception as e:
            return MCPToolResult(success=False, content=None, error=str(e))
    
    async def _execute_sse_tool(self, url: str, tool_name: str, arguments: Dict[str, Any], 
                               headers: Optional[Dict] = None) -> MCPToolResult:
        """Execute tool on SSE MCP server"""
        try:
            async with asyncio.timeout(30):
                client_context = sse_client(url, headers=headers) if headers else sse_client(url)
                async with client_context as (read_stream, write_stream):
                    async with ClientSession(read_stream, write_stream) as session:
                        await session.initialize()
                        result = await session.call_tool(tool_name, arguments)
                        
                        content = self._extract_content(result)
                        return MCPToolResult(success=True, content=content)
                        
        except Exception as e:
            return MCPToolResult(success=False, content=None, error=str(e))
    
    def _extract_content(self, result) -> str:
        """Extract content from MCP result"""
        if hasattr(result, 'content'):
            content = result.content
            if isinstance(content, list):
                text_parts = []
                for item in content:
                    if hasattr(item, 'text'):
                        text_parts.append(item.text)
                    else:
                        text_parts.append(str(item))
                return "\n".join(text_parts)
            elif hasattr(content, 'text'):
                return content.text
            else:
                return str(content)
        else:
            return str(result)


# Global instance
mcp_protocol_handler = MCPProtocolHandler()