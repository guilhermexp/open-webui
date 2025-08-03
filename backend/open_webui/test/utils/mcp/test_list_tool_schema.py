#!/usr/bin/env python3
import sys
import os
import asyncio

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from open_webui.models.mcp import MCPTools
from open_webui.internal.db import get_db

async def main():
    # Get the Sequential Thinking tool details
    tools = MCPTools.get_tools_by_server_id("f7dc028c-7ac6-4b29-ba22-82846ddccb7e")
    
    for tool in tools:
        print(f"Tool: {tool.tool_name}")
        print(f"Description: {tool.description[:200] if tool.description else 'No description'}...")
        
        # Show the tool parameters
        print(f"Tool Parameters/Input Schema:")
        if tool.parameters:
            import json
            print(json.dumps(tool.parameters, indent=2))
        else:
            print("  No parameters defined")
        print()

if __name__ == "__main__":
    asyncio.run(main())