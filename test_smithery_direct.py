#!/usr/bin/env python3
"""
Test direct connection to Smithery MCP server
"""
import asyncio
import os
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

# Set the API key
os.environ["SMITHERY_API_KEY"] = "01fc178f-5b5f-4a90-9c51-f1bf7e9f2f6e"

async def test_smithery():
    # Test URLs - try different formats
    test_urls = [
        "https://server.smithery.ai/exa/mcp",
        "https://server.smithery.ai/sequential/mcp",
        "https://server.smithery.ai/n8n/mcp",
        "https://server.smithery.ai/duckduckgo/mcp",
        "https://server.smithery.ai/github/mcp",
        "https://server.smithery.ai/google-drive/mcp",
        "https://server.smithery.ai/google-maps/mcp",
        "https://server.smithery.ai/filesystem/mcp",
    ]
    
    for url in test_urls:
        print(f"\nTesting URL: {url}")
        try:
            # Add API key to URL
            url_with_key = f"{url}?api_key={os.environ['SMITHERY_API_KEY']}"
            
            async with streamablehttp_client(url_with_key) as (read_stream, write_stream, _):
                async with ClientSession(read_stream, write_stream) as session:
                    await session.initialize()
                    print("✓ Connected successfully!")
                    
                    # List tools
                    tools_result = await session.list_tools()
                    tools = tools_result.tools if hasattr(tools_result, 'tools') else tools_result
                    print(f"✓ Found {len(tools)} tools:")
                    for tool in tools[:3]:  # Show first 3 tools
                        print(f"  - {tool.name}: {tool.description[:50]}...")
                    
        except Exception as e:
            print(f"✗ Failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_smithery())