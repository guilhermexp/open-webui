<script lang="ts">
	import { createEventDispatcher, getContext } from 'svelte';
	import type { MCPServer } from '$lib/apis/mcp';
	import Switch from '$lib/components/common/Switch.svelte';
	import Tooltip from '$lib/components/common/Tooltip.svelte';
	
	export let server: MCPServer;
	
	const dispatch = createEventDispatcher();
	const i18n = getContext('i18n');
	
	const getTransportIcon = (type: string) => {
		switch (type) {
			case 'stdio': return '🖥️';
			case 'http': return '🌐';
			case 'websocket': return '🔌';
			default: return '❓';
		}
	};
	
	const getTransportLabel = (type: string) => {
		switch (type) {
			case 'stdio': return 'Standard I/O';
			case 'http': return 'HTTP';
			case 'websocket': return 'WebSocket';
			default: return type;
		}
	};
</script>

<div class="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
	<div class="flex items-center gap-4 flex-1">
		<!-- Status Indicator -->
		<div class="flex items-center">
			<div class="w-10 h-10 flex items-center justify-center text-2xl rounded-lg bg-gray-100 dark:bg-gray-700">
				{getTransportIcon(server.transport_type)}
			</div>
		</div>
		
		<!-- Server Info -->
		<div class="flex-1">
			<div class="flex items-center gap-2">
				<h4 class="font-medium text-gray-900 dark:text-gray-100">
					{server.name}
				</h4>
				<span class="text-xs px-2 py-0.5 rounded-full bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-400">
					{getTransportLabel(server.transport_type)}
				</span>
			</div>
			
			<div class="text-sm text-gray-500 dark:text-gray-400 mt-0.5">
				{#if server.transport_type === 'stdio'}
					<code class="font-mono text-xs">{server.command}</code>
				{:else if server.transport_type === 'http' || server.transport_type === 'websocket'}
					<code class="font-mono text-xs">{server.url}</code>
				{/if}
			</div>
			
			{#if server.args && server.args.length > 0}
				<div class="text-xs text-gray-400 dark:text-gray-500 mt-1">
					{$i18n.t('{{count}} arguments', { count: server.args.length })}
				</div>
			{/if}
		</div>
	</div>
	
	<!-- Actions -->
	<div class="flex items-center gap-2">
		<!-- Enable/Disable Toggle -->
		<Switch
			bind:state={server.enabled}
			on:change={(e) => dispatch('toggle', e.detail)}
		/>
		
		<!-- Action Buttons -->
		<div class="flex items-center gap-1 ml-2">
			<!-- Test Connection -->
			<Tooltip content={$i18n.t('Test Connection')}>
				<button
					type="button"
					on:click={() => dispatch('test')}
					class="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg transition-colors"
				>
					<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
					</svg>
				</button>
			</Tooltip>
			
			<!-- Sync Tools -->
			<Tooltip content={$i18n.t('Sync Tools')}>
				<button
					type="button"
					on:click={() => dispatch('sync')}
					class="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg transition-colors"
					disabled={!server.enabled}
				>
					<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
					</svg>
				</button>
			</Tooltip>
			
			<!-- Edit -->
			<Tooltip content={$i18n.t('Edit')}>
				<button
					type="button"
					on:click={() => dispatch('edit')}
					class="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg transition-colors"
				>
					<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
					</svg>
				</button>
			</Tooltip>
			
			<!-- Delete -->
			<Tooltip content={$i18n.t('Delete')}>
				<button
					type="button"
					on:click={() => {
						if (confirm($i18n.t('Are you sure you want to delete this MCP server?'))) {
							dispatch('delete');
						}
					}}
					class="p-2 hover:bg-red-100 dark:hover:bg-red-900/20 text-red-600 rounded-lg transition-colors"
				>
					<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
					</svg>
				</button>
			</Tooltip>
		</div>
	</div>
</div>