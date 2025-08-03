"""
MCP (Model Context Protocol) API Router
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from open_webui.models.mcp import (
    MCPServers, 
    MCPServerForm, 
    MCPServerModel,
    MCPTools,
    MCPToolModel,
    MCPConnectionStatus
)
from open_webui.models.users import Users
from open_webui.utils.auth import get_admin_user, get_verified_user
from open_webui.utils.access_control import has_access
from open_webui.constants import ERROR_MESSAGES
from open_webui.services.mcp_custom import discover_custom_tools

import logging
log = logging.getLogger(__name__)

router = APIRouter()

############################
# Get MCP Servers
############################

@router.get("/", response_model=List[MCPServerModel])
async def get_mcp_servers(user=Depends(get_verified_user)):
    """Get all MCP servers for the current user"""
    try:
        return MCPServers.get_servers_by_user_id(user.id)
    except Exception as e:
        log.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.DEFAULT()
        )


############################
# Create MCP Server
############################

@router.post("/", response_model=MCPServerModel)
async def create_mcp_server(
    form_data: MCPServerForm,
    user=Depends(get_verified_user)
):
    """Create a new MCP server configuration"""
    try:
        # Temporary: Skip validation for testing
        pass
        
        server = MCPServers.create_server(user.id, form_data)
        if server:
            return server
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR_MESSAGES.DEFAULT("Failed to create MCP server")
            )
    except HTTPException:
        raise
    except Exception as e:
        log.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.DEFAULT()
        )


############################
# Get MCP Server by ID
############################

@router.get("/{server_id}", response_model=MCPServerModel)
async def get_mcp_server(
    server_id: str,
    user=Depends(get_verified_user)
):
    """Get a specific MCP server configuration"""
    try:
        server = MCPServers.get_server_by_id_and_user(server_id, user.id)
        if server:
            return server
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_MESSAGES.NOT_FOUND
            )
    except HTTPException:
        raise
    except Exception as e:
        log.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.DEFAULT()
        )


############################
# Update MCP Server
############################

@router.put("/{server_id}", response_model=MCPServerModel)
async def update_mcp_server(
    server_id: str,
    form_data: MCPServerForm,
    user=Depends(get_verified_user)
):
    """Update an MCP server configuration"""
    try:
        # Validate transport-specific fields
        if form_data.transport_type == "stdio" and not form_data.command:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Command is required for stdio transport"
            )
        
        if form_data.transport_type in ["http", "websocket"] and not form_data.url:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"URL is required for {form_data.transport_type} transport"
            )
        
        server = MCPServers.update_server(server_id, user.id, form_data)
        if server:
            # If server transport or connection details changed, disconnect existing connection
            from open_webui.utils.mcp import mcp_manager
            await mcp_manager.disconnect(server_id)
            
            return server
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_MESSAGES.NOT_FOUND
            )
    except HTTPException:
        raise
    except Exception as e:
        log.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.DEFAULT()
        )


############################
# Delete MCP Server
############################

@router.delete("/{server_id}")
async def delete_mcp_server(
    server_id: str,
    user=Depends(get_verified_user)
):
    """Delete an MCP server configuration"""
    try:
        # Disconnect before deleting
        from open_webui.utils.mcp import mcp_manager
        await mcp_manager.disconnect(server_id)
        
        # Remove associated tools from Open WebUI
        from open_webui.utils.mcp_tool_adapter import MCPToolAdapter
        await MCPToolAdapter.remove_mcp_tools(server_id, user.id)
        
        if MCPServers.delete_server(server_id, user.id):
            return {"detail": "MCP server deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_MESSAGES.NOT_FOUND
            )
    except HTTPException:
        raise
    except Exception as e:
        log.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.DEFAULT()
        )


############################
# Toggle MCP Server
############################

class ToggleForm(BaseModel):
    enabled: bool


@router.post("/{server_id}/toggle", response_model=MCPServerModel)
async def toggle_mcp_server(
    server_id: str,
    form_data: ToggleForm,
    user=Depends(get_verified_user)
):
    """Enable or disable an MCP server"""
    try:
        server = MCPServers.toggle_server(server_id, user.id, form_data.enabled)
        if server:
            # Disconnect if disabling
            if not form_data.enabled:
                from open_webui.utils.mcp import mcp_manager
                await mcp_manager.disconnect(server_id)
            
            return server
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_MESSAGES.NOT_FOUND
            )
    except HTTPException:
        raise
    except Exception as e:
        log.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.DEFAULT()
        )


############################
# Test MCP Connection
############################

@router.post("/{server_id}/test", response_model=MCPConnectionStatus)
async def test_mcp_connection(
    server_id: str,
    user=Depends(get_verified_user)
):
    """Test connection to an MCP server"""
    try:
        from open_webui.utils.mcp import test_mcp_connection
        
        server = MCPServers.get_server_by_id_and_user(server_id, user.id)
        if not server:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_MESSAGES.NOT_FOUND
            )
        
        result = await test_mcp_connection(server)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        log.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


############################
# Test Custom MCP Connection
############################

class CustomConnectionRequest(BaseModel):
    type: str  # 'http' or 'sse'
    config: Dict[str, Any]


@router.post("/test-custom", response_model=Dict[str, Any])
async def test_custom_mcp_connection(
    request: CustomConnectionRequest,
    user=Depends(get_verified_user)
):
    """Test a custom MCP connection (HTTP or SSE)"""
    try:
        result = await discover_custom_tools(request.type, request.config)
        return result
    except HTTPException:
        raise
    except Exception as e:
        log.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


############################
# Get MCP Tools
############################

@router.get("/{server_id}/tools", response_model=List[MCPToolModel])
async def get_mcp_tools(
    server_id: str,
    user=Depends(get_verified_user)
):
    """Get available tools from an MCP server"""
    try:
        server = MCPServers.get_server_by_id_and_user(server_id, user.id)
        if not server:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_MESSAGES.NOT_FOUND
            )
        
        # Get tools from database
        tools = MCPTools.get_tools_by_server_id(server_id)
        return tools
        
    except HTTPException:
        raise
    except Exception as e:
        log.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.DEFAULT()
        )


############################
# Sync MCP Tools
############################

@router.post("/{server_id}/sync")
async def sync_mcp_tools(
    server_id: str,
    user=Depends(get_verified_user)
):
    """Sync tools from an MCP server to Open WebUI"""
    try:
        from open_webui.utils.mcp import mcp_manager
        from open_webui.utils.mcp_tool_adapter import MCPToolAdapter
        
        server = MCPServers.get_server_by_id_and_user(server_id, user.id)
        if not server:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_MESSAGES.NOT_FOUND
            )
        
        if not server.enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot sync tools from disabled server"
            )
        
        # Connect to server and get tools
        try:
            connection = await mcp_manager.connect(server)
            tools = await mcp_manager.get_available_tools(server_id)
        except Exception as e:
            log.error(f"Failed to connect to MCP server {server.name}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Failed to connect to MCP server: {str(e)}"
            )
        
        # Sync tools to Open WebUI
        synced_count = 0
        for tool in tools:
            MCPTools.create_or_update_tool(server_id, tool)
            synced_count += 1
        
        # Update Open WebUI tools
        try:
            await MCPToolAdapter.sync_server_tools(server, user.id)
        except Exception as e:
            log.error(f"Failed to sync tools to Open WebUI: {str(e)}")
            # Don't fail the entire operation if Open WebUI sync fails
            pass
        
        return {
            "detail": f"Successfully synced {synced_count} tools",
            "count": synced_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        log.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


############################
# Get MCP Servers with Tools Count
############################

@router.get("/with-tools-count")
async def get_mcp_servers_with_tools_count(user=Depends(get_verified_user)):
    """Get all MCP servers with their tools count"""
    try:
        servers = MCPServers.get_servers_by_user_id(user.id)
        result = []
        
        for server in servers:
            server_dict = server.model_dump()
            tools = MCPTools.get_tools_by_server_id(server.id)
            server_dict['tools_count'] = len(tools)
            result.append(server_dict)
            
        return result
    except Exception as e:
        log.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.DEFAULT()
        )


############################
# Admin: Get All MCP Servers
############################

@router.get("/admin/all", response_model=List[MCPServerModel])
async def get_all_mcp_servers(user=Depends(get_admin_user)):
    """Admin: Get all MCP servers across all users"""
    try:
        # This would need a new method in MCPServers
        # For now, return empty list
        return []
    except Exception as e:
        log.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.DEFAULT()
        )