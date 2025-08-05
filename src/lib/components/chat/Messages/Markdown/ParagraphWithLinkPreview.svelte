<script>
	import { onMount } from 'svelte';
	import MarkdownInlineTokens from './MarkdownInlineTokens.svelte';
	import LinkPreview from '../LinkPreview.svelte';
	
	export let id;
	export let tokens = [];
	export let done = true;
	export let onSourceClick = () => {};
	
	let standaloneUrls = [];
	let processedTokens = [];
	
	// Function to check if a text contains a standalone URL
	function extractStandaloneUrls(text) {
		const urlRegex = /^(https?:\/\/[^\s<]+)$/gm;
		const matches = text.match(urlRegex);
		return matches || [];
	}
	
	// Process tokens to find standalone URLs
	$: {
		standaloneUrls = [];
		processedTokens = [];
		
		// Check if the paragraph contains only a URL
		if (tokens.length === 1 && tokens[0].type === 'text') {
			const urls = extractStandaloneUrls(tokens[0].text.trim());
			if (urls.length > 0) {
				standaloneUrls = urls;
			} else {
				processedTokens = tokens;
			}
		} else {
			processedTokens = tokens;
		}
	}
</script>

{#if standaloneUrls.length > 0}
	{#each standaloneUrls as url}
		<LinkPreview {url} />
	{/each}
{:else}
	<p dir="auto">
		<MarkdownInlineTokens
			id={`${id}`}
			tokens={processedTokens}
			{done}
			{onSourceClick}
		/>
	</p>
{/if}