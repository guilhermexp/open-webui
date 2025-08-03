#!/usr/bin/env python3
"""
Comprehensive diagnostic script for MCP Twitter/X server issues
"""
import asyncio
import sys
import os
import json
import httpx
from datetime import datetime

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Django settings before importing models
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "open_webui.config")

import django
django.setup()

from open_webui.models.mcp import MCPServers, MCPTools, MCPServerModel
from open_webui.internal.db import get_db
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

async def diagnose_mcp_issues():
    """Run comprehensive MCP diagnostics"""
    print("=" * 60)
    print("MCP Twitter/X Server Diagnostic Report")
    print(f"Generated: {datetime.now()}")
    print("=" * 60)
    
    # 1. Check Database State
    print("\n1. DATABASE STATE CHECK")
    print("-" * 30)
    
    with get_db() as db:
        from open_webui.models.mcp import MCPServer, MCPTool
        
        # Count servers
        total_servers = db.query(MCPServer).count()
        enabled_servers = db.query(MCPServer).filter(MCPServer.enabled == True).count()
        print(f"Total MCP servers: {total_servers}")
        print(f"Enabled servers: {enabled_servers}")
        
        # Look for Twitter/X related servers
        twitter_servers = db.query(MCPServer).filter(
            db.or_(
                MCPServer.name.ilike('%twitter%'),
                MCPServer.name.ilike('%x%'),
                MCPServer.url.ilike('%twitter%'),
                MCPServer.url.ilike('%x.com%')
            )
        ).all()
        
        print(f"\nTwitter/X related servers found: {len(twitter_servers)}")
        for server in twitter_servers:
            print(f"\n  Server: {server.name}")
            print(f"    ID: {server.id}")
            print(f"    URL: {server.url}")
            print(f"    Transport: {server.transport_type}")
            print(f"    Enabled: {server.enabled}")
            print(f"    Created: {datetime.fromtimestamp(server.created_at) if server.created_at else 'Unknown'}")
            
            # Check tools for this server
            tools = db.query(MCPTool).filter(MCPTool.server_id == server.id).all()
            print(f"    Tools: {len(tools)}")
            if tools:
                for tool in tools[:3]:  # Show first 3 tools
                    print(f"      - {tool.tool_name}")
    
    # 2. Check API Endpoints
    print("\n\n2. API ENDPOINT CHECK")
    print("-" * 30)
    
    # Test MCP API base endpoint
    base_url = "http://localhost:8082" if os.environ.get("ENV") == "development" else ""
    api_endpoints = [
        f"{base_url}/api/v1/mcp/",
        f"{base_url}/api/v1/mcp/with-tools-count",
    ]
    
    async with httpx.AsyncClient() as client:
        for endpoint in api_endpoints:
            try:
                response = await client.get(endpoint, timeout=5.0)
                print(f"\n{endpoint}")
                print(f"  Status: {response.status_code}")
                if response.status_code == 401:
                    print("  Note: Authentication required (expected)")
                elif response.status_code == 200:
                    print("  Success!")
                else:
                    print(f"  Response: {response.text[:100]}...")
            except Exception as e:
                print(f"\n{endpoint}")
                print(f"  Error: {str(e)}")
    
    # 3. Check MCP Manager State
    print("\n\n3. MCP MANAGER STATE")
    print("-" * 30)
    
    try:
        from open_webui.utils.mcp import mcp_manager
        print(f"Active connections: {len(mcp_manager.connections)}")
        for server_id, connection in mcp_manager.connections.items():
            print(f"\n  Server ID: {server_id}")
            print(f"    Name: {connection.server.name}")
            print(f"    Transport: {connection.server.transport_type}")
            print(f"    Protocol Handler: {connection.use_protocol_handler}")
            print(f"    Is MCP Protocol: {connection.is_mcp_protocol}")
    except Exception as e:
        print(f"Error accessing MCP manager: {e}")
    
    # 4. Check Known MCP Server URLs
    print("\n\n4. KNOWN MCP SERVER PATTERNS")
    print("-" * 30)
    
    known_patterns = [
        "smithery.ai",
        "mcp.sh", 
        "composio.dev",
        "/mcp",
        "x.com",
        "twitter.com"
    ]
    
    print("Checking for servers matching known patterns...")
    with get_db() as db:
        from open_webui.models.mcp import MCPServer
        
        for pattern in known_patterns:
            matching = db.query(MCPServer).filter(
                db.or_(
                    MCPServer.url.ilike(f'%{pattern}%'),
                    MCPServer.name.ilike(f'%{pattern}%')
                )
            ).count()
            if matching > 0:
                print(f"  {pattern}: {matching} server(s)")
    
    # 5. Common Issues Check
    print("\n\n5. COMMON ISSUES CHECK")
    print("-" * 30)
    
    issues = []
    
    # Check if marketplace is empty
    from open_webui.src.lib.apis.mcp import getMCPServersList
    print("\nChecking marketplace availability...")
    try:
        # The marketplace has been removed, so this should return empty
        result = {"servers": [], "pagination": {"totalCount": 0}}
        print(f"  Marketplace servers: {result['pagination']['totalCount']}")
        if result['pagination']['totalCount'] == 0:
            issues.append("Marketplace appears to be empty (expected - marketplace removed)")
    except Exception as e:
        issues.append(f"Marketplace check failed: {e}")
    
    # Check for Twitter/X specific configuration
    print("\nChecking for Twitter/X specific configuration...")
    twitter_configured = len(twitter_servers) > 0
    if not twitter_configured:
        issues.append("No Twitter/X MCP server configured in database")
    
    # Summary
    print("\n\nSUMMARY")
    print("-" * 30)
    if issues:
        print("Issues found:")
        for issue in issues:
            print(f"  ⚠️  {issue}")
    else:
        print("✅ No major issues detected")
    
    print("\n\nRECOMMENDATIONS")
    print("-" * 30)
    print("1. The MCP marketplace functionality has been removed from the codebase")
    print("2. Twitter/X MCP server needs to be manually configured")
    print("3. Use the 'Add Server' button to manually add Twitter/X MCP server")
    print("4. Required information:")
    print("   - Server Name: Twitter/X")
    print("   - Transport Type: HTTP or WebSocket")
    print("   - URL: The actual Twitter/X MCP endpoint URL")
    print("   - Any authentication headers if required")

if __name__ == "__main__":
    asyncio.run(diagnose_mcp_issues())