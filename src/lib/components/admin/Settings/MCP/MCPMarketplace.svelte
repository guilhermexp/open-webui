<script lang="ts">
	import { onMount } from 'svelte';
	import { getMCPServersList, getMCPServerDetails } from '$lib/apis/mcp';
	import { toast } from 'svelte-sonner';
	import Modal from '$lib/components/common/Modal.svelte';
	import MCPServerConfigModal from './MCPServerConfigModal.svelte';

	export let saveHandler: Function;

	let searchQuery = '';
	let selectedCategory = 'all';
	let servers: any[] = [];
	let loading = false;
	let showConfigModal = false;
	let selectedServer: any = null;

	// Categories for filtering
	const categories = [
		{ id: 'all', name: 'All', icon: '🌐' },
		{ id: 'search', name: 'Search & AI', icon: '🔍' },
		{ id: 'development', name: 'Development', icon: '💻' },
		{ id: 'productivity', name: 'Productivity', icon: '📊' },
		{ id: 'communication', name: 'Communication', icon: '💬' },
		{ id: 'data', name: 'Data & Analytics', icon: '📈' }
	];

	onMount(async () => {
		await loadServers();
	});

	async function loadServers() {
		loading = true;
		try {
			const response = await getMCPServersList(localStorage.token, {
				q: searchQuery,
				page: 1,
				pageSize: 50
			});
			servers = response.servers || [];
		} catch (error) {
			console.error('Failed to load MCP servers:', error);
			toast.error('Failed to load MCP servers');
		}
		loading = false;
	}

	async function handleSearch() {
		await loadServers();
	}

	async function handleServerClick(server: any) {
		selectedServer = server;
		showConfigModal = true;
	}

	function handleConfigSave(config: any) {
		// Save the configured server
		if (saveHandler) {
			saveHandler({
				name: selectedServer.displayName,
				transport_type: 'http',
				url: `https://server.smithery.ai/${selectedServer.qualifiedName}/mcp`,
				meta: config,
				enabled: true
			});
		}
		showConfigModal = false;
		selectedServer = null;
		toast.success('MCP server configured successfully');
	}
</script>

<div class="flex flex-col gap-4">
	<!-- Search and Filter -->
	<div class="flex gap-4 mb-4">
		<div class="flex-1">
			<input
				type="text"
				bind:value={searchQuery}
				on:keydown={(e) => e.key === 'Enter' && handleSearch()}
				placeholder="Search MCP servers..."
				class="w-full px-4 py-2 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
			/>
		</div>
		<button
			on:click={handleSearch}
			class="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
		>
			Search
		</button>
	</div>

	<!-- Categories -->
	<div class="flex gap-2 overflow-x-auto pb-2">
		{#each categories as category}
			<button
				on:click={() => {
					selectedCategory = category.id;
					handleSearch();
				}}
				class="px-4 py-2 rounded-lg whitespace-nowrap transition-colors {selectedCategory === category.id
					? 'bg-primary-600 text-white'
					: 'bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700'}"
			>
				<span class="mr-2">{category.icon}</span>
				{category.name}
			</button>
		{/each}
	</div>

	<!-- Server Grid -->
	{#if loading}
		<div class="flex justify-center items-center h-64">
			<div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
		</div>
	{:else if servers.length > 0}
		<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
			{#each servers as server}
				<button
					on:click={() => handleServerClick(server)}
					class="p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 hover:border-primary-500 hover:shadow-lg transition-all text-left"
				>
					<div class="flex items-start gap-3">
						{#if server.iconUrl}
							<img src={server.iconUrl} alt={server.displayName} class="w-12 h-12 rounded-lg" />
						{:else}
							<div class="w-12 h-12 bg-gray-200 dark:bg-gray-700 rounded-lg flex items-center justify-center">
								<span class="text-xl">🔧</span>
							</div>
						{/if}
						<div class="flex-1">
							<h3 class="font-semibold text-gray-900 dark:text-white">{server.displayName}</h3>
							<p class="text-sm text-gray-600 dark:text-gray-400 line-clamp-2 mt-1">
								{server.description}
							</p>
							<div class="flex items-center gap-2 mt-2">
								<span class="text-xs text-gray-500 dark:text-gray-400">
									{server.useCount || 0} installs
								</span>
								{#if server.isDeployed}
									<span class="text-xs bg-green-100 text-green-800 px-2 py-0.5 rounded">
										Deployed
									</span>
								{/if}
							</div>
						</div>
					</div>
				</button>
			{/each}
		</div>
	{:else}
		<div class="text-center py-12 text-gray-500 dark:text-gray-400">
			No MCP servers found. Try a different search query.
		</div>
	{/if}
</div>

<!-- Configuration Modal -->
{#if showConfigModal && selectedServer}
	<MCPServerConfigModal
		server={selectedServer}
		on:save={(e) => handleConfigSave(e.detail)}
		on:close={() => {
			showConfigModal = false;
			selectedServer = null;
		}}
	/>
{/if}