#!/usr/bin/env python3
import sys
import os
import asyncio

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from open_webui.utils.mcp import mcp_manager
from open_webui.models.mcp import MCPServer, MCPServerModel
from open_webui.internal.db import get_db

async def main():
    # Get the Sequential Thinking server to test
    with get_db() as db:
        server = db.query(MCPServer).filter(
            MCPServer.name == "Sequencias Thinking"
        ).first()
        
        if not server:
            print("Sequential Thinking server not found!")
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
        
        # Test the Sequential Thinking tool
        print("\nTesting Sequential Thinking tool...")
        test_args = {
            "thought": "I need to analyze the key steps for implementing a user authentication system. Let me break this down systematically.",
            "next_thought_needed": True,
            "thought_number": 1,
            "total_thoughts": 5
        }
        
        try:
            result = await mcp_manager.call_tool(
                server.id,
                "sequentialthinking_tools",
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