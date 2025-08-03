"""
Test cases for MCP (Model Context Protocol) functionality
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from open_webui.models.mcp import (
    MCPServers,
    MCPServerForm,
    MCPServerModel,
    MCPTools,
    MCPToolModel,
)
from open_webui.routers.mcp import router
from open_webui.test.util.abstract_integration_test import AbstractIntegrationTest


class TestMCPIntegration(AbstractIntegrationTest):
    """Integration tests for MCP functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        super().setup_method()
        self.test_server_data = {
            "name": "Test MCP Server",
            "transport_type": "http",
            "url": "http://localhost:8080/mcp",
            "enabled": True,
            "meta": {"api_key": "test_key"},
        }
        
        self.test_custom_connection = {
            "type": "http",
            "config": {
                "url": "http://localhost:8080/mcp"
            }
        }

    def test_create_mcp_server(self):
        """Test creating a new MCP server"""
        response = self.client.post(
            "/api/v1/mcp/",
            json=self.test_server_data,
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == self.test_server_data["name"]
        assert data["transport_type"] == self.test_server_data["transport_type"]
        assert data["url"] == self.test_server_data["url"]
        assert data["enabled"] == self.test_server_data["enabled"]

    def test_get_mcp_servers(self):
        """Test retrieving all MCP servers for a user"""
        # First create a server
        self.client.post(
            "/api/v1/mcp/",
            json=self.test_server_data,
            headers={"Authorization": f"Bearer {self.user_token}"},
        )

        # Then retrieve all servers
        response = self.client.get(
            "/api/v1/mcp/",
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["name"] == self.test_server_data["name"]

    def test_update_mcp_server(self):
        """Test updating an existing MCP server"""
        # Create a server
        create_response = self.client.post(
            "/api/v1/mcp/",
            json=self.test_server_data,
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        server_id = create_response.json()["id"]

        # Update the server
        updated_data = self.test_server_data.copy()
        updated_data["name"] = "Updated MCP Server"
        updated_data["enabled"] = False

        response = self.client.put(
            f"/api/v1/mcp/{server_id}",
            json=updated_data,
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated MCP Server"
        assert data["enabled"] == False

    def test_delete_mcp_server(self):
        """Test deleting an MCP server"""
        # Create a server
        create_response = self.client.post(
            "/api/v1/mcp/",
            json=self.test_server_data,
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        server_id = create_response.json()["id"]

        # Delete the server
        response = self.client.delete(
            f"/api/v1/mcp/{server_id}",
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        assert response.status_code == 200

        # Verify deletion
        get_response = self.client.get(
            f"/api/v1/mcp/{server_id}",
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        assert get_response.status_code == 404

    def test_toggle_mcp_server(self):
        """Test toggling MCP server enabled state"""
        # Create a server
        create_response = self.client.post(
            "/api/v1/mcp/",
            json=self.test_server_data,
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        server_id = create_response.json()["id"]

        # Toggle to disabled
        response = self.client.post(
            f"/api/v1/mcp/{server_id}/toggle",
            json={"enabled": False},
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        assert response.status_code == 200
        assert response.json()["enabled"] == False

        # Toggle back to enabled
        response = self.client.post(
            f"/api/v1/mcp/{server_id}/toggle",
            json={"enabled": True},
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        assert response.status_code == 200
        assert response.json()["enabled"] == True

    @patch("open_webui.routers.mcp.test_mcp_connection")
    async def test_test_mcp_connection(self, mock_test_connection):
        """Test MCP connection testing"""
        # Create a server
        create_response = self.client.post(
            "/api/v1/mcp/",
            json=self.test_server_data,
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        server_id = create_response.json()["id"]

        # Mock successful connection
        mock_test_connection.return_value = {
            "status": "success",
            "message": "Connected successfully",
            "tools": [
                {"name": "tool1", "description": "Test tool 1"},
                {"name": "tool2", "description": "Test tool 2"},
            ],
        }

        # Test connection
        response = self.client.post(
            f"/api/v1/mcp/{server_id}/test",
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["tools"]) == 2

    @patch("open_webui.services.mcp_custom.discover_custom_tools")
    async def test_test_custom_mcp_connection(self, mock_discover_tools):
        """Test custom MCP connection testing"""
        # Mock successful tool discovery
        mock_discover_tools.return_value = {
            "tools": [
                {
                    "name": "custom_tool",
                    "description": "Custom MCP tool",
                    "inputSchema": {},
                }
            ],
            "count": 1,
        }

        # Test custom connection
        response = self.client.post(
            "/api/v1/mcp/test-custom",
            json=self.test_custom_connection,
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert len(data["tools"]) == 1
        assert data["tools"][0]["name"] == "custom_tool"

    def test_invalid_transport_type(self):
        """Test creating server with invalid transport type"""
        invalid_data = self.test_server_data.copy()
        invalid_data["transport_type"] = "invalid_type"

        response = self.client.post(
            "/api/v1/mcp/",
            json=invalid_data,
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        assert response.status_code == 422  # Validation error

    def test_unauthorized_access(self):
        """Test accessing MCP endpoints without authentication"""
        response = self.client.get("/api/v1/mcp/")
        assert response.status_code == 401

        response = self.client.post("/api/v1/mcp/", json=self.test_server_data)
        assert response.status_code == 401


class TestMCPUnit:
    """Unit tests for MCP functionality"""

    def test_mcp_server_form_validation(self):
        """Test MCPServerForm validation"""
        # Valid HTTP transport
        form = MCPServerForm(
            name="Test Server",
            transport_type="http",
            url="http://localhost:8080",
            enabled=True,
        )
        assert form.name == "Test Server"
        assert form.transport_type == "http"
        assert form.url == "http://localhost:8080"

        # Valid stdio transport
        form = MCPServerForm(
            name="Test Server",
            transport_type="stdio",
            command="python",
            args=["-m", "mcp_server"],
            enabled=True,
        )
        assert form.transport_type == "stdio"
        assert form.command == "python"
        assert form.args == ["-m", "mcp_server"]

    @pytest.mark.asyncio
    async def test_custom_connection_http(self):
        """Test custom HTTP MCP connection"""
        from open_webui.services.mcp_custom import discover_custom_tools

        # Mock the HTTP client
        with patch("open_webui.services.mcp_custom.streamablehttp_client") as mock_client:
            mock_session = AsyncMock()
            mock_session.initialize = AsyncMock()
            mock_session.list_tools = AsyncMock(
                return_value=MagicMock(
                    tools=[
                        MagicMock(
                            name="test_tool",
                            description="Test tool",
                            inputSchema={"type": "object"},
                        )
                    ]
                )
            )

            # Setup context manager mocks
            mock_client.return_value.__aenter__.return_value = (
                Mock(),  # read_stream
                Mock(),  # write_stream
                Mock(),  # _
            )

            with patch("open_webui.services.mcp_custom.ClientSession", return_value=mock_session):
                result = await discover_custom_tools(
                    "http", {"url": "http://localhost:8080/mcp"}
                )

                assert result["count"] == 1
                assert result["tools"][0]["name"] == "test_tool"
                assert result["tools"][0]["description"] == "Test tool"

    @pytest.mark.asyncio
    async def test_custom_connection_sse(self):
        """Test custom SSE MCP connection"""
        from open_webui.services.mcp_custom import discover_custom_tools

        # Mock the SSE client
        with patch("open_webui.services.mcp_custom.sse_client") as mock_client:
            mock_session = AsyncMock()
            mock_session.initialize = AsyncMock()
            mock_session.list_tools = AsyncMock(
                return_value=MagicMock(
                    tools=[
                        MagicMock(
                            name="sse_tool",
                            description="SSE tool",
                            inputSchema={"type": "object"},
                        )
                    ]
                )
            )

            # Setup context manager mocks
            mock_client.return_value.__aenter__.return_value = (
                Mock(),  # read
                Mock(),  # write
            )

            with patch("open_webui.services.mcp_custom.ClientSession", return_value=mock_session):
                result = await discover_custom_tools(
                    "sse", {"url": "http://localhost:8080/sse"}
                )

                assert result["count"] == 1
                assert result["tools"][0]["name"] == "sse_tool"
                assert result["tools"][0]["description"] == "SSE tool"

    def test_mcp_server_model_creation(self):
        """Test MCPServerModel creation and properties"""
        server = MCPServerModel(
            id="test-id",
            user_id="user-123",
            name="Test Server",
            transport_type="http",
            url="http://localhost:8080",
            args=[],
            env={},
            enabled=True,
            meta={"api_key": "test"},
            created_at=1234567890,
            updated_at=1234567890,
        )
        
        assert server.id == "test-id"
        assert server.user_id == "user-123"
        assert server.name == "Test Server"
        assert server.transport_type == "http"
        assert server.url == "http://localhost:8080"
        assert server.enabled == True
        assert server.meta["api_key"] == "test"

    def test_mcp_tool_model_creation(self):
        """Test MCPToolModel creation and properties"""
        tool = MCPToolModel(
            id="tool-id",
            server_id="server-id",
            tool_name="test_tool",
            description="Test tool description",
            parameters={"type": "object", "properties": {}},
            enabled=True,
            created_at=1234567890,
        )
        
        assert tool.id == "tool-id"
        assert tool.server_id == "server-id"
        assert tool.tool_name == "test_tool"
        assert tool.description == "Test tool description"
        assert tool.parameters["type"] == "object"
        assert tool.enabled == True


class TestMCPMarketplace:
    """Tests for MCP marketplace functionality"""

    @pytest.mark.skip(reason="mcp_local module has been removed")
    @pytest.mark.asyncio
    async def test_get_mcp_servers_list(self):
        """Test getting MCP servers from marketplace"""
        pass

    @pytest.mark.skip(reason="mcp_local module has been removed")
    @pytest.mark.asyncio
    async def test_get_mcp_server_details(self):
        """Test getting detailed MCP server information"""
        pass
        # Test removed - mcp_local module has been deleted
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "qualifiedName": "exa",
                "displayName": "Exa Search",
                "iconUrl": "https://exa.ai/icon.png",
                "deploymentUrl": "https://server.smithery.ai/exa/mcp",
                "connections": [],
                "tools": [
                    {"name": "web_search", "description": "Search the web"}
                ],
            }
            
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            # Create mock user
            mock_user = Mock()
            mock_user.id = "user-123"
            
            result = await get_mcp_server_details("exa", user=mock_user)
            
            assert result.qualifiedName == "exa"
            assert result.displayName == "Exa Search"
            assert result.iconUrl == "https://exa.ai/icon.png"
            assert len(result.tools) == 1
            assert result.tools[0]["name"] == "web_search"