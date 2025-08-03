"""
MCP (Model Context Protocol) Manager
Handles connections and communication with MCP servers
"""
import asyncio
import json
import subprocess
import os
import sys
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from contextlib import asynccontextmanager
import httpx
import websockets
from websockets.client import WebSocketClientProtocol
import time
import uuid

from open_webui.models.mcp import MCPServerModel, MCPTransportType, MCPConnectionStatus
from open_webui.utils.mcp_protocol_handler import mcp_protocol_handler, MCPToolResult
import logging

# SunaMCPManager import removed - mcp_local module has been deleted

log = logging.getLogger(__name__)


@dataclass
class MCPConnection:
    """Represents a connection to an MCP server"""
    server: MCPServerModel
    process: Optional[subprocess.Popen] = None
    client: Optional[Union[httpx.AsyncClient, WebSocketClientProtocol]] = None
    stdin: Optional[asyncio.StreamWriter] = None
    stdout: Optional[asyncio.StreamReader] = None
    stderr: Optional[asyncio.StreamReader] = None
    request_id: int = 0
    pending_requests: Dict[str, asyncio.Future] = field(default_factory=dict)
    mcp_session: Optional[Any] = None  # MCP ClientSession for official protocol
    is_mcp_protocol: bool = False  # Whether using official MCP protocol
    smithery_client: Optional[Any] = None  # SmitheryMCPClient for Smithery servers
    is_smithery: bool = False  # Whether this is a Smithery server
    use_protocol_handler: bool = False  # Whether to use the new MCPProtocolHandler
    
    def next_request_id(self) -> str:
        """Generate next request ID"""
        self.request_id += 1
        return str(self.request_id)


class MCPManager:
    """Manages MCP server connections"""
    
    def __init__(self):
        self.connections: Dict[str, MCPConnection] = {}
        self._lock = asyncio.Lock()
        # SunaMCPManager removed - mcp_local module has been deleted
    
    async def connect(self, server: MCPServerModel) -> MCPConnection:
        """Establish connection to an MCP server"""
        async with self._lock:
            # Return existing connection if available
            if server.id in self.connections:
                connection = self.connections[server.id]
                # Check if connection is still alive
                if await self._is_connection_alive(connection):
                    return connection
                else:
                    # Clean up dead connection
                    await self._cleanup_connection(connection)
                    del self.connections[server.id]
            
            # Create new connection for all servers
            connection = MCPConnection(server=server)
            
            try:
                # Check if this is a Smithery, Composio, or other MCP protocol server that needs special handling
                if server.transport_type == MCPTransportType.HTTP and (
                    "smithery.ai" in server.url or 
                    "mcp.sh" in server.url or
                    "composio.dev" in server.url or
                    "/mcp" in server.url
                ):
                    # Use the new MCPProtocolHandler for these servers
                    success, error = await mcp_protocol_handler.connect_server(server.url, "http", server.headers if hasattr(server, 'headers') else None)
                    if success:
                        connection.use_protocol_handler = True
                        connection.is_mcp_protocol = True
                        self.connections[server.id] = connection
                        log.info(f"Connected to MCP protocol server: {server.name}")
                        return connection
                    else:
                        raise ValueError(f"Failed to connect to MCP server: {error}")
                
                if server.transport_type == MCPTransportType.STDIO:
                    connection = await self._connect_stdio(connection)
                elif server.transport_type == MCPTransportType.HTTP:
                    connection = await self._connect_http(connection)
                elif server.transport_type == MCPTransportType.WEBSOCKET:
                    connection = await self._connect_websocket(connection)
                else:
                    raise ValueError(f"Unsupported transport type: {server.transport_type}")
                
                # Initialize MCP protocol
                await self._initialize_protocol(connection)
                
                self.connections[server.id] = connection
                log.info(f"Connected to MCP server: {server.name} ({server.id})")
                return connection
                
            except Exception as e:
                log.error(f"Failed to connect to MCP server {server.name}: {str(e)}")
                await self._cleanup_connection(connection)
                raise
    
    async def _connect_stdio(self, connection: MCPConnection) -> MCPConnection:
        """Connect to MCP server via stdio transport"""
        server = connection.server
        
        # Prepare environment
        env = os.environ.copy()
        if server.env:
            env.update(server.env)
        
        # Prepare command
        cmd = [server.command] + (server.args or [])
        
        log.debug(f"Starting stdio process: {' '.join(cmd)}")
        
        # Start process with asyncio
        try:
            connection.process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env
            )
            
            connection.stdin = connection.process.stdin
            connection.stdout = connection.process.stdout
            connection.stderr = connection.process.stderr
            
            # Start reading stderr in background
            asyncio.create_task(self._read_stderr(connection))
            
            # Start reading stdout for responses
            asyncio.create_task(self._read_stdout(connection))
            
        except FileNotFoundError:
            raise ValueError(f"Command not found: {server.command}")
        except Exception as e:
            raise ValueError(f"Failed to start process: {str(e)}")
        
        return connection
    
    async def _connect_http(self, connection: MCPConnection) -> MCPConnection:
        """Connect to MCP server via HTTP transport"""
        log.debug(f"Connecting to HTTP MCP server at: {connection.server.url}")
        
        # Check if this is a Smithery server URL
        if "smithery.ai" in connection.server.url or "mcp" in connection.server.url.lower():
            # For Smithery servers, we need to use their custom discovery endpoint
            # The sync endpoint should handle the MCP protocol internally
            log.debug("Detected Smithery/MCP server, will use MCP protocol handling")
            connection.is_mcp_protocol = True
        else:
            connection.is_mcp_protocol = False
        
        # Set proper headers for MCP protocol
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        connection.client = httpx.AsyncClient(
            base_url=connection.server.url,
            timeout=30.0,
            headers=headers
        )
        return connection
    
    async def _connect_websocket(self, connection: MCPConnection) -> MCPConnection:
        """Connect to MCP server via WebSocket transport"""
        connection.client = await websockets.connect(
            connection.server.url,
            ping_interval=30,
            ping_timeout=10
        )
        
        # Start reading messages in background
        asyncio.create_task(self._read_websocket(connection))
        
        return connection
    
    async def _initialize_protocol(self, connection: MCPConnection) -> None:
        """Initialize MCP protocol handshake"""
        # Skip initialization for Smithery/MCP protocol servers
        # They handle initialization internally
        if connection.is_mcp_protocol:
            log.debug("Skipping initialization for MCP protocol server")
            return
            
        # Send initialization request for standard JSON-RPC servers
        request = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "Open WebUI",
                    "version": "1.0.0"
                }
            },
            "id": connection.next_request_id()
        }
        
        response = await self._send_request(connection, request)
        
        if "error" in response:
            raise ValueError(f"Initialization failed: {response['error']}")
        
        # Send initialized notification
        notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        
        await self._send_notification(connection, notification)
    
    async def _send_request(self, connection: MCPConnection, request: Dict) -> Dict:
        """Send JSON-RPC request and wait for response"""
        # For MCP protocol servers, we don't send standard JSON-RPC requests
        if connection.is_mcp_protocol:
            raise ValueError("Cannot send JSON-RPC requests to MCP protocol servers")
            
        request_id = request.get("id")
        if not request_id:
            raise ValueError("Request must have an ID")
        
        # Create future for response
        future = asyncio.get_event_loop().create_future()
        connection.pending_requests[request_id] = future
        
        try:
            # Send request based on transport
            if connection.server.transport_type == MCPTransportType.STDIO:
                await self._send_stdio(connection, request)
            elif connection.server.transport_type == MCPTransportType.HTTP:
                return await self._send_http(connection, request)
            elif connection.server.transport_type == MCPTransportType.WEBSOCKET:
                await self._send_websocket(connection, request)
            
            # Wait for response with timeout
            response = await asyncio.wait_for(future, timeout=30.0)
            return response
            
        except asyncio.TimeoutError:
            connection.pending_requests.pop(request_id, None)
            raise TimeoutError(f"Request {request_id} timed out")
        except Exception:
            connection.pending_requests.pop(request_id, None)
            raise
    
    async def _send_notification(self, connection: MCPConnection, notification: Dict) -> None:
        """Send JSON-RPC notification (no response expected)"""
        if connection.server.transport_type == MCPTransportType.STDIO:
            await self._send_stdio(connection, notification)
        elif connection.server.transport_type == MCPTransportType.HTTP:
            # HTTP doesn't support notifications in standard JSON-RPC
            pass
        elif connection.server.transport_type == MCPTransportType.WEBSOCKET:
            await self._send_websocket(connection, notification)
    
    async def _send_stdio(self, connection: MCPConnection, message: Dict) -> None:
        """Send message via stdio"""
        if not connection.stdin:
            raise ValueError("stdin not available")
        
        data = json.dumps(message) + "\n"
        connection.stdin.write(data.encode())
        await connection.stdin.drain()
    
    async def _send_http(self, connection: MCPConnection, request: Dict) -> Dict:
        """Send message via HTTP and return response"""
        if not connection.client:
            raise ValueError("HTTP client not available")
        
        response = await connection.client.post("/", json=request)
        response.raise_for_status()
        return response.json()
    
    async def _send_websocket(self, connection: MCPConnection, message: Dict) -> None:
        """Send message via WebSocket"""
        if not connection.client:
            raise ValueError("WebSocket client not available")
        
        await connection.client.send(json.dumps(message))
    
    async def _read_stdout(self, connection: MCPConnection) -> None:
        """Read stdout for JSON-RPC responses"""
        if not connection.stdout:
            return
        
        try:
            while True:
                line = await connection.stdout.readline()
                if not line:
                    break
                
                try:
                    message = json.loads(line.decode().strip())
                    await self._handle_message(connection, message)
                except json.JSONDecodeError:
                    log.warning(f"Invalid JSON from stdout: {line}")
                except Exception as e:
                    log.error(f"Error handling message: {e}")
                    
        except Exception as e:
            log.error(f"Error reading stdout: {e}")
    
    async def _read_stderr(self, connection: MCPConnection) -> None:
        """Read stderr for error messages"""
        if not connection.stderr:
            return
        
        try:
            while True:
                line = await connection.stderr.readline()
                if not line:
                    break
                
                error_msg = line.decode().strip()
                if error_msg:
                    log.warning(f"MCP stderr: {error_msg}")
                    
        except Exception as e:
            log.error(f"Error reading stderr: {e}")
    
    async def _read_websocket(self, connection: MCPConnection) -> None:
        """Read WebSocket messages"""
        if not connection.client:
            return
        
        try:
            async for message in connection.client:
                try:
                    data = json.loads(message)
                    await self._handle_message(connection, data)
                except json.JSONDecodeError:
                    log.warning(f"Invalid JSON from WebSocket: {message}")
                except Exception as e:
                    log.error(f"Error handling WebSocket message: {e}")
                    
        except Exception as e:
            log.error(f"Error reading WebSocket: {e}")
    
    async def _handle_message(self, connection: MCPConnection, message: Dict) -> None:
        """Handle incoming JSON-RPC message"""
        # Check if it's a response to a pending request
        if "id" in message and message["id"] in connection.pending_requests:
            future = connection.pending_requests.pop(message["id"])
            if not future.done():
                future.set_result(message)
        
        # Handle notifications
        elif "method" in message and "id" not in message:
            # Process notification
            log.debug(f"Received notification: {message['method']}")
    
    async def get_available_tools(self, server_id: str) -> List[Dict[str, Any]]:
        """Get available tools from an MCP server"""
        connection = self.connections.get(server_id)
        if not connection:
            raise ValueError(f"No connection to server {server_id}")
        
        # For MCP protocol servers, use the MCPProtocolHandler
        if connection.use_protocol_handler:
            try:
                headers = connection.server.headers if hasattr(connection.server, 'headers') else None
                tools = await mcp_protocol_handler.list_tools(
                    connection.server.url, 
                    "http",  # We know it's HTTP if using protocol handler
                    headers
                )
                return tools
            except Exception as e:
                log.error(f"Failed to get tools from MCP protocol server: {e}")
                raise
        
        # For Smithery servers, use the Smithery client (legacy - being replaced by protocol handler)
        if connection.is_smithery and connection.smithery_client:
            try:
                return await connection.smithery_client.list_tools()
            except Exception as e:
                log.error(f"Failed to get tools from Smithery server: {e}")
                raise
        
        # For other MCP protocol servers, use the custom discovery service
        if connection.is_mcp_protocol:
            try:
                from open_webui.services.mcp_custom import discover_custom_tools
                
                # Use the custom MCP discovery for MCP servers
                result = await discover_custom_tools('http', {'url': connection.server.url})
                return result.get('tools', [])
            except Exception as e:
                log.error(f"Failed to discover tools via MCP protocol: {e}")
                # Fall back to standard JSON-RPC
        
        # Standard JSON-RPC approach
        request = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "id": connection.next_request_id()
        }
        
        response = await self._send_request(connection, request)
        
        if "error" in response:
            raise ValueError(f"Failed to get tools: {response['error']}")
        
        return response.get("result", {}).get("tools", [])
    
    async def call_tool(self, server_id: str, tool_name: str, arguments: Dict) -> Any:
        """Call a tool on an MCP server"""
        connection = self.connections.get(server_id)
        if not connection:
            raise ValueError(f"No connection to server {server_id}")
        
        # For MCP protocol servers, use the MCPProtocolHandler
        if connection.use_protocol_handler:
            try:
                headers = connection.server.headers if hasattr(connection.server, 'headers') else None
                result = await mcp_protocol_handler.execute_tool(
                    connection.server.url,
                    "http",  # We know it's HTTP if using protocol handler
                    tool_name,
                    arguments,
                    headers
                )
                if result.success:
                    return result.content
                else:
                    raise ValueError(f"Tool execution failed: {result.error}")
            except Exception as e:
                log.error(f"Failed to call tool on MCP protocol server: {e}")
                raise
        
        # For Smithery servers, use the Smithery client (legacy - being replaced by protocol handler)
        if connection.is_smithery and connection.smithery_client:
            try:
                return await connection.smithery_client.call_tool(tool_name, arguments)
            except Exception as e:
                log.error(f"Failed to call tool on Smithery server: {e}")
                raise
        
        # Standard JSON-RPC approach
        request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            },
            "id": connection.next_request_id()
        }
        
        response = await self._send_request(connection, request)
        
        if "error" in response:
            raise ValueError(f"Tool call failed: {response['error']}")
        
        return response.get("result", {})
    
    async def disconnect(self, server_id: str) -> None:
        """Disconnect from an MCP server"""
        async with self._lock:
            if server_id in self.connections:
                connection = self.connections[server_id]
                await self._cleanup_connection(connection)
                del self.connections[server_id]
                log.info(f"Disconnected from MCP server: {connection.server.name}")
    
    async def _cleanup_connection(self, connection: MCPConnection) -> None:
        """Clean up connection resources"""
        try:
            # Cancel pending requests
            for future in connection.pending_requests.values():
                if not future.done():
                    future.cancel()
            
            # Close Smithery client if present
            if connection.smithery_client:
                try:
                    await connection.smithery_client.disconnect()
                except Exception as e:
                    log.error(f"Error disconnecting Smithery client: {e}")
            
            # Close stdio process
            if connection.process:
                try:
                    connection.process.terminate()
                    await asyncio.wait_for(connection.process.wait(), timeout=5.0)
                except asyncio.TimeoutError:
                    connection.process.kill()
                    await connection.process.wait()
                except Exception as e:
                    log.error(f"Error terminating process: {e}")
            
            # Close HTTP client
            if isinstance(connection.client, httpx.AsyncClient):
                await connection.client.aclose()
            
            # Close WebSocket
            elif isinstance(connection.client, WebSocketClientProtocol):
                await connection.client.close()
                
        except Exception as e:
            log.error(f"Error cleaning up connection: {e}")
    
    async def _is_connection_alive(self, connection: MCPConnection) -> bool:
        """Check if connection is still alive"""
        try:
            # Check Smithery connections
            if connection.is_smithery:
                return connection.smithery_client is not None and connection.smithery_client.session is not None
            
            if connection.server.transport_type == MCPTransportType.STDIO:
                return connection.process and connection.process.returncode is None
            elif connection.server.transport_type == MCPTransportType.HTTP:
                # HTTP connections are stateless
                return connection.client is not None
            elif connection.server.transport_type == MCPTransportType.WEBSOCKET:
                return connection.client and not connection.client.closed
        except Exception:
            return False
        
        return False
    
    async def disconnect_all(self) -> None:
        """Disconnect from all MCP servers"""
        server_ids = list(self.connections.keys())
        for server_id in server_ids:
            await self.disconnect(server_id)


# Global MCP manager instance
mcp_manager = MCPManager()


async def test_mcp_connection(server: MCPServerModel) -> MCPConnectionStatus:
    """Test connection to an MCP server"""
    try:
        # Try to connect
        connection = await mcp_manager.connect(server)
        
        # Get available tools
        tools = await mcp_manager.get_available_tools(server.id)
        
        return MCPConnectionStatus(
            status="success",
            message="Connection successful",
            tools=tools
        )
        
    except Exception as e:
        log.error(f"Connection test failed: {str(e)}")
        return MCPConnectionStatus(
            status="error",
            message=str(e),
            tools=[]
        )