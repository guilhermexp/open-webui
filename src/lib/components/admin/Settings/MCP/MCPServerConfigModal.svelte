<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import Modal from '$lib/components/common/Modal.svelte';
	import Spinner from '$lib/components/common/Spinner.svelte';
	import FloppyDisk from '$lib/components/icons/FloppyDisk.svelte';

	export let server: any;

	const dispatch = createEventDispatcher();

	let config: Record<string, string> = {};
	let loading = false;
	let error = '';

	// Initialize config based on server's configSchema
	$: if (server?.configSchema?.properties) {
		Object.keys(server.configSchema.properties).forEach(key => {
			if (!config[key]) {
				config[key] = '';
			}
		});
	}

	function handleSave() {
		// Validate required fields
		if (server.configSchema?.required) {
			for (const field of server.configSchema.required) {
				if (!config[field]) {
					error = `${server.configSchema.properties[field].title} is required`;
					return;
				}
			}
		}

		dispatch('save', config);
		dispatch('close');
	}

	function handleClose() {
		dispatch('close');
	}
</script>

<Modal show={true} size="md">
	<div class="px-6 py-4">
		<div class="flex items-center gap-3 mb-4">
			{#if server.iconUrl}
				<img src={server.iconUrl} alt={server.displayName} class="w-12 h-12 rounded-lg" />
			{:else}
				<div class="w-12 h-12 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center">
					<span class="text-xl">🔧</span>
				</div>
			{/if}
			<div>
				<h3 class="text-lg font-semibold">{server.displayName}</h3>
				<p class="text-sm text-gray-600 dark:text-gray-400">{server.description}</p>
			</div>
		</div>

		{#if error}
			<div class="mb-4 p-3 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 rounded-lg text-sm">
				{error}
			</div>
		{/if}

		<div class="space-y-4">
			<h4 class="font-medium">Configuration</h4>
			
			{#if server.configSchema?.properties}
				{#each Object.entries(server.configSchema.properties) as [key, schema]}
					<div>
						<label for={key} class="block text-sm font-medium mb-1.5">
							{schema.title}
							{#if server.configSchema.required?.includes(key)}
								<span class="text-red-500">*</span>
							{/if}
						</label>
						{#if schema.format === 'password'}
							<input
								id={key}
								type="password"
								bind:value={config[key]}
								placeholder={schema.description}
								class="w-full px-3 py-2 border rounded-lg dark:border-gray-700 dark:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-primary-500"
							/>
						{:else}
							<input
								id={key}
								type="text"
								bind:value={config[key]}
								placeholder={schema.description}
								class="w-full px-3 py-2 border rounded-lg dark:border-gray-700 dark:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-primary-500"
							/>
						{/if}
						{#if schema.description}
							<p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
								{schema.description}
							</p>
						{/if}
					</div>
				{/each}
			{:else}
				<p class="text-sm text-gray-600 dark:text-gray-400">
					No configuration required for this server.
				</p>
			{/if}
		</div>

		<div class="flex justify-end gap-3 mt-6">
			<button
				on:click={handleClose}
				class="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
			>
				Cancel
			</button>
			<button
				on:click={handleSave}
				disabled={loading}
				class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
			>
				{#if loading}
					<Spinner className="w-4 h-4" />
				{:else}
					<FloppyDisk className="w-4 h-4" />
				{/if}
				Save Configuration
			</button>
		</div>
	</div>
</Modal>