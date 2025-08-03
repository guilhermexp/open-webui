<script lang="ts">
	import { toast } from 'svelte-sonner';
	import { createEventDispatcher, onMount, getContext } from 'svelte';
	
	import { getMCPServers, createMCPServer, updateMCPServer, deleteMCPServer, testMCPConnection, toggleMCPServer, syncMCPTools } from '$lib/apis/mcp';
	import type { MCPServer, MCPServerForm } from '$lib/apis/mcp';
	
	import Plus from '$lib/components/icons/Plus.svelte';
	import Spinner from '$lib/components/common/Spinner.svelte';
	import Tooltip from '$lib/components/common/Tooltip.svelte';
	
	import MCPServerCard from './MCP/MCPServerCard.svelte';
	import MCPServerModal from './MCP/MCPServerModal.svelte';
	import MCPConnectModal from './MCP/MCPConnectModal.svelte';
	import MCPMarketplace from './MCP/MCPMarketplace.svelte';
	import Cube from '$lib/components/icons/Cube.svelte';
	import Bolt from '$lib/components/icons/Bolt.svelte';
	import Cog6 from '$lib/components/icons/Cog6.svelte';
	
	const dispatch = createEventDispatcher();
	const i18n = getContext('i18n');
	
	let servers: MCPServer[] = [];
	let loading = true;
	let showAddModal = false;
	let showConnectModal = false;
	let showMarketplace = false;
	let selectedServer: MCPServer | null = null;
	let activeTab: 'servers' | 'marketplace' = 'servers';
	
	const loadServers = async () => {
		loading = true;
		try {
			servers = await getMCPServers(localStorage.token);
		} catch (error) {
			console.error('Failed to load MCP servers:', error);
			toast.error('Failed to load MCP servers');
		} finally {
			loading = false;
		}
	};
	
	const handleCreateServer = async (serverData: MCPServerForm) => {
		try {
			const newServer = await createMCPServer(localStorage.token, serverData);
			servers = [...servers, newServer];
			toast.success('MCP server created successfully');
			showAddModal = false;
			showConnectModal = false;
		} catch (error) {
			console.error('Failed to create MCP server:', error);
			toast.error('Failed to create MCP server');
		}
	};
	
	const handleUpdateServer = async (serverId: string, serverData: MCPServerForm) => {
		try {
			const updatedServer = await updateMCPServer(localStorage.token, serverId, serverData);
			servers = servers.map(s => s.id === serverId ? updatedServer : s);
			toast.success('MCP server updated successfully');
			selectedServer = null;
		} catch (error) {
			console.error('Failed to update MCP server:', error);
			toast.error('Failed to update MCP server');
		}
	};
	
	const handleDeleteServer = async (serverId: string) => {
		try {
			await deleteMCPServer(localStorage.token, serverId);
			servers = servers.filter(s => s.id !== serverId);
			toast.success('MCP server deleted successfully');
		} catch (error) {
			console.error('Failed to delete MCP server:', error);
			toast.error('Failed to delete MCP server');
		}
	};
	
	const handleTestConnection = async (serverId: string) => {
		try {
			const result = await testMCPConnection(localStorage.token, serverId);
			if (result.status === 'success') {
				toast.success(`Connected successfully! Found ${result.tools.length} tools`);
			} else {
				toast.error(result.message || 'Connection failed');
			}
		} catch (error) {
			console.error('Failed to test connection:', error);
			toast.error('Failed to test connection');
		}
	};
	
	const handleToggleServer = async (serverId: string, enabled: boolean) => {
		try {
			const updatedServer = await toggleMCPServer(localStorage.token, serverId, enabled);
			servers = servers.map(s => s.id === serverId ? updatedServer : s);
			toast.success(enabled ? 'MCP server enabled' : 'MCP server disabled');
		} catch (error) {
			console.error('Failed to toggle server:', error);
			toast.error('Failed to toggle server');
		}
	};
	
	const handleSyncTools = async (serverId: string) => {
		try {
			const result = await syncMCPTools(localStorage.token, serverId);
			toast.success(result.detail || 'Tools synced successfully');
		} catch (error) {
			console.error('Failed to sync tools:', error);
			toast.error('Failed to sync tools');
		}
	};
	
	onMount(() => {
		loadServers();
	});
