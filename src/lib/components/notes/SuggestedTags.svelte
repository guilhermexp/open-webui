<script lang="ts">
	import { getContext, onMount } from 'svelte';
	import { getSuggestedTagsById, acceptSuggestedTags } from '$lib/apis/notes';
	import { toast } from 'svelte-sonner';
	import Tooltip from '../common/Tooltip.svelte';
	import XMark from '../icons/XMark.svelte';

	const i18n = getContext('i18n');

	export let noteId: string;
	export let onTagsAccepted: () => void = () => {};

	let suggestedTags: string[] = [];
	let selectedTags: Set<string> = new Set();
	let showSuggestions = false;
	let loading = false;

	const loadSuggestedTags = async () => {
		loading = true;
		try {
			const tags = await getSuggestedTagsById(localStorage.token, noteId);
			suggestedTags = tags || [];
			if (suggestedTags.length > 0) {
				showSuggestions = true;
				// Auto-select all suggested tags by default
				selectedTags = new Set(suggestedTags);
			}
		} catch (error) {
			console.error('Error loading suggested tags:', error);
		}
		loading = false;
	};

	const toggleTag = (tag: string) => {
		if (selectedTags.has(tag)) {
			selectedTags.delete(tag);
		} else {
			selectedTags.add(tag);
		}
		selectedTags = selectedTags;
	};

	const acceptTags = async () => {
		if (selectedTags.size === 0) {
			showSuggestions = false;
			return;
		}

		loading = true;
		try {
			await acceptSuggestedTags(localStorage.token, noteId, Array.from(selectedTags));
			toast.success($i18n.t('Tags added successfully'));
			showSuggestions = false;
			suggestedTags = [];
			selectedTags.clear();
			onTagsAccepted();
		} catch (error) {
			toast.error($i18n.t('Failed to add tags'));
			console.error('Error accepting tags:', error);
		}
		loading = false;
	};

	const dismissTag = (tag: string) => {
		selectedTags.delete(tag);
		selectedTags = selectedTags;
		
		if (selectedTags.size === 0) {
			showSuggestions = false;
			suggestedTags = [];
		}
	};

	const acceptSingleTag = async (tag: string) => {
		loading = true;
		try {
			await acceptSuggestedTags(localStorage.token, noteId, [tag]);
			toast.success($i18n.t('Tag added successfully'));
			
			// Remove this tag from suggestions
			suggestedTags = suggestedTags.filter(t => t !== tag);
			selectedTags.delete(tag);
			selectedTags = selectedTags;
			
			if (suggestedTags.length === 0) {
				showSuggestions = false;
			}
			
			onTagsAccepted();
		} catch (error) {
			toast.error($i18n.t('Failed to add tag'));
			console.error('Error accepting tag:', error);
		}
		loading = false;
	};

	onMount(() => {
		loadSuggestedTags();
	});
</script>

{#if showSuggestions && suggestedTags.length > 0}
	<div class="mt-2 mb-3">
		<div class="flex items-center gap-1 mb-2">
			<span class="text-xs text-gray-500 dark:text-gray-400 font-medium">
				{$i18n.t('Suggested Tags')}:
			</span>
		</div>
		<ul class="flex flex-row flex-wrap gap-1 line-clamp-1">
			{#each suggestedTags as tag}
				{#if selectedTags.has(tag)}
					<Tooltip content={$i18n.t('Click to add this tag')}>
						<li
							class="relative group/tags px-1.5 py-[0.2px] gap-0.5 flex justify-between h-fit max-h-fit w-fit items-center rounded-full bg-blue-500/20 text-blue-700 dark:text-blue-300 transition cursor-pointer hover:bg-blue-500/30"
						>
							<button
								class="text-[0.7rem] font-medium self-center line-clamp-1 w-fit"
								on:click={() => acceptSingleTag(tag)}
								disabled={loading}
							>
								{tag}
							</button>
							<div class="absolute invisible right-0.5 group-hover/tags:visible transition">
								<button
									class="rounded-full border bg-white dark:bg-gray-700 h-full flex self-center cursor-pointer"
									on:click={() => dismissTag(tag)}
									type="button"
									aria-label={$i18n.t('Remove this suggestion')}
									disabled={loading}
								>
									<XMark className="size-3" strokeWidth="2.5" />
								</button>
							</div>
						</li>
					</Tooltip>
				{/if}
			{/each}
		</ul>
	</div>
{/if}