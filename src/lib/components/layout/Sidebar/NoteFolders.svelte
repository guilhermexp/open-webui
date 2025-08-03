<script lang="ts">
	import { createEventDispatcher, getContext } from 'svelte';
	import { toast } from 'svelte-sonner';
	const i18n = getContext('i18n');

	import NoteFolderItem from './NoteFolders/NoteFolderItem.svelte';
	import NoteFolderModal from './NoteFolders/NoteFolderModal.svelte';
	import { deleteNoteFolderById, updateNoteFolderById } from '$lib/apis/note-folders';

	export let folders = {};
	export let shiftKey = false;

	export let onDelete = () => {};

	const dispatch = createEventDispatcher();

	let selectedFolderId = null;
	let selectedFolder = null;

	let showEdit = false;
	let showFolderModal = false;

	const editFolderHandler = async (folder) => {
		console.log('editFolderHandler', folder);

		const res = await updateNoteFolderById(localStorage.token, folder.id, {
			name: folder.name,
			data: folder.data ?? {}
		}).catch((error) => {
			toast.error(`${error}`);
			return null;
		});

		if (res) {
			dispatch('update');
		}
	};

	const deleteHandler = async (folderId) => {
		const res = await deleteNoteFolderById(localStorage.token, folderId).catch((error) => {
			toast.error(`${error}`);
			return null;
		});

		if (res) {
			onDelete(folderId);
		}
	};
</script>

<NoteFolderModal
	bind:show={showFolderModal}
	edit={showEdit}
	folder={selectedFolder}
	onSubmit={async (folder) => {
		await editFolderHandler(folder);
		showFolderModal = false;
	}}
/>

<div class="flex flex-col">
	{#each Object.values(folders).filter((f) => f.parent_id === null) as folder (folder.id)}
		<NoteFolderItem
			{folder}
			{folders}
			{shiftKey}
			selected={selectedFolderId === folder.id}
			on:select={() => {
				selectedFolderId = folder.id;
			}}
			on:unselect={() => {
				selectedFolderId = null;
			}}
			on:change={async () => {
				dispatch('change');
			}}
			on:update={() => {
				dispatch('update');
			}}
			on:click={(e) => {
				dispatch('click', e.detail);
			}}
			on:import={(e) => {
				dispatch('import', e.detail);
			}}
			on:delete={(e) => {
				deleteHandler(e.detail);
			}}
			on:edit={(e) => {
				selectedFolder = e.detail;
				showEdit = true;
				showFolderModal = true;
			}}
		/>
	{/each}
</div>