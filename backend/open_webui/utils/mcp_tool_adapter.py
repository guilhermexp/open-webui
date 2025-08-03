"""
MCP Tool Adapter
Bridges MCP tools to Open WebUI's tool system
"""
from typing import Dict, List, Any, Optional
from open_webui.models.tools import Tools, ToolForm, ToolMeta
from open_webui.models.mcp import MCPServers, MCPTools, MCPServerModel
from open_webui.utils.mcp import mcp_manager
import json
import uuid
import time
import logging

log = logging.getLogger(__name__)


class MCPToolAdapter:
    """Adapts MCP tools to Open WebUI's tool system"""
    
    @staticmethod
    async def sync_mcp_tools(user_id: str) -> Dict[str, int]:
        """Sync all MCP tools for a user"""
        results = {
            "synced": 0,
            "failed": 0,
            "total": 0
        }
        
        servers = MCPServers.get_servers_by_user_id(user_id)
        
        for server in servers:
            if not server.enabled:
                continue
            
            try:
                server_results = await MCPToolAdapter.sync_server_tools(server, user_id)
                results["synced"] += server_results["synced"]
                results["failed"] += server_results["failed"]
                results["total"] += server_results["total"]
            except Exception as e:
                log.error(f"Failed to sync tools from server {server.name}: {str(e)}")
                results["failed"] += 1
        
        return results
    
    @staticmethod
    async def sync_server_tools(server: MCPServerModel, user_id: str) -> Dict[str, int]:
        """Sync tools from a specific MCP server"""
        results = {
            "synced": 0,
            "failed": 0,
            "total": 0
        }
        
        try:
            # Connect to MCP server
            await mcp_manager.connect(server)
            
            # Get available tools
            mcp_tools = await mcp_manager.get_available_tools(server.id)
            results["total"] = len(mcp_tools)
            
            # Sync each tool
            for mcp_tool in mcp_tools:
                try:
                    # Store in MCP tools table
                    MCPTools.create_or_update_tool(server.id, mcp_tool)
                    
                    # Create/update Open WebUI tool
                    tool_id = f"mcp_{server.id}_{mcp_tool['name']}"
                    
                    # Generate tool wrapper code
                    content = MCPToolAdapter._generate_tool_content(
                        server.id,
                        mcp_tool
                    )
                    
                    # Create tool spec
                    spec = {
                        "name": mcp_tool['name'],
                        "description": mcp_tool.get('description', ''),
                        "parameters": mcp_tool.get('inputSchema', {})
                    }
                    
                    # Create tool meta
                    meta = ToolMeta(
                        profile_image_url=f"/mcp-icon.png",  # Default MCP icon
                        name=f"MCP: {server.name}",
                        description=f"MCP Server: {server.name}",
                        manifest={
                            "type": "mcp",
                            "server_id": server.id,
                            "server_name": server.name,
                            "tool_name": mcp_tool['name']
                        }
                    )
                    
                    # Check if tool exists
                    existing_tool = Tools.get_tool_by_id(tool_id)
                    
                    if existing_tool:
                        # Update existing tool
                        updated = Tools.update_tool_by_id(
                            tool_id,
                            ToolForm(
                                id=tool_id,
                                name=f"{server.name}: {mcp_tool['name']}",
                                content=content,
                                specs=[spec],
                                meta=meta.model_dump()
                            )
                        )
                        if updated:
                            results["synced"] += 1
                        else:
                            results["failed"] += 1
                    else:
                        # Create new tool
                        created = Tools.insert_new_tool(
                            user_id,
                            ToolForm(
                                id=tool_id,
                                name=f"{server.name}: {mcp_tool['name']}",
                                content=content,
                                meta=meta.model_dump()
                            ),
                            specs=[spec]
                        )
                        if created:
                            results["synced"] += 1
                        else:
                            results["failed"] += 1
                            
                except Exception as e:
                    log.error(f"Failed to sync tool {mcp_tool['name']}: {str(e)}")
                    results["failed"] += 1
                    
        except Exception as e:
            log.error(f"Failed to connect to server {server.name}: {str(e)}")
            results["failed"] = results["total"] if results["total"] > 0 else 1
        
        return results
    
    @staticmethod
    def _generate_tool_content(server_id: str, mcp_tool: Dict) -> str:
        """Generate Python code for MCP tool wrapper"""
        
        # Extract parameter names from schema
        params = []
        if 'inputSchema' in mcp_tool and 'properties' in mcp_tool['inputSchema']:
            params = list(mcp_tool['inputSchema']['properties'].keys())
        
        # Create parameter string for function signature
        param_str = ", ".join(params) if params else ""
        if param_str:
            param_str = f", {param_str}"
        
        # Generate the tool wrapper code
        content = f'''"""
MCP Tool Wrapper: {mcp_tool['name']}
Server ID: {server_id}
Auto-generated by MCP Tool Adapter
"""
import json
import asyncio
from typing import Dict, Any, Optional

class Tools:
    def __init__(self):
        self.citation = True
    
    async def {mcp_tool['name']}(self{param_str}) -> Dict[str, Any]:
        """
        {mcp_tool.get('description', 'MCP Tool')}
        
        This is an MCP tool wrapper that calls the actual MCP server.
        """
        from open_webui.utils.mcp import mcp_manager
        
        try:
            # Prepare arguments
            arguments = {{}}
'''
        
        # Add parameter assignments
        for param in params:
            content += f'''            if {param} is not None:
                arguments["{param}"] = {param}
'''
        
        content += f'''            
            # Call the MCP tool
            result = await mcp_manager.call_tool(
                "{server_id}",
                "{mcp_tool['name']}",
                arguments
            )
            
            # Process result based on content type
            if isinstance(result, dict):
                # Handle different content types
                if "content" in result:
                    content_items = result.get("content", [])
                    if isinstance(content_items, list):
                        # Extract text content
                        text_content = []
                        for item in content_items:
                            if item.get("type") == "text":
                                text_content.append(item.get("text", ""))
                        
                        if text_content:
                            return {{
                                "status": "success",
                                "result": "\\n".join(text_content)
                            }}
                
                # Return raw result if no special processing needed
                return {{
                    "status": "success",
                    "result": result
                }}
            else:
                # Handle non-dict results
                return {{
                    "status": "success",
                    "result": str(result)
                }}
            
        except Exception as e:
            return {{
                "status": "error",
                "error": str(e)
            }}
'''
        
        return content
    
    @staticmethod
    async def remove_mcp_tools(server_id: str, user_id: str) -> int:
        """Remove all tools associated with an MCP server"""
        removed_count = 0
        
        try:
            # Get all tools for this user
            tools = Tools.get_tools_by_user_id(user_id)
            
            # Filter and delete MCP tools for this server
            for tool in tools:
                if (tool.meta and 
                    isinstance(tool.meta, dict) and
                    tool.meta.get('manifest', {}).get('type') == 'mcp' and 
                    tool.meta.get('manifest', {}).get('server_id') == server_id):
                    
                    if Tools.delete_tool_by_id(tool.id):
                        removed_count += 1
                        
        except Exception as e:
            log.error(f"Error removing MCP tools: {str(e)}")
        
        return removed_count
    
    @staticmethod
    async def execute_mcp_tool(server_id: str, tool_name: str, arguments: Dict) -> Dict[str, Any]:
        """Execute an MCP tool (used by generated tool wrappers)"""
        try:
            result = await mcp_manager.call_tool(server_id, tool_name, arguments)
            return {
                "status": "success",
                "result": result
            }
        except Exception as e:
            log.error(f"MCP tool execution failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }