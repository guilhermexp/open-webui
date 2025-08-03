#!/usr/bin/env python3
"""
Test script to verify MCP HTTP client functionality
"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from open_webui.models.mcp import MCPServerModel, MCPTransportType
from open_webui.utils.mcp import mcp_manager, test_mcp_connection
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

async def test_http_mcp_server():
    """Test HTTP MCP server connection and operations"""
    print("\n=== Testing MCP HTTP Client Implementation ===\n")
    
    # Test server configuration
    import time
    current_time = int(time.time())
    
    test_server = MCPServerModel(
        id="test-http-server",
        user_id="test-user",
        name="Test HTTP Server",
        transport_type=MCPTransportType.HTTP,
        url="https://api.smithery.ai/mcp",  # Using Smithery as test endpoint
        enabled=True,
        created_at=current_time,
        updated_at=current_time
    )
    
    print(f"1. Testing connection to: {test_server.url}")
    print(f"   Transport type: {test_server.transport_type}")
    
    try:
        # Test connection
        print("\n2. Testing connection...")
        result = await test_mcp_connection(test_server)
        print(f"   Status: {result.status}")
        print(f"   Message: {result.message}")
        print(f"   Tools found: {len(result.tools)}")
        
        if result.status == "success":
            # List available tools
            print("\n3. Available tools:")
            for i, tool in enumerate(result.tools[:5]):  # Show first 5 tools
                print(f"   {i+1}. {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')[:60]}...")
            
            if len(result.tools) > 5:
                print(f"   ... and {len(result.tools) - 5} more tools")
            
            # Test tool call if connected
            if result.tools:
                print("\n4. Testing tool call...")
                try:
                    # Call a simple tool (e.g., list tools)
                    tool_name = result.tools[0].get('name')
                    print(f"   Calling tool: {tool_name}")
                    
                    # Note: Actual tool call would require proper arguments
                    # This is just to verify the HTTP request mechanism
                    
                except Exception as e:
                    print(f"   Tool call error: {str(e)}")
        
        # Test HTTP-specific error handling
        print("\n5. Testing error handling...")
        
        # Test with invalid URL
        invalid_server = MCPServerModel(
            id="test-invalid",
            user_id="test-user",
            name="Invalid Server",
            transport_type=MCPTransportType.HTTP,
            url="http://invalid.example.com/mcp",
            enabled=True,
            created_at=current_time,
            updated_at=current_time
        )
        
        print("   Testing with invalid URL...")
        invalid_result = await test_mcp_connection(invalid_server)
        print(f"   Status: {invalid_result.status}")
        print(f"   Error: {invalid_result.message}")
        
    except Exception as e:
        print(f"\nError during testing: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        print("\n6. Cleaning up connections...")
        await mcp_manager.disconnect_all()
        print("   All connections closed")
    
    print("\n=== Test Complete ===\n")

async def analyze_http_flow():
    """Analyze the HTTP request/response flow"""
    print("\n=== HTTP Flow Analysis ===\n")
    
    print("1. HTTP Client Configuration:")
    print("   - Base URL: Set from server.url")
    print("   - Headers: Content-Type: application/json")
    print("   - Timeout: 30 seconds")
    print("   - Client: httpx.AsyncClient")
    
    print("\n2. Request Flow:")
    print("   a) Initialize connection (HTTP client creation)")
    print("   b) Send initialize request (JSON-RPC)")
    print("   c) Receive initialize response")
    print("   d) Send initialized notification")
    print("   e) Ready for tool operations")
    
    print("\n3. JSON-RPC Structure:")
    print("   - All requests POST to base URL")
    print("   - Request format: {jsonrpc: '2.0', method: 'method_name', params: {...}, id: request_id}")
    print("   - Response format: {jsonrpc: '2.0', result: {...}, id: request_id}")
    
    print("\n4. Error Handling:")
    print("   - HTTP errors: Caught by httpx and raised")
    print("   - JSON-RPC errors: Returned in response.error field")
    print("   - Timeout errors: 30-second timeout on all requests")
    print("   - Connection errors: Raised as exceptions")

if __name__ == "__main__":
    print("Starting MCP HTTP Client Test...")
    asyncio.run(test_http_mcp_server())
    asyncio.run(analyze_http_flow())