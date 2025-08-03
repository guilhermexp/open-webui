#!/usr/bin/env python3
"""
Test script to diagnose Twitter/X MCP server issues
"""
import asyncio
import sys
import os
import json
from pathlib import Path

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Django settings before importing models
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "open_webui.config")

import django
django.setup()

from open_webui.models.mcp import MCPServers, MCPTools, MCPServerModel, MCPServerForm
from open_webui.utils.mcp import mcp_manager, test_mcp_connection
from open_webui.internal.db import get_db
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

async def test_twitter_server():
    """Test Twitter/X MCP server functionality"""
    print("=== Twitter/X MCP Server Diagnostic Test ===\n")
    
    # Check if there are any MCP servers in the database
    with get_db() as db:
        from open_webui.models.mcp import MCPServer
        servers = db.query(MCPServer).all()
        print(f"Total MCP servers in database: {len(servers)}\n")
        
        # Look for Twitter/X server
        twitter_server = None
        for server in servers:
            print(f"Server: {server.name}")
            print(f"  ID: {server.id}")
            print(f"  URL: {server.url}")
            print(f"  Transport: {server.transport_type}")
            print(f"  Enabled: {server.enabled}")
            
            if 'twitter' in server.name.lower() or 'x.com' in str(server.url).lower():
                twitter_server = server
                print("  ^^^ This appears to be the Twitter/X server")
            print()
    
    if not twitter_server:
        print("No Twitter/X MCP server found in database.")
        print("\nCreating a test Twitter/X MCP server...")
        
        # Create a test server
        # Note: These are hypothetical values - adjust based on actual Twitter/X MCP server specs
        test_server_data = MCPServerForm(
            name="Twitter/X",
            transport_type="http",
            url="https://mcp.x.com/api",  # Hypothetical URL
            enabled=True,
            meta={"provider": "x.com"}
        )
        
        # Use a test user ID (would need actual user ID in production)
        test_user_id = "test-user-123"
        
        try:
            twitter_server = MCPServers.create_server(test_user_id, test_server_data)
            print(f"Created test server with ID: {twitter_server.id}")
        except Exception as e:
            print(f"Failed to create test server: {e}")
            return
    
    # Test connection
    print("\n=== Testing MCP Connection ===")
    try:
        # Convert to MCPServerModel if needed
        if not isinstance(twitter_server, MCPServerModel):
            twitter_server = MCPServerModel.model_validate(twitter_server)
            
        result = await test_mcp_connection(twitter_server)
        print(f"Connection Status: {result.status}")
        print(f"Message: {result.message}")
        print(f"Tools Found: {len(result.tools)}")
        
        if result.tools:
            print("\nAvailable Tools:")
            for tool in result.tools:
                print(f"  - {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')}")
    except Exception as e:
        print(f"Connection test failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Check MCP protocol handler
    print("\n=== Checking MCP Protocol Handler ===")
    try:
        from open_webui.utils.mcp_protocol_handler import mcp_protocol_handler
        print("MCP Protocol Handler imported successfully")
        
        # Check if it's configured for Twitter/X
        if hasattr(mcp_protocol_handler, 'servers'):
            print(f"Registered servers: {list(mcp_protocol_handler.servers.keys())}")
    except Exception as e:
        print(f"Failed to check MCP protocol handler: {e}")
    
    # Check for tools in database
    print("\n=== Checking Tools in Database ===")
    if twitter_server:
        tools = MCPTools.get_tools_by_server_id(twitter_server.id)
        print(f"Tools in database for Twitter/X server: {len(tools)}")
        for tool in tools:
            print(f"  - {tool.tool_name}: {tool.description[:50] if tool.description else 'No description'}")

if __name__ == "__main__":
    asyncio.run(test_twitter_server())