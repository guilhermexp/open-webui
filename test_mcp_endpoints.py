#!/usr/bin/env python3
"""
Test MCP API endpoints
"""
import httpx
import asyncio
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8082"
API_KEY = None  # Set this if you have an API key

# Headers
headers = {
    "Content-Type": "application/json",
}

if API_KEY:
    headers["Authorization"] = f"Bearer {API_KEY}"

async def test_endpoints():
    """Test all MCP endpoints"""
    async with httpx.AsyncClient() as client:
        print("=" * 50)
        print("Testing MCP API Endpoints")
        print("=" * 50)
        
        # Test 1: GET /api/v1/mcp/ - List MCP servers
        print("\n1. Testing GET /api/v1/mcp/")
        try:
            response = await client.get(f"{BASE_URL}/api/v1/mcp/", headers=headers)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                servers = response.json()
                print(f"   Found {len(servers)} MCP servers")
                for server in servers:
                    print(f"   - {server.get('name')} ({server.get('transport_type')})")
            else:
                print(f"   Error: {response.json()}")
        except Exception as e:
            print(f"   Failed: {str(e)}")
        
        # Test 2: POST /api/v1/mcp/ - Create a test MCP server
        print("\n2. Testing POST /api/v1/mcp/")
        test_server = {
            "name": "Test MCP Server",
            "transport_type": "http",
            "url": "https://server.smithery.ai/exa/mcp",
            "config": {
                "apiKey": "test-key"
            },
            "enabled": True
        }
        try:
            response = await client.post(
                f"{BASE_URL}/api/v1/mcp/", 
                headers=headers,
                json=test_server
            )
            print(f"   Status: {response.status_code}")
            if response.status_code in [200, 201]:
                created_server = response.json()
                server_id = created_server.get("id")
                print(f"   Created server with ID: {server_id}")
                
                # Test subsequent endpoints with this server
                if server_id:
                    # Test 3: GET /api/v1/mcp/{id} - Get specific server
                    print(f"\n3. Testing GET /api/v1/mcp/{server_id}")
                    try:
                        response = await client.get(
                            f"{BASE_URL}/api/v1/mcp/{server_id}",
                            headers=headers
                        )
                        print(f"   Status: {response.status_code}")
                        if response.status_code == 200:
                            server = response.json()
                            print(f"   Server: {server.get('name')}")
                        else:
                            print(f"   Error: {response.json()}")
                    except Exception as e:
                        print(f"   Failed: {str(e)}")
                    
                    # Test 4: POST /api/v1/mcp/{id}/test - Test connection
                    print(f"\n4. Testing POST /api/v1/mcp/{server_id}/test")
                    try:
                        response = await client.post(
                            f"{BASE_URL}/api/v1/mcp/{server_id}/test",
                            headers=headers
                        )
                        print(f"   Status: {response.status_code}")
                        if response.status_code == 200:
                            result = response.json()
                            print(f"   Connection status: {result.get('status')}")
                            print(f"   Message: {result.get('message')}")
                            if result.get('tools'):
                                print(f"   Found {len(result['tools'])} tools")
                        else:
                            print(f"   Error: {response.json()}")
                    except Exception as e:
                        print(f"   Failed: {str(e)}")
                    
                    # Test 5: GET /api/v1/mcp/{id}/tools - Get tools
                    print(f"\n5. Testing GET /api/v1/mcp/{server_id}/tools")
                    try:
                        response = await client.get(
                            f"{BASE_URL}/api/v1/mcp/{server_id}/tools",
                            headers=headers
                        )
                        print(f"   Status: {response.status_code}")
                        if response.status_code == 200:
                            tools = response.json()
                            print(f"   Found {len(tools)} tools")
                            for tool in tools[:3]:  # Show first 3 tools
                                print(f"   - {tool.get('name')}: {tool.get('description', '')[:50]}...")
                        else:
                            print(f"   Error: {response.json()}")
                    except Exception as e:
                        print(f"   Failed: {str(e)}")
                    
                    # Test 6: POST /api/v1/mcp/{id}/sync - Sync tools
                    print(f"\n6. Testing POST /api/v1/mcp/{server_id}/sync")
                    try:
                        response = await client.post(
                            f"{BASE_URL}/api/v1/mcp/{server_id}/sync",
                            headers=headers
                        )
                        print(f"   Status: {response.status_code}")
                        if response.status_code == 200:
                            result = response.json()
                            print(f"   Result: {result}")
                        else:
                            print(f"   Error: {response.json()}")
                    except Exception as e:
                        print(f"   Failed: {str(e)}")
                    
                    # Test 7: DELETE /api/v1/mcp/{id} - Clean up
                    print(f"\n7. Testing DELETE /api/v1/mcp/{server_id}")
                    try:
                        response = await client.delete(
                            f"{BASE_URL}/api/v1/mcp/{server_id}",
                            headers=headers
                        )
                        print(f"   Status: {response.status_code}")
                        if response.status_code == 200:
                            print("   Server deleted successfully")
                        else:
                            print(f"   Error: {response.json()}")
                    except Exception as e:
                        print(f"   Failed: {str(e)}")
            else:
                print(f"   Error: {response.json()}")
        except Exception as e:
            print(f"   Failed: {str(e)}")
        
        print("\n" + "=" * 50)
        print("Testing completed")
        print("=" * 50)

if __name__ == "__main__":
    print("Note: Make sure you're authenticated with Open WebUI")
    print("You may need to set the API_KEY variable in this script")
    print()
    asyncio.run(test_endpoints())