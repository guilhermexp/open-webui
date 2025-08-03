#!/usr/bin/env python3
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from open_webui.models.mcp import MCPServer, MCPTools
from open_webui.internal.db import get_db

# Get all MCP servers from database
with get_db() as db:
    servers = db.query(MCPServer).all()
    print(f"Total servers: {len(servers)}\n")

    for server in servers:
        print(f'Server: {server.name} (ID: {server.id})')
        print(f'  URL: {server.url}')
        print(f'  Transport: {server.transport_type}')
        print(f'  Enabled: {server.enabled}')
        print(f'  User ID: {server.user_id}')
        
        # Get tools for this server
        tools = MCPTools.get_tools_by_server_id(server.id)
        print(f'  Tools: {len(tools)}')
        for tool in tools:
            print(f'    - {tool.tool_name}: {tool.description[:50]}...' if tool.description else f'    - {tool.tool_name}')
        print()