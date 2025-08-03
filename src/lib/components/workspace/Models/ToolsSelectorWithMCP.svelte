<script lang="ts">
	import Checkbox from '$lib/components/common/Checkbox.svelte';
	import { getContext, onMount } from 'svelte';
	import { getMCPServers } from '$lib/apis/mcp';

	export let tools = [];
	export let selectedToolIds = [];

	let _tools = {};
	let mcpServers = [];
	let mcpServerTools = {};
	let mcpServerStates = {};

	const i18n = getContext('i18n');

	onMount(async () => {
		// Load regular tools
		_tools = tools.reduce((acc, tool) => {
			// Skip MCP tools from the regular tools list
			if (!tool.id.startsWith('mcp_')) {
				acc[tool.id] = {
					...tool,
					selected: selectedToolIds.includes(tool.id)
				};
			}
			return acc;
		}, {});

		// Load MCP servers and organize their tools
		try {
			mcpServers = await getMCPServers(localStorage.token);
			
			// Group MCP tools by server
			for (const server of mcpServers) {
				if (server.enabled) {
					mcpServerTools[server.id] = [];
					
					// Find all tools belonging to this server
					for (const tool of tools) {
						if (tool.id.startsWith(`mcp_${server.id}_`)) {
							mcpServerTools[server.id].push(tool);
						}
					}
					
					// Check if all tools from this server are selected
					const serverToolIds = mcpServerTools[server.id].map(t => t.id);
					const selectedServerTools = serverToolIds.filter(id => selectedToolIds.includes(id));
					
					mcpServerStates[server.id] = {
						selected: selectedServerTools.length === serverToolIds.length && serverToolIds.length > 0,
						partial: selectedServerTools.length > 0 && selectedServerTools.length < serverToolIds.length
					};
				}
			}
		} catch (error) {
			console.error('Failed to load MCP servers:', error);
		}
	});

	function toggleMCPServer(serverId: string) {
		const serverToolIds = mcpServerTools[serverId].map(t => t.id);
		const isSelected = mcpServerStates[serverId].selected;
		
		if (isSelected) {
			// Deselect all tools from this server
			selectedToolIds = selectedToolIds.filter(id => !serverToolIds.includes(id));
			mcpServerStates[serverId].selected = false;
			mcpServerStates[serverId].partial = false;
		} else {
			// Select all tools from this server
			selectedToolIds = [...new Set([...selectedToolIds, ...serverToolIds])];
			mcpServerStates[serverId].selected = true;
			mcpServerStates[serverId].partial = false;
		}
	}

	function toggleRegularTool(toolId: string) {
		_tools[toolId].selected = !_tools[toolId].selected;
		if (_tools[toolId].selected) {
			selectedToolIds = [...selectedToolIds, toolId];
		} else {
			selectedToolIds = selectedToolIds.filter(id => id !== toolId);
		}
	}
</script>

<div>
	<div class="flex w-full justify-between mb-1">
		<div class=" self-center text-sm font-semibold">{$i18n.t('Tools')}</div>
	</div>

	<div class=" text-xs dark:text-gray-500 mb-3">
		{$i18n.t('To select toolkits here, add them to the "Tools" workspace first.')}
	</div>

	<div class="flex flex-col gap-3">
		<!-- MCP Servers Section -->
		{#if mcpServers.length > 0}
			<div>
				<div class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-2">
					{$i18n.t('MCP Servers')}
				</div>
				<div class="flex flex-col gap-2">
					{#each mcpServers.filter(s => s.enabled && mcpServerTools[s.id]?.length > 0) as server}
						<div class="flex items-center gap-3 p-2 rounded-md hover:bg-gray-50 dark:hover:bg-gray-800">
							<div class="flex items-center">
								<Checkbox
									state={mcpServerStates[server.id]?.selected ? 'checked' : 
										   mcpServerStates[server.id]?.partial ? 'partial' : 'unchecked'}
									on:change={() => toggleMCPServer(server.id)}
								/>
							</div>
							<div class="flex items-center gap-2 flex-1">
								<div class="w-6 h-6 rounded bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
									<svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
									</svg>
								</div>
								<div class="flex-1">
									<div class="text-sm font-medium capitalize">{server.name}</div>
									<div class="text-xs text-gray-500">
										{mcpServerTools[server.id].length} {$i18n.t('tools')}
									</div>
								</div>
							</div>
						</div>
					{/each}
				</div>
			</div>
		{/if}

		<!-- Regular Tools Section -->
		{#if Object.keys(_tools).length > 0}
			<div>
				<div class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-2">
					{$i18n.t('Individual Tools')}
				</div>
				<div class="flex flex-wrap gap-3">
					{#each Object.keys(_tools) as toolId}
						<div class="flex items-center gap-2">
							<div class="self-center flex items-center">
								<Checkbox
									state={_tools[toolId].selected ? 'checked' : 'unchecked'}
									on:change={() => toggleRegularTool(toolId)}
								/>
							</div>
							<div class="py-0.5 text-sm capitalize font-medium">
								{_tools[toolId].name}
							</div>
						</div>
					{/each}
				</div>
			</div>
		{/if}
	</div>
</div>

<style>
	/* Add animation for checkbox state changes */
	:global(.checkbox-container) {
		transition: all 0.2s ease;
	}
</style>