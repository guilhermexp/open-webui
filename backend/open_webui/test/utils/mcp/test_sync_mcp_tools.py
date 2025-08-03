#!/usr/bin/env python3
import sys
import os
import asyncio

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from open_webui.models.mcp import MCPServer, MCPServerModel, MCPTools
from open_webui.utils.mcp_tool_adapter import MCPToolAdapter
from open_webui.internal.db import get_db

async def main():
    # Get all MCP servers from database
    with get_db() as db:
        servers = db.query(MCPServer).all()
        print(f"Total servers: {len(servers)}\n")

        for server in servers:
            print(f'Server: {server.name} (ID: {server.id})')
            print(f'  URL: {server.url}')
            
            # Convert to MCPServerModel
            server_model = MCPServerModel.model_validate(server)
            
            # Get current tools
            current_tools = MCPTools.get_tools_by_server_id(server.id)
            print(f'  Current tools: {len(current_tools)}')
            
            if server.enabled:
                print(f'  Attempting to sync tools...')
                try:
                    # Sync tools for this server
                    results = await MCPToolAdapter.sync_server_tools(server_model, server.user_id)
                    print(f'  Sync results: {results}')
                    
                    # Get updated tools
                    updated_tools = MCPTools.get_tools_by_server_id(server.id)
                    print(f'  Updated tools: {len(updated_tools)}')
                    
                    # List first few tools
                    for i, tool in enumerate(updated_tools[:5]):
                        print(f'    - {tool.tool_name}: {tool.description[:50]}...' if tool.description else f'    - {tool.tool_name}')
                    if len(updated_tools) > 5:
                        print(f'    ... and {len(updated_tools) - 5} more tools')
                    
                except Exception as e:
                    print(f'  Error syncing tools: {str(e)}')
            else:
                print(f'  Server is disabled, skipping sync')
            
            print()

if __name__ == "__main__":
    asyncio.run(main())