</script>

<div class="flex flex-col h-full">
	<div class="mb-4">
		<div class="flex items-center justify-between mb-4">
			<div>
				<div class="text-base font-medium">MCP Integrations</div>
				<div class="text-sm text-gray-500 mt-0.5">
					Connect to MCP (Model Context Protocol) servers to extend your AI capabilities
				</div>
			</div>
		</div>
		
		<!-- Tabs -->
		<div class="flex gap-1 p-1 bg-gray-100 dark:bg-gray-800 rounded-lg">
			<button
				class="flex-1 px-3 py-2 rounded-md text-sm font-medium transition-colors {activeTab === 'servers' 
					? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm' 
					: 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'}"
				on:click={() => activeTab = 'servers'}
			>
				<div class="flex items-center justify-center gap-2">
					<Cog6 className="w-4 h-4" />
					My Connections
				</div>
			</button>
			<button
				class="flex-1 px-3 py-2 rounded-md text-sm font-medium transition-colors {activeTab === 'marketplace' 
					? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm' 
					: 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'}"
				on:click={() => activeTab = 'marketplace'}
			>
				<div class="flex items-center justify-center gap-2">
					<Cube className="w-4 h-4" />
					Browse Services
				</div>
			</button>
		</div>
	</div>
	
	<div class="flex-1 overflow-y-auto">
		{#if activeTab === 'servers'}
			<!-- My Connections Tab -->
			<div class="space-y-4">
				<!-- Action Buttons -->
				<div class="flex gap-3">
					<button
						class="flex-1 px-4 py-3 rounded-lg border-2 border-dashed border-gray-300 dark:border-gray-700 hover:border-gray-400 dark:hover:border-gray-600 transition-colors flex items-center justify-center gap-2 text-sm font-medium text-gray-700 dark:text-gray-300"
						on:click={() => showConnectModal = true}
						type="button"
					>
						<Bolt className="w-4 h-4" />
						Connect Custom Service
					</button>
					<button
						class="flex-1 px-4 py-3 rounded-lg border-2 border-dashed border-gray-300 dark:border-gray-700 hover:border-gray-400 dark:hover:border-gray-600 transition-colors flex items-center justify-center gap-2 text-sm font-medium text-gray-700 dark:text-gray-300"
						on:click={() => activeTab = 'marketplace'}
						type="button"
					>
						<Cube className="w-4 h-4" />
						Browse Marketplace
					</button>
				</div>
				
				<!-- Server List -->
				{#if loading}
					<div class="flex justify-center items-center h-64">
						<Spinner />
					</div>
				{:else if servers.length === 0}
					<div class="flex flex-col items-center justify-center h-64 text-gray-500">
						<div class="text-6xl mb-4">🔌</div>
						<div class="text-lg font-medium mb-2">No connections yet</div>
						<div class="text-sm text-gray-400">Connect to a service to get started</div>
					</div>
				{:else}
					<div class="space-y-3">
						{#each servers as server (server.id)}
							<MCPServerCard
								{server}
								on:edit={() => selectedServer = server}
								on:delete={() => handleDeleteServer(server.id)}
								on:test={() => handleTestConnection(server.id)}
								on:toggle={(e) => handleToggleServer(server.id, e.detail)}
								on:sync={() => handleSyncTools(server.id)}
							/>
						{/each}
					</div>
				{/if}
			</div>
		{:else}
			<!-- Browse Services Tab -->
			<MCPMarketplace saveHandler={handleCreateServer} />
		{/if}
	</div>
</div>

<!-- Modals -->
{#if showConnectModal}
	<MCPConnectModal
		show={showConnectModal}
		on:save={(e) => handleCreateServer(e.detail)}
		on:close={() => showConnectModal = false}
	/>
{/if}

{#if selectedServer}
	<MCPServerModal
		server={selectedServer}
		on:save={(e) => handleUpdateServer(selectedServer.id, e.detail)}
		on:close={() => selectedServer = null}
	/>
{/if}