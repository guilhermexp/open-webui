<script lang="ts">
	import Fuse from 'fuse.js';
	import Bolt from '$lib/components/icons/Bolt.svelte';
	import { onMount, getContext } from 'svelte';
	import { settings, WEBUI_NAME } from '$lib/stores';
	import { WEBUI_VERSION } from '$lib/constants';

	const i18n = getContext('i18n');

	export let suggestionPrompts = [];
	export let className = '';
	export let inputValue = '';
	export let onSelect = (e) => {};

	let sortedPrompts = [];

	const fuseOptions = {
		keys: ['content', 'title'],
		threshold: 0.5
	};

	let fuse;
	let filteredPrompts = [];

	// Initialize Fuse
	$: fuse = new Fuse(sortedPrompts, fuseOptions);

	// Update the filteredPrompts if inputValue changes
	// Only increase version if something wirklich geändert hat
	$: getFilteredPrompts(inputValue);

	// Helper function to check if arrays are the same
	// (based on unique IDs oder content)
	function arraysEqual(a, b) {
		if (a.length !== b.length) return false;
		for (let i = 0; i < a.length; i++) {
			if ((a[i].id ?? a[i].content) !== (b[i].id ?? b[i].content)) {
				return false;
			}
		}
		return true;
	}

	const getFilteredPrompts = (inputValue) => {
		if (inputValue.length > 500) {
			filteredPrompts = [];
		} else {
			const newFilteredPrompts =
				inputValue.trim() && fuse
					? fuse.search(inputValue.trim()).map((result) => result.item)
					: sortedPrompts;

			// Compare with the oldFilteredPrompts
			// If there's a difference, update array + version
			if (!arraysEqual(filteredPrompts, newFilteredPrompts)) {
				filteredPrompts = newFilteredPrompts;
			}
		}
	};

	$: if (suggestionPrompts) {
		// Se não houver prompts, use os padrão
		const defaultPrompts = [
			{ title: ['Show me a code snippet'], content: 'Show me a code snippet example', icon: 'camera' },
			{ title: ['Overcome procrastination'], content: 'Help me overcome procrastination and be more productive', icon: 'target' },
			{ title: ['Explain options trading'], content: 'Explain the basics of options trading', icon: 'users' }
		];
		
		sortedPrompts = suggestionPrompts.length > 0 
			? [...(suggestionPrompts ?? [])].sort(() => Math.random() - 0.5)
			: defaultPrompts;
		getFilteredPrompts(inputValue);
	}
</script>

<div class="w-full">
	{#if filteredPrompts.length > 0}
		<div role="list" class="flex flex-wrap gap-3 justify-center {className}">
			{#each filteredPrompts.slice(0, 3) as prompt, idx (prompt.id || prompt.content)}
				<button
					role="listitem"
					class="flex items-center gap-2.5 px-4 py-2.5 rounded-full bg-gray-50 dark:bg-gray-800 
					       border border-gray-200 dark:border-gray-700 hover:bg-white dark:hover:bg-gray-750
					       transition-all duration-200 text-sm font-medium"
					on:click={() => onSelect({ type: 'prompt', data: prompt.content })}
				>
					<div class="w-4 h-4">
						{#if prompt.icon === 'camera' || idx === 0}
							<!-- Ícone verde para "Show me a code snippet" -->
							<div class="w-full h-full border-2 border-green-500 rounded-full flex items-center justify-center">
								<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" class="w-2.5 h-2.5 text-green-500">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
								</svg>
							</div>
						{:else if prompt.icon === 'target' || idx === 1}
							<!-- Ícone rosa para "Overcome procrastination" -->
							<div class="w-full h-full border-2 border-pink-500 rounded-full flex items-center justify-center">
								<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" class="w-2.5 h-2.5 text-pink-500">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
								</svg>
							</div>
						{:else}
							<!-- Ícone amarelo para "Explain options trading" -->
							<div class="w-full h-full border-2 border-yellow-500 rounded-full flex items-center justify-center">
								<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" class="w-2.5 h-2.5 text-yellow-500">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
								</svg>
							</div>
						{/if}
					</div>
					<span class="text-gray-700 dark:text-gray-300">
						{#if prompt.title && prompt.title[0] !== ''}
							{prompt.title[0]}
						{:else}
							{prompt.content.substring(0, 30)}{prompt.content.length > 30 ? '...' : ''}
						{/if}
					</span>
				</button>
			{/each}
		</div>
	{/if}
</div>

<style>
	/* Waterfall animation for the suggestions */
	@keyframes fadeInUp {
		0% {
			opacity: 0;
			transform: translateY(20px);
		}
		100% {
			opacity: 1;
			transform: translateY(0);
		}
	}

	.waterfall {
		opacity: 0;
		animation-name: fadeInUp;
		animation-duration: 200ms;
		animation-fill-mode: forwards;
		animation-timing-function: ease;
	}
</style>
