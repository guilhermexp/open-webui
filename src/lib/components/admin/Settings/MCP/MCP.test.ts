import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, fireEvent, waitFor } from '@testing-library/svelte';
import { writable } from 'svelte/store';
import MCP from './MCP.svelte';
import * as mcpApi from '$lib/apis/mcp';

// Mock the MCP API functions
vi.mock('$lib/apis/mcp', () => ({
	getMCPServers: vi.fn(),
	createMCPServer: vi.fn(),
	updateMCPServer: vi.fn(),
	deleteMCPServer: vi.fn(),
	testMCPConnection: vi.fn(),
	toggleMCPServer: vi.fn(),
	syncMCPTools: vi.fn(),
	getMCPServersList: vi.fn(),
	getMCPServerDetails: vi.fn()
}));

// Mock the stores
vi.mock('$lib/stores', () => ({
	mcp: writable({})
}));

// Mock localStorage
const localStorageMock = {
	getItem: vi.fn(),
	setItem: vi.fn(),
	clear: vi.fn()
};
global.localStorage = localStorageMock;

describe('MCP Component', () => {
	beforeEach(() => {
		vi.clearAllMocks();
		localStorageMock.getItem.mockReturnValue('test-token');
	});

	it('should render the MCP component', async () => {
		vi.mocked(mcpApi.getMCPServers).mockResolvedValue([]);

		const { getByText } = render(MCP);

		expect(getByText('MCP Integrations')).toBeTruthy();
		expect(getByText('Connect to MCP (Model Context Protocol) servers to extend your AI capabilities')).toBeTruthy();
	});

	it('should display tabs for My Connections and Browse Services', async () => {
		vi.mocked(mcpApi.getMCPServers).mockResolvedValue([]);

		const { getByText } = render(MCP);

		expect(getByText('My Connections')).toBeTruthy();
		expect(getByText('Browse Services')).toBeTruthy();
	});

	it('should load and display existing MCP servers', async () => {
		const mockServers = [
			{
				id: '1',
				name: 'Test Server',
				transport_type: 'http',
				url: 'http://localhost:8080',
				enabled: true,
				user_id: 'user-1',
				args: [],
				env: {},
				meta: {},
				created_at: Date.now(),
				updated_at: Date.now()
			}
		];

		vi.mocked(mcpApi.getMCPServers).mockResolvedValue(mockServers);

		const { container } = render(MCP);

		await waitFor(() => {
			const serverCard = container.querySelector('[data-server-id="1"]');
			expect(serverCard).toBeTruthy();
		});
	});

	it('should open connect modal when clicking Connect Custom Service', async () => {
		vi.mocked(mcpApi.getMCPServers).mockResolvedValue([]);

		const { getByText, getByRole } = render(MCP);

		const connectButton = getByText('Connect Custom Service');
		await fireEvent.click(connectButton);

		await waitFor(() => {
			expect(getByText('Connect New Service')).toBeTruthy();
			expect(getByText('How would you like to connect?')).toBeTruthy();
		});
	});

	it('should switch to marketplace tab when clicking Browse Marketplace', async () => {
		vi.mocked(mcpApi.getMCPServers).mockResolvedValue([]);
		vi.mocked(mcpApi.getMCPServersList).mockResolvedValue({
			servers: [],
			pagination: { totalCount: 0 }
		});

		const { getByText } = render(MCP);

		const marketplaceButton = getByText('Browse Marketplace');
		await fireEvent.click(marketplaceButton);

		await waitFor(() => {
			expect(getByText('Search MCP servers...')).toBeTruthy();
		});
	});

	it('should handle server creation', async () => {
		vi.mocked(mcpApi.getMCPServers).mockResolvedValue([]);
		vi.mocked(mcpApi.createMCPServer).mockResolvedValue({
			id: '2',
			name: 'New Server',
			transport_type: 'http',
			url: 'http://localhost:9090',
			enabled: true,
			user_id: 'user-1',
			args: [],
			env: {},
			meta: {},
			created_at: Date.now(),
			updated_at: Date.now()
		});

		const { component } = render(MCP);

		// Simulate server creation through the component's handler
		await component.handleCreateServer({
			name: 'New Server',
			transport_type: 'http',
			url: 'http://localhost:9090',
			enabled: true
		});

		expect(mcpApi.createMCPServer).toHaveBeenCalledWith(
			'test-token',
			expect.objectContaining({
				name: 'New Server',
				transport_type: 'http',
				url: 'http://localhost:9090'
			})
		);
	});

	it('should handle server deletion', async () => {
		const mockServers = [
			{
				id: '1',
				name: 'Test Server',
				transport_type: 'http',
				url: 'http://localhost:8080',
				enabled: true,
				user_id: 'user-1',
				args: [],
				env: {},
				meta: {},
				created_at: Date.now(),
				updated_at: Date.now()
			}
		];

		vi.mocked(mcpApi.getMCPServers).mockResolvedValue(mockServers);
		vi.mocked(mcpApi.deleteMCPServer).mockResolvedValue();

		const { component } = render(MCP);

		await waitFor(() => {
			expect(component.servers.length).toBe(1);
		});

		await component.handleDeleteServer('1');

		expect(mcpApi.deleteMCPServer).toHaveBeenCalledWith('test-token', '1');
	});

	it('should handle server toggle', async () => {
		const mockServers = [
			{
				id: '1',
				name: 'Test Server',
				transport_type: 'http',
				url: 'http://localhost:8080',
				enabled: true,
				user_id: 'user-1',
				args: [],
				env: {},
				meta: {},
				created_at: Date.now(),
				updated_at: Date.now()
			}
		];

		vi.mocked(mcpApi.getMCPServers).mockResolvedValue(mockServers);
		vi.mocked(mcpApi.toggleMCPServer).mockResolvedValue({
			...mockServers[0],
			enabled: false
		});

		const { component } = render(MCP);

		await component.handleToggleServer('1', false);

		expect(mcpApi.toggleMCPServer).toHaveBeenCalledWith('test-token', '1', false);
	});

	it('should handle connection testing', async () => {
		vi.mocked(mcpApi.getMCPServers).mockResolvedValue([]);
		vi.mocked(mcpApi.testMCPConnection).mockResolvedValue({
			status: 'success',
			message: 'Connected successfully',
			tools: [{ name: 'tool1' }, { name: 'tool2' }]
		});

		const { component } = render(MCP);

		await component.handleTestConnection('1');

		expect(mcpApi.testMCPConnection).toHaveBeenCalledWith('test-token', '1');
	});

	it('should handle tool synchronization', async () => {
		vi.mocked(mcpApi.getMCPServers).mockResolvedValue([]);
		vi.mocked(mcpApi.syncMCPTools).mockResolvedValue({
			detail: 'Successfully synced 5 tools',
			count: 5
		});

		const { component } = render(MCP);

		await component.handleSyncTools('1');

		expect(mcpApi.syncMCPTools).toHaveBeenCalledWith('test-token', '1');
	});

	it('should show empty state when no servers exist', async () => {
		vi.mocked(mcpApi.getMCPServers).mockResolvedValue([]);

		const { getByText } = render(MCP);

		await waitFor(() => {
			expect(getByText('No connections yet')).toBeTruthy();
			expect(getByText('Connect to a service to get started')).toBeTruthy();
		});
	});

	it('should handle errors gracefully', async () => {
		vi.mocked(mcpApi.getMCPServers).mockRejectedValue(new Error('Network error'));

		const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

		render(MCP);

		await waitFor(() => {
			expect(consoleSpy).toHaveBeenCalledWith(
				'Failed to load MCP servers:',
				expect.any(Error)
			);
		});

		consoleSpy.mockRestore();
	});
});