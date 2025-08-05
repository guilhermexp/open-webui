<script lang="ts">
	import { onMount } from 'svelte';
	import { WEBUI_API_BASE_URL } from '$lib/constants';
	
	export let url: string;
	
	let loading = true;
	let error = false;
	let metadata = {
		title: '',
		description: '',
		image: '',
		siteName: '',
		favicon: ''
	};
	
	const fetchMetadata = async () => {
		try {
			loading = true;
			error = false;
			
			// Call the backend API to fetch link metadata
			const response = await fetch(`${WEBUI_API_BASE_URL}/utils/link-preview`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					'Authorization': `Bearer ${localStorage.getItem('token')}`
				},
				body: JSON.stringify({ url })
			});
			
			if (!response.ok) {
				throw new Error('Failed to fetch metadata');
			}
			
			const data = await response.json();
			metadata = {
				title: data.title || '',
				description: data.description || '',
				image: data.image || '',
				siteName: data.site_name || '',
				favicon: data.favicon || ''
			};
		} catch (e) {
			console.error('Error fetching link metadata:', e);
			error = true;
		} finally {
			loading = false;
		}
	};
	
	onMount(() => {
		if (url) {
			fetchMetadata();
		}
	});
	
	$: if (url) {
		fetchMetadata();
	}
</script>

{#if !error}
	<a 
		href={url} 
		target="_blank" 
		rel="noopener noreferrer"
		class="block my-2 no-underline"
	>
		<div class="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors">
			{#if loading}
				<!-- Loading skeleton -->
				<div class="p-4">
					<div class="animate-pulse">
						<div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4 mb-2"></div>
						<div class="h-3 bg-gray-200 dark:bg-gray-700 rounded w-full mb-2"></div>
						<div class="h-3 bg-gray-200 dark:bg-gray-700 rounded w-5/6"></div>
					</div>
				</div>
			{:else}
				<!-- Link preview content -->
				{#if metadata.image}
					<div class="aspect-video w-full bg-gray-100 dark:bg-gray-800">
						<img 
							src={metadata.image} 
							alt={metadata.title}
							class="w-full h-full object-cover"
							on:error={(e) => {
								e.target.style.display = 'none';
							}}
						/>
					</div>
				{/if}
				
				<div class="p-4">
					<div class="flex items-start gap-2">
						{#if metadata.favicon}
							<img 
								src={metadata.favicon} 
								alt=""
								class="w-4 h-4 mt-0.5 flex-shrink-0"
								on:error={(e) => {
									e.target.style.display = 'none';
								}}
							/>
						{/if}
						
						<div class="flex-1 min-w-0">
							{#if metadata.siteName}
								<div class="text-xs text-gray-500 dark:text-gray-400 mb-1">
									{metadata.siteName}
								</div>
							{/if}
							
							{#if metadata.title}
								<h3 class="font-medium text-sm text-gray-900 dark:text-gray-100 line-clamp-2 mb-1">
									{metadata.title}
								</h3>
							{/if}
							
							{#if metadata.description}
								<p class="text-xs text-gray-600 dark:text-gray-300 line-clamp-2">
									{metadata.description}
								</p>
							{/if}
							
							<div class="text-xs text-gray-400 dark:text-gray-500 mt-2 truncate">
								{url}
							</div>
						</div>
					</div>
				</div>
			{/if}
		</div>
	</a>
{/if}

<style>
	.line-clamp-2 {
		overflow: hidden;
		display: -webkit-box;
		-webkit-line-clamp: 2;
		-webkit-box-orient: vertical;
	}
</style>