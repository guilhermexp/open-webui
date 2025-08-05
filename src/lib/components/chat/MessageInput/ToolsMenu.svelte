<script lang="ts">
	import { DropdownMenu } from 'bits-ui';
	import { flyAndScale } from '$lib/utils/transitions';
	import { getContext, onMount, tick } from 'svelte';

	import { config, user, tools as _tools, mobile, toolServers } from '$lib/stores';
	import { getTools } from '$lib/apis/tools';

	import Dropdown from '$lib/components/common/Dropdown.svelte';
	import Tooltip from '$lib/components/common/Tooltip.svelte';
	import Switch from '$lib/components/common/Switch.svelte';
	import WrenchSolid from '$lib/components/icons/WrenchSolid.svelte';

	const i18n = getContext('i18n');

	export let selectedToolIds: string[] = [];
	export let transparentBackground = false;
	export let onClose: Function;

	let tools = {};
	let servers = {};
	let show = false;
	let showAllTools = false;

	$: if (show) {
		init();
	}

	const init = async () => {
		if ($_tools === null) {
			await _tools.set(await getTools(localStorage.token));
		}

		// Group MCP tools by server
		const mcpServers = {};
		const regularTools = {};

		$_tools.forEach(tool => {
			if (tool.id.startsWith('mcp_')) {
				// Extract server info from mcp_{server_id}_{tool_name}
				const parts = tool.id.split('_');
				if (parts.length >= 3) {
					const serverId = parts[1];
					
					// Get server name from tool manifest if available
					let serverName = serverId;
					
					// Try to get the server name from toolServers store
					if ($toolServers) {
						// Find the server that matches this serverId
						const server = Object.values($toolServers).find(s => {
							// Check if this server has tools that match our serverId
							return s.id === serverId || s.name === serverId;
						});
						
						if (server && server.name) {
							serverName = server.name;
						}
					}
					
					// If still not found and tool name has format "ServerName: ToolName"
					if (serverName === serverId && tool.name.includes(':')) {
						serverName = tool.name.split(':')[0].trim();
					}
					
					if (!mcpServers[serverId]) {
						mcpServers[serverId] = {
							name: serverName,
							id: serverId,
							tools: [],
							enabled: false
						};
					}
					
					const enabled = selectedToolIds.includes(tool.id);
					mcpServers[serverId].tools.push({
						id: tool.id,
						name: tool.name.includes(':') ? tool.name.split(':')[1].trim() : tool.name,
						description: tool.meta?.description,
						enabled: enabled
					});
					
					// Update server enabled state
					if (enabled) {
						mcpServers[serverId].enabled = true;
					}
				}
			} else {
				// Regular tools
				regularTools[tool.id] = {
					id: tool.id,
					name: tool.name,
					description: tool.meta?.description,
					enabled: selectedToolIds.includes(tool.id)
				};
			}
		});

		servers = mcpServers;
		tools = regularTools;
	};

	onMount(() => {
		init();
	});
</script>

<Dropdown
	bind:show
	on:change={(e) => {
		if (e.detail === false) {
			onClose();
		}
	}}
>
	<button
		type="button"
		class="rounded-lg p-2 {transparentBackground ? '' : 'bg-black/5 dark:bg-white/5'} cursor-pointer
			   hover:bg-black/10 dark:hover:bg-white/10 
			   focus:outline-none focus:ring-1 focus:ring-blue-500
			   text-black/40 dark:text-white/40 hover:text-black dark:hover:text-white
			   transition-colors {selectedToolIds?.length > 0
			? 'text-black dark:text-white' 
			: ''}"
		aria-label={$i18n.t('Tools')}
	>
		<WrenchSolid className="w-4 h-4" />
	</button>
	
	<DropdownMenu.Content
		slot="content"
		transition={flyAndScale}
		sideOffset={10}
		side="bottom"
		align="start"
		class="w-full max-w-[280px] rounded-xl px-1 py-1 border border-gray-300/30 dark:border-gray-700/50 z-50 bg-white dark:bg-gray-850 dark:text-white shadow-sm"
	>
		<!-- MCP Servers -->
		{#if Object.keys(servers).length > 0}
			<div class="px-3 py-2">
				<div class="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">{$i18n.t('MCP Servers')}</div>
			</div>
			<div class="max-h-64 overflow-y-auto">
				{#each Object.keys(servers) as serverId}
					<div class="px-1">
						<button
							class="flex w-full items-center justify-between gap-2 px-3 py-2 text-sm font-medium cursor-pointer rounded-xl hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
							on:click={() => {
								servers[serverId].enabled = !servers[serverId].enabled;
								
								servers[serverId].tools.forEach(tool => {
									tool.enabled = servers[serverId].enabled;
									if (servers[serverId].enabled) {
										if (!selectedToolIds.includes(tool.id)) {
											selectedToolIds = [...selectedToolIds, tool.id];
										}
									} else {
										selectedToolIds = selectedToolIds.filter(id => id !== tool.id);
									}
								});
							}}
						>
							<div class="flex items-center gap-2 flex-1 min-w-0">
								<WrenchSolid className="w-4 h-4 flex-shrink-0 text-gray-500 dark:text-gray-400" />
								<span class="truncate">{servers[serverId].name}</span>
							</div>
							<Switch
								state={servers[serverId].enabled}
								on:change={async (e) => {
									const state = e.detail;
									await tick();
									
									servers[serverId].tools.forEach(tool => {
										tool.enabled = state;
										if (state) {
											if (!selectedToolIds.includes(tool.id)) {
												selectedToolIds = [...selectedToolIds, tool.id];
											}
										} else {
											selectedToolIds = selectedToolIds.filter(id => id !== tool.id);
										}
									});
								}}
							/>
						</button>
						
						<!-- Expanded tools -->
						{#if servers[serverId].enabled}
							<div class="ml-7 mr-2 mb-2 space-y-1">
								{#each servers[serverId].tools as tool}
									<label 
										class="flex items-center justify-between gap-2 px-3 py-1.5 text-xs cursor-pointer rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
									>
										<Tooltip content={tool.description ?? ''} placement="left" className="flex-1 min-w-0">
											<span class="truncate block">{tool.name}</span>
										</Tooltip>
										<input
											type="checkbox"
											class="w-4 h-4 rounded border-gray-300 dark:border-gray-600 text-blue-600 focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700"
											bind:checked={tool.enabled}
											on:change={(e) => {
												if (e.target.checked) {
													selectedToolIds = [...selectedToolIds, tool.id];
												} else {
													selectedToolIds = selectedToolIds.filter(id => id !== tool.id);
												}
											}}
										/>
									</label>
								{/each}
							</div>
						{/if}
					</div>
				{/each}
			</div>
			{#if Object.keys(tools).length > 0}
				<hr class="border-gray-200 dark:border-gray-700 my-2" />
			{/if}
		{/if}
		
		<!-- Regular Tools -->
		{#if Object.keys(tools).length > 0}
			<div class="px-3 py-2">
				<div class="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">{$i18n.t('Tools')}</div>
			</div>
			<div class="{showAllTools ? '' : 'max-h-32'} overflow-y-auto px-1">
				{#each Object.keys(tools) as toolId}
					<button
						class="flex w-full items-center justify-between gap-2 px-3 py-2 text-sm font-medium cursor-pointer rounded-xl hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
						on:click={() => {
							tools[toolId].enabled = !tools[toolId].enabled;
							if (tools[toolId].enabled) {
								selectedToolIds = [...selectedToolIds, toolId];
							} else {
								selectedToolIds = selectedToolIds.filter((id) => id !== toolId);
							}
						}}
					>
						<div class="flex items-center gap-2 flex-1 min-w-0">
							<WrenchSolid className="w-4 h-4 flex-shrink-0 text-gray-500 dark:text-gray-400" />
							<Tooltip
								content={tools[toolId]?.description ?? ''}
								placement="top-start"
								className="truncate"
							>
								{tools[toolId].name}
							</Tooltip>
						</div>
						<Switch
							state={tools[toolId].enabled}
							on:change={async (e) => {
								const state = e.detail;
								await tick();
								if (state) {
									selectedToolIds = [...selectedToolIds, toolId];
								} else {
									selectedToolIds = selectedToolIds.filter((id) => id !== toolId);
								}
							}}
						/>
					</button>
				{/each}
			</div>
			{#if Object.keys(tools).length > 3}
				<div class="px-3 py-1">
					<button
						class="flex w-full justify-center items-center py-1 text-xs text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 transition-colors"
						on:click={() => {
							showAllTools = !showAllTools;
						}}
						title={showAllTools ? $i18n.t('Show Less') : $i18n.t('Show All')}
					>
						<svg
							xmlns="http://www.w3.org/2000/svg"
							fill="none"
							viewBox="0 0 24 24"
							stroke-width="2"
							stroke="currentColor"
							class="w-4 h-4 transition-transform duration-200 {showAllTools ? 'rotate-180' : ''}"
						>
							<path stroke-linecap="round" stroke-linejoin="round" d="m19.5 8.25-7.5 7.5-7.5-7.5" />
						</svg>
					</button>
				</div>
			{/if}
		{/if}
		
		<!-- Empty state -->
		{#if Object.keys(servers).length === 0 && Object.keys(tools).length === 0}
			<div class="px-3 py-8 text-center text-sm text-gray-500 dark:text-gray-400">
				{$i18n.t('No tools available')}
			</div>
		{/if}
	</DropdownMenu.Content>
</Dropdown>