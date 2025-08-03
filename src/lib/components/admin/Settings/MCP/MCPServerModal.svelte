<script lang="ts">
	import { createEventDispatcher, getContext } from 'svelte';
	import Modal from '$lib/components/common/Modal.svelte';
	import type { MCPServer, MCPServerForm } from '$lib/apis/mcp';
	
	export let server: MCPServer | null = null;
	
	const dispatch = createEventDispatcher();
	const i18n = getContext('i18n');
	
	let formData: MCPServerForm = {
		name: server?.name || '',
		transport_type: server?.transport_type || 'stdio',
		command: server?.command || '',
		url: server?.url || '',
		args: server?.args || [],
		env: server?.env || {},
		enabled: server?.enabled ?? true,
		meta: server?.meta || {}
	};
	
	let newArg = '';
	let newEnvKey = '';
	let newEnvValue = '';
	
	const transportTypes = [
		{ value: 'stdio', label: 'Standard I/O', icon: '🖥️' },
		{ value: 'http', label: 'HTTP', icon: '🌐' },
		{ value: 'websocket', label: 'WebSocket', icon: '🔌' }
	];
	
	const validateForm = (): boolean => {
		// Apenas requer nome preenchido
		return formData.name.trim().length > 0;
	};
	
	const handleSubmit = () => {
		if (!validateForm()) {
			return;
		}
		
		dispatch('save', formData);
	};
	
	const addArgument = () => {
		if (newArg.trim()) {
			formData.args = [...formData.args, newArg.trim()];
			newArg = '';
		}
	};
	
	const removeArgument = (index: number) => {
		formData.args = formData.args.filter((_, i) => i !== index);
	};
	
	const addEnvironmentVariable = () => {
		if (newEnvKey.trim() && newEnvValue.trim()) {
			formData.env = { ...formData.env, [newEnvKey.trim()]: newEnvValue.trim() };
			newEnvKey = '';
			newEnvValue = '';
		}
	};
	
	const removeEnvironmentVariable = (key: string) => {
		const { [key]: _, ...rest } = formData.env;
		formData.env = rest;
	};
</script>

<Modal size="lg" on:close>
	<div class="px-6 py-4">
		<h3 class="text-lg font-semibold mb-4">
			{server ? 'Edit MCP Server' : 'Add MCP Server'}
		</h3>
		
		<div class="space-y-4">
			<!-- Name -->
			<div>
				<label class="block text-sm font-medium mb-1.5" for="name">
					Name <span class="text-red-500">*</span>
				</label>
				<input
					id="name"
					type="text"
					bind:value={formData.name}
					class="w-full px-3 py-2 border rounded-lg dark:border-gray-700 dark:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-primary-500"
					placeholder="My MCP Server"
					required
				/>
			</div>
			
			<!-- Transport Type -->
			<div>
				<label class="block text-sm font-medium mb-1.5" for="transport">
					Transport Type <span class="text-red-500">*</span>
				</label>
				<select
					id="transport"
					bind:value={formData.transport_type}
					class="w-full px-3 py-2 border rounded-lg dark:border-gray-700 dark:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-primary-500"
				>
					{#each transportTypes as type}
						<option value={type.value}>
							{type.icon} {type.label}
						</option>
					{/each}
				</select>
			</div>
			
			<!-- Command (for stdio) -->
			{#if formData.transport_type === 'stdio'}
				<div>
					<label class="block text-sm font-medium mb-1.5" for="command">
						Command <span class="text-red-500">*</span>
					</label>
					<input
						id="command"
						type="text"
						bind:value={formData.command}
						class="w-full px-3 py-2 border rounded-lg dark:border-gray-700 dark:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-primary-500 font-mono text-sm"
						placeholder="npx @modelcontextprotocol/server-filesystem"
						required
					/>
					<div class="text-xs text-gray-500 mt-1">
						The command to run the MCP server
					</div>
				</div>
				
				<!-- Arguments -->
				<div>
					<label class="block text-sm font-medium mb-1.5">
						Arguments
					</label>
					<div class="space-y-2">
						{#each formData.args as arg, index}
							<div class="flex items-center gap-2">
								<input
									type="text"
									value={arg}
									class="flex-1 px-3 py-2 border rounded-lg dark:border-gray-700 dark:bg-gray-800 font-mono text-sm"
									readonly
								/>
								<button
									type="button"
									on:click={() => removeArgument(index)}
									class="p-2 text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
								>
									<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
									</svg>
								</button>
							</div>
						{/each}
						
						<div class="flex items-center gap-2">
							<input
								type="text"
								bind:value={newArg}
								on:keypress={(e) => e.key === 'Enter' && (e.preventDefault(), addArgument())}
								class="flex-1 px-3 py-2 border rounded-lg dark:border-gray-700 dark:bg-gray-800 font-mono text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
								placeholder="Add argument"
							/>
							<button
								type="button"
								on:click={addArgument}
								class="p-2 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg transition-colors"
							>
								<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
								</svg>
							</button>
						</div>
					</div>
				</div>
			{/if}
			
			<!-- URL (for http/websocket) -->
			{#if formData.transport_type === 'http' || formData.transport_type === 'websocket'}
				<div>
					<label class="block text-sm font-medium mb-1.5" for="url">
						URL <span class="text-red-500">*</span>
					</label>
					<input
						id="url"
						type="url"
						bind:value={formData.url}
						class="w-full px-3 py-2 border rounded-lg dark:border-gray-700 dark:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-primary-500 font-mono text-sm"
						placeholder={formData.transport_type === 'http' ? 'https://example.com/mcp' : 'ws://example.com/mcp'}
						required
					/>
					<div class="text-xs text-gray-500 mt-1">
						The URL of the MCP server
					</div>
				</div>
			{/if}
			
			<!-- Environment Variables -->
			<div>
				<label class="block text-sm font-medium mb-1.5">
					Environment Variables
				</label>
				<div class="space-y-2">
					{#each Object.entries(formData.env) as [key, value]}
						<div class="flex items-center gap-2">
							<input
								type="text"
								value={key}
								class="flex-1 px-3 py-2 border rounded-lg dark:border-gray-700 dark:bg-gray-800 font-mono text-sm"
								readonly
							/>
							<input
								type="text"
								value={value}
								class="flex-1 px-3 py-2 border rounded-lg dark:border-gray-700 dark:bg-gray-800 font-mono text-sm"
								readonly
							/>
							<button
								type="button"
								on:click={() => removeEnvironmentVariable(key)}
								class="p-2 text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
							>
								<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
								</svg>
							</button>
						</div>
					{/each}
					
					<div class="flex items-center gap-2">
						<input
							type="text"
							bind:value={newEnvKey}
							on:keypress={(e) => e.key === 'Enter' && e.preventDefault()}
							class="flex-1 px-3 py-2 border rounded-lg dark:border-gray-700 dark:bg-gray-800 font-mono text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
							placeholder="Key"
						/>
						<input
							type="text"
							bind:value={newEnvValue}
							on:keypress={(e) => e.key === 'Enter' && (e.preventDefault(), addEnvironmentVariable())}
							class="flex-1 px-3 py-2 border rounded-lg dark:border-gray-700 dark:bg-gray-800 font-mono text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
							placeholder="Value"
						/>
						<button
							type="button"
							on:click={addEnvironmentVariable}
							class="p-2 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg transition-colors"
						>
							<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
							</svg>
						</button>
					</div>
				</div>
				<div class="text-xs text-gray-500 mt-1">
					Environment variables passed to the MCP server
				</div>
			</div>
			
			<!-- Enabled -->
			<div class="flex items-center gap-3">
				<input
					type="checkbox"
					bind:checked={formData.enabled}
					id="enabled"
					class="w-4 h-4 text-primary-600 bg-gray-100 border-gray-300 rounded focus:ring-primary-500 dark:focus:ring-primary-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600"
				/>
				<label for="enabled" class="text-sm font-medium">
					Enable this server
				</label>
			</div>
		</div>
		
		<div class="flex justify-end gap-2 mt-6">
			<button
				type="button"
				on:click={() => dispatch('close')}
				class="px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
			>
				Cancel
			</button>
			<button
				type="button"
				on:click={handleSubmit}
				class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
			>
				Save Server
			</button>
		</div>
	</div>
</Modal>