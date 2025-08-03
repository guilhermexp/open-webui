<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import { WEBUI_API_BASE_URL } from '$lib/constants';
	import Modal from '$lib/components/common/Modal.svelte';
	import Bolt from '$lib/components/icons/Bolt.svelte';
	import GlobeAlt from '$lib/components/icons/GlobeAlt.svelte';

	export let show = false;

	const dispatch = createEventDispatcher();

	let step = 1;
	let connectionType: 'http' | 'sse' = 'http';
	let connectionName = '';
	let connectionUrl = '';
	let selectedTools: string[] = [];
	let availableTools: any[] = [];
	let loading = false;
	let error = '';

	// Reset form when modal opens
	$: if (show) {
		step = 1;
		connectionType = 'http';
		connectionName = '';
		connectionUrl = '';
		selectedTools = [];
		availableTools = [];
		error = '';
	}

	async function testConnection() {
		if (!connectionUrl || !connectionName) {
			error = 'Please fill in all required fields';
			return;
		}

		loading = true;
		error = '';

		try {
			// Test the connection and get available tools
			const response = await fetch(`${WEBUI_API_BASE_URL}/mcp/test-custom`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					Authorization: `Bearer ${localStorage.token}`
				},
				body: JSON.stringify({
					type: connectionType,
					config: {
						url: connectionUrl
					}
				})
			});

			if (!response.ok) {
				throw new Error('Failed to connect to MCP server');
			}

			const data = await response.json();
			availableTools = data.tools || [];
			
			// Auto-select all tools initially
			selectedTools = availableTools.map(tool => tool.name);
			
			// Move to step 2
			step = 2;
		} catch (err) {
			error = err.message || 'Connection failed';
		} finally {
			loading = false;
		}
	}

	function handleSave() {
		if (selectedTools.length === 0) {
			error = 'Please select at least one tool';
			return;
		}

		dispatch('save', {
			name: connectionName,
			transport_type: connectionType,
			url: connectionUrl,
			enabledTools: selectedTools,
			isCustom: true,
			customType: connectionType
		});

		dispatch('close');
	}

	function handleClose() {
		dispatch('close');
	}
</script>

<Modal bind:show size="md">
	<div class="px-6 py-4">
		<div class="flex items-center gap-3 mb-4">
			<div class="w-12 h-12 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center">
				<Bolt className="w-6 h-6 text-gray-600 dark:text-gray-400" />
			</div>
			<div>
				<h3 class="text-lg font-semibold">Connect New Service</h3>
				<p class="text-sm text-gray-600 dark:text-gray-400">
					Connect to external services to expand your capabilities with new tools and integrations.
				</p>
			</div>
		</div>

		<!-- Step indicator -->
		<div class="flex items-center gap-4 mb-6">
			<div class="flex items-center gap-2">
				<div class="w-8 h-8 rounded-full bg-black text-white flex items-center justify-center text-sm font-medium">
					1
				</div>
				<span class="text-sm font-medium {step === 1 ? 'text-gray-900 dark:text-white' : 'text-gray-500 dark:text-gray-400'}">
					Setup Connection
				</span>
			</div>
			<div class="h-px flex-1 bg-gray-200 dark:bg-gray-700"></div>
			<div class="flex items-center gap-2">
				<div class="w-8 h-8 rounded-full {step === 2 ? 'bg-black text-white' : 'bg-gray-200 dark:bg-gray-700 text-gray-500'} flex items-center justify-center text-sm font-medium">
					2
				</div>
				<span class="text-sm font-medium {step === 2 ? 'text-gray-900 dark:text-white' : 'text-gray-500 dark:text-gray-400'}">
					Select Tools
				</span>
			</div>
		</div>

		{#if error}
			<div class="mb-4 p-3 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 rounded-lg text-sm">
				{error}
			</div>
		{/if}

		{#if step === 1}
			<!-- Step 1: Setup Connection -->
			<div class="space-y-4">
				<div>
					<label class="block text-sm font-medium mb-2">How would you like to connect?</label>
					<div class="grid grid-cols-2 gap-3">
						<button
							on:click={() => connectionType = 'http'}
							class="p-4 border-2 rounded-lg text-left transition-all {connectionType === 'http' 
								? 'border-primary-600 bg-primary-50 dark:bg-primary-900/20' 
								: 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'}"
						>
							<div class="flex items-center gap-3">
								<div class="w-8 h-8 rounded-full bg-gray-100 dark:bg-gray-800 flex items-center justify-center">
									<Bolt className="w-4 h-4" />
								</div>
								<span class="font-medium">Streamable HTTP</span>
							</div>
						</button>
						<button
							on:click={() => connectionType = 'sse'}
							class="p-4 border-2 rounded-lg text-left transition-all {connectionType === 'sse' 
								? 'border-primary-600 bg-primary-50 dark:bg-primary-900/20' 
								: 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'}"
						>
							<div class="flex items-center gap-3">
								<div class="w-8 h-8 rounded-full bg-gray-100 dark:bg-gray-800 flex items-center justify-center">
									<GlobeAlt className="w-4 h-4" />
								</div>
								<span class="font-medium">SSE (Server-Sent Events)</span>
							</div>
						</button>
					</div>
				</div>

				<div>
					<label for="connection-name" class="block text-sm font-medium mb-1.5">
						Connection Name
					</label>
					<input
						id="connection-name"
						type="text"
						bind:value={connectionName}
						placeholder="e.g., Gmail, Slack, Customer Support Tools"
						class="w-full px-3 py-2 border rounded-lg dark:border-gray-700 dark:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-primary-500"
					/>
					<p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
						Give this connection a memorable name
					</p>
				</div>

				<div>
					<label for="connection-url" class="block text-sm font-medium mb-1.5">
						Connection URL
					</label>
					<input
						id="connection-url"
						type="url"
						bind:value={connectionUrl}
						placeholder="https://server.example.com/mcp"
						class="w-full px-3 py-2 border rounded-lg dark:border-gray-700 dark:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-primary-500"
					/>
					<p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
						Paste the complete connection URL provided by your service
					</p>
				</div>
			</div>

			<div class="flex justify-end gap-3 mt-6">
				<button
					on:click={handleClose}
					class="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
				>
					Cancel
				</button>
				<button
					on:click={testConnection}
					disabled={loading || !connectionUrl || !connectionName}
					class="px-4 py-2 bg-gray-800 dark:bg-gray-700 text-white rounded-lg hover:bg-gray-900 dark:hover:bg-gray-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
				>
					{#if loading}
						<div class="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
					{:else}
						<Bolt className="w-4 h-4" />
					{/if}
					Connect
				</button>
			</div>
		{:else}
			<!-- Step 2: Select Tools -->
			<div class="space-y-4">
				<div>
					<h4 class="font-medium mb-2">Available Tools</h4>
					<p class="text-sm text-gray-600 dark:text-gray-400 mb-4">
						Select the tools you want to enable for this connection
					</p>
					
					{#if availableTools.length > 0}
						<div class="space-y-2 max-h-96 overflow-y-auto">
							{#each availableTools as tool}
								<label class="flex items-start gap-3 p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 cursor-pointer">
									<input
										type="checkbox"
										value={tool.name}
										checked={selectedTools.includes(tool.name)}
										on:change={(e) => {
											if (e.target.checked) {
												selectedTools = [...selectedTools, tool.name];
											} else {
												selectedTools = selectedTools.filter(t => t !== tool.name);
											}
										}}
										class="mt-1"
									/>
									<div class="flex-1">
										<div class="font-medium text-sm">{tool.name}</div>
										{#if tool.description}
											<div class="text-xs text-gray-600 dark:text-gray-400 mt-0.5">
												{tool.description}
											</div>
										{/if}
									</div>
								</label>
							{/each}
						</div>
					{:else}
						<div class="text-center py-8 text-gray-500 dark:text-gray-400">
							No tools found
						</div>
					{/if}
				</div>
			</div>

			<div class="flex justify-between mt-6">
				<button
					on:click={() => step = 1}
					class="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
				>
					Back
				</button>
				<div class="flex gap-3">
					<button
						on:click={handleClose}
						class="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
					>
						Cancel
					</button>
					<button
						on:click={handleSave}
						disabled={selectedTools.length === 0}
						class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
					>
						Save Connection
					</button>
				</div>
			</div>
		{/if}
	</div>
</Modal>