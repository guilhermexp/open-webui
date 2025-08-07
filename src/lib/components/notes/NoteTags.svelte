<script>
	import {
		addTagById,
		deleteTagById,
		getTagsById,
		updateNoteById
	} from '$lib/apis/notes';
	import {
		getAllTags
	} from '$lib/apis/chats';
	import {
		tags as _tags
	} from '$lib/stores';
	import { createEventDispatcher, onMount } from 'svelte';

	const dispatch = createEventDispatcher();

	import Tags from '../common/Tags.svelte';
	import { toast } from 'svelte-sonner';

	export let noteId = '';
	let tags = [];

	const getTags = async () => {
		return await getTagsById(localStorage.token, noteId).catch(async (error) => {
			return [];
		});
	};

	const addTag = async (tagName) => {
		const res = await addTagById(localStorage.token, noteId, tagName).catch(async (error) => {
			toast.error(`${error}`);
			return null;
		});
		if (!res) {
			return;
		}

		tags = await getTags();
		
		// Update the global tags store
		await _tags.set(await getAllTags(localStorage.token));
		dispatch('add', {
			name: tagName
		});
	};

	const deleteTag = async (tagName) => {
		const res = await deleteTagById(localStorage.token, noteId, tagName);
		tags = await getTags();
		
		// Update the global tags store
		await _tags.set(await getAllTags(localStorage.token));
		dispatch('delete', {
			name: tagName
		});
	};

	onMount(async () => {
		if (noteId) {
			tags = await getTags();
		}
	});
</script>

<Tags
	{tags}
	on:delete={(e) => {
		deleteTag(e.detail);
	}}
	on:add={(e) => {
		addTag(e.detail);
	}}
/>