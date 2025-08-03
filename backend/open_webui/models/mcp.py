"""
MCP (Model Context Protocol) Database Models and Business Logic
"""
from typing import Optional, Dict, List, Any
from enum import Enum
from sqlalchemy import Column, String, Text, JSON, Boolean, BigInteger, ForeignKey
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field
import time
import uuid
import json

from open_webui.internal.db import Base, JSONField, get_db

# NOTE: Add the following relationship to the User model in models/users.py:
# from sqlalchemy.orm import relationship
# mcp_servers = relationship("MCPServer", back_populates="user", cascade="all, delete-orphan")


####################
# Database Models
####################

class MCPTransportType(str, Enum):
    """Supported MCP transport types"""
    STDIO = "stdio"
    HTTP = "http"
    WEBSOCKET = "websocket"


class MCPServer(Base):
    """MCP Server database model"""
    __tablename__ = "mcp_servers"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)  # Temporarily removed FK
    name = Column(Text, nullable=False)
    transport_type = Column(String, nullable=False)
    command = Column(Text)  # For stdio transport
    url = Column(Text)  # For http/websocket transport
    args = Column(JSONField, default=list)
    env = Column(JSONField, default=dict)
    enabled = Column(Boolean, default=True)
    meta = Column(JSONField, default=dict)
    created_at = Column(BigInteger)
    updated_at = Column(BigInteger)
    
    # Relationships
    # user = relationship("User", back_populates="mcp_servers")
    # NOTE: Temporarily disabled to avoid circular import issues
    tools = relationship("MCPTool", back_populates="server", cascade="all, delete-orphan")


class MCPTool(Base):
    """MCP Tool database model"""
    __tablename__ = "mcp_tools"
    
    id = Column(String, primary_key=True)
    server_id = Column(String, ForeignKey("mcp_servers.id", ondelete="CASCADE"), nullable=False)
    tool_name = Column(String, nullable=False)
    description = Column(Text)
    parameters = Column(JSONField, default=dict)
    enabled = Column(Boolean, default=True)
    created_at = Column(BigInteger)
    
    # Relationships
    server = relationship("MCPServer", back_populates="tools")


####################
# Pydantic Models
####################

class MCPServerModel(BaseModel):
    """MCP Server response model"""
    id: str
    user_id: str
    name: str
    transport_type: MCPTransportType
    command: Optional[str] = None
    url: Optional[str] = None
    args: List[str] = Field(default_factory=list)
    env: Dict[str, str] = Field(default_factory=dict)
    enabled: bool = True
    meta: Dict[str, Any] = Field(default_factory=dict)
    created_at: int
    updated_at: int
    
    model_config = {
        "from_attributes": True
    }


class MCPServerForm(BaseModel):
    """MCP Server input form"""
    name: str
    transport_type: MCPTransportType
    command: Optional[str] = None
    url: Optional[str] = None
    args: Optional[List[str]] = Field(default_factory=list)
    env: Optional[Dict[str, str]] = Field(default_factory=dict)
    enabled: bool = True
    meta: Optional[Dict[str, Any]] = Field(default_factory=dict)


class MCPToolModel(BaseModel):
    """MCP Tool response model"""
    id: str
    server_id: str
    tool_name: str
    description: Optional[str] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)
    enabled: bool = True
    created_at: int
    
    model_config = {
        "from_attributes": True
    }


class MCPConnectionStatus(BaseModel):
    """MCP connection test result"""
    status: str  # "success" or "error"
    message: str
    tools: List[Dict[str, Any]] = Field(default_factory=list)


####################
# Business Logic
####################

class MCPServers:
    """MCP Server business logic"""
    
    @staticmethod
    def get_servers_by_user_id(user_id: str) -> List[MCPServerModel]:
        """Get all MCP servers for a user"""
        with get_db() as db:
            servers = db.query(MCPServer).filter(
                MCPServer.user_id == user_id
            ).all()
            return [MCPServerModel.model_validate(server) for server in servers]
    
    @staticmethod
    def get_server_by_id_and_user(server_id: str, user_id: str) -> Optional[MCPServerModel]:
        """Get a specific MCP server by ID and user"""
        with get_db() as db:
            server = db.query(MCPServer).filter(
                MCPServer.id == server_id,
                MCPServer.user_id == user_id
            ).first()
            return MCPServerModel.model_validate(server) if server else None
    
    @staticmethod
    def create_server(user_id: str, form_data: MCPServerForm) -> Optional[MCPServerModel]:
        """Create a new MCP server"""
        with get_db() as db:
            server_id = str(uuid.uuid4())
            current_time = int(time.time())
            
            server = MCPServer(
                id=server_id,
                user_id=user_id,
                name=form_data.name,
                transport_type=form_data.transport_type,
                command=form_data.command,
                url=form_data.url,
                args=form_data.args or [],
                env=form_data.env or {},
                enabled=form_data.enabled,
                meta=form_data.meta or {},
                created_at=current_time,
                updated_at=current_time
            )
            
            db.add(server)
            db.commit()
            db.refresh(server)
            
            return MCPServerModel.model_validate(server)
    
    @staticmethod
    def update_server(server_id: str, user_id: str, form_data: MCPServerForm) -> Optional[MCPServerModel]:
        """Update an existing MCP server"""
        with get_db() as db:
            server = db.query(MCPServer).filter(
                MCPServer.id == server_id,
                MCPServer.user_id == user_id
            ).first()
            
            if not server:
                return None
            
            server.name = form_data.name
            server.transport_type = form_data.transport_type
            server.command = form_data.command
            server.url = form_data.url
            server.args = form_data.args or []
            server.env = form_data.env or {}
            server.enabled = form_data.enabled
            server.meta = form_data.meta or {}
            server.updated_at = int(time.time())
            
            db.commit()
            db.refresh(server)
            
            return MCPServerModel.model_validate(server)
    
    @staticmethod
    def delete_server(server_id: str, user_id: str) -> bool:
        """Delete an MCP server"""
        with get_db() as db:
            server = db.query(MCPServer).filter(
                MCPServer.id == server_id,
                MCPServer.user_id == user_id
            ).first()
            
            if not server:
                return False
            
            db.delete(server)
            db.commit()
            
            return True
    
    @staticmethod
    def toggle_server(server_id: str, user_id: str, enabled: bool) -> Optional[MCPServerModel]:
        """Enable or disable an MCP server"""
        with get_db() as db:
            server = db.query(MCPServer).filter(
                MCPServer.id == server_id,
                MCPServer.user_id == user_id
            ).first()
            
            if not server:
                return None
            
            server.enabled = enabled
            server.updated_at = int(time.time())
            
            db.commit()
            db.refresh(server)
            
            return MCPServerModel.model_validate(server)


class MCPTools:
    """MCP Tool business logic"""
    
    @staticmethod
    def get_tools_by_server_id(server_id: str) -> List[MCPToolModel]:
        """Get all tools for an MCP server"""
        with get_db() as db:
            tools = db.query(MCPTool).filter(
                MCPTool.server_id == server_id
            ).all()
            return [MCPToolModel.model_validate(tool) for tool in tools]
    
    @staticmethod
    def create_or_update_tool(server_id: str, tool_data: Dict[str, Any]) -> MCPToolModel:
        """Create or update an MCP tool"""
        with get_db() as db:
            tool_id = f"mcp_{server_id}_{tool_data['name']}"
            
            existing_tool = db.query(MCPTool).filter(
                MCPTool.id == tool_id
            ).first()
            
            if existing_tool:
                # Update existing tool
                existing_tool.tool_name = tool_data['name']
                existing_tool.description = tool_data.get('description', '')
                existing_tool.parameters = tool_data.get('inputSchema', {})
                tool = existing_tool
            else:
                # Create new tool
                tool = MCPTool(
                    id=tool_id,
                    server_id=server_id,
                    tool_name=tool_data['name'],
                    description=tool_data.get('description', ''),
                    parameters=tool_data.get('inputSchema', {}),
                    enabled=True,
                    created_at=int(time.time())
                )
                db.add(tool)
            
            db.commit()
            db.refresh(tool)
            
            return MCPToolModel.model_validate(tool)
    
    @staticmethod
    def delete_tools_by_server_id(server_id: str) -> bool:
        """Delete all tools for an MCP server"""
        with get_db() as db:
            db.query(MCPTool).filter(
                MCPTool.server_id == server_id
            ).delete()
            db.commit()
            return True