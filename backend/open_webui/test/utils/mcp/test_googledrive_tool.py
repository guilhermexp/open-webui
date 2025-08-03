#!/usr/bin/env python3
import sys
import os
import asyncio

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from open_webui.utils.mcp import mcp_manager
from open_webui.models.mcp import MCPServer, MCPServerModel, MCPTools
from open_webui.internal.db import get_db

async def main():
    # Get the Google Drive server to test
    with get_db() as db:
        server = db.query(MCPServer).filter(
            MCPServer.name == "Google Drive"
        ).first()
        
        if not server:
            print("Google Drive server not found!")
            return
        
        print(f"Testing MCP tool execution for: {server.name}")
        print(f"Server ID: {server.id}")
        print(f"URL: {server.url}")
        
        # Convert to MCPServerModel
        server_model = MCPServerModel.model_validate(server)
        
        # Connect to the server
        print("\nConnecting to server...")
        connection = await mcp_manager.connect(server_model)
        print("Connected successfully!")
        
        # List available tools
        tools = MCPTools.get_tools_by_server_id(server.id)
        print(f"\nAvailable tools: {len(tools)}")
        
        # Find the generate IDs tool (simple tool that doesn't require authentication)
        generate_ids_tool = None
        for tool in tools:
            if tool.tool_name == "GOOGLEDRIVE_GENERATE_IDS":
                generate_ids_tool = tool
                break
        
        if not generate_ids_tool:
            print("GOOGLEDRIVE_GENERATE_IDS tool not found!")
            return
        
        print(f"\nTesting tool: {generate_ids_tool.tool_name}")
        print(f"Description: {generate_ids_tool.description[:100]}...")
        
        # Test the tool
        test_args = {
            "count": 3,
            "space": "drive"
        }
        
        try:
            result = await mcp_manager.call_tool(
                server.id,
                generate_ids_tool.tool_name,
                test_args
            )
            
            print("\nTool execution result:")
            print(f"Type: {type(result)}")
            print(f"Content: {result}")
            
        except Exception as e:
            print(f"\nError executing tool: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())