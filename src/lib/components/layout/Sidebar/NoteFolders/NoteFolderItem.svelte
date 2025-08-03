<script lang="ts">
	import { createEventDispatcher, getContext } from 'svelte';
	import { getNotes, updateNoteFolderIdById } from '$lib/apis/notes';
	import { updateNoteFolderIsExpandedById } from '$lib/apis/note-folders';
	import { toast } from 'svelte-sonner';
	import { goto } from '$app/navigation';
	import { DropdownMenu } from 'bits-ui';
	import { fade } from 'svelte/transition';

	const i18n = getContext('i18n');
	const dispatch = createEventDispatcher();

	import Folder from '$lib/components/common/Folder.svelte';
	import Tooltip from '$lib/components/common/Tooltip.svelte';
	import Dropdown from '$lib/components/common/Dropdown.svelte';
	import { flyAndScale } from '$lib/utils/transitions';

	import ChevronDown from '$lib/components/icons/ChevronDown.svelte';
	import ChevronUp from '$lib/components/icons/ChevronUp.svelte';
	import EllipsisHorizontal from '$lib/components/icons/EllipsisHorizontal.svelte';
	import Pencil from '$lib/components/icons/Pencil.svelte';
	import GarbageBin from '$lib/components/icons/GarbageBin.svelte';

	export let folder;
	export let folders = {};
	export let shiftKey = false;
	export let selected = false;

	const onNoteImport = (e) => {
		dispatch('import', {
			folderId: folder.id,
			items: e.detail
		});
	};

	const onDrop = async (e) => {
		const { type, id } = e.detail;

		if (type === 'note') {
			const res = await updateNoteFolderIdById(localStorage.token, id, folder.id).catch(
				(error) => {
					toast.error(`${error}`);
					return null;
				}
			);

			if (res) {
				dispatch('change');
			}
		} else if (type === 'folder') {
			// Handle folder drag and drop
			dispatch('update');
		}
	};

	const toggleExpanded = async () => {
		folder.is_expanded = !folder.is_expanded;
		await updateNoteFolderIsExpandedById(
			localStorage.token,
			folder.id,
			folder.is_expanded
		).catch((error) => {
			toast.error(`${error}`);
		});
	};
</script>

<Folder
	name={folder.name}
	open={folder.is_expanded}
	className=""
	on:import={onNoteImport}
	on:drop={onDrop}
	on:change={toggleExpanded}
	on:click={() => {
		dispatch('click', folder);
		goto(`/notes?folder=${folder.id}`);
	}}
	on:select={() => {
		dispatch('select');
	}}
	on:unselect={() => {
		dispatch('unselect');
	}}
	type="folder"
	id={folder.id}
	{selected}
	{shiftKey}
	importPlaceholder={$i18n.t('Drop notes here to add to folder')}
	dragAndDrop={true}
>
	<div slot="actions" class="invisible group-hover:visible">
		<Dropdown let:show>
			<button
				class="self-center w-fit text-sm p-1 dark:text-gray-300 dark:hover:text-white hover:bg-black/5 dark:hover:bg-white/5 rounded-lg transition"
				type="button"
			>
				<EllipsisHorizontal className="size-3.5" />
			</button>
			
			<div slot="content">
				<DropdownMenu.Content
					class="w-full max-w-[180px] text-sm rounded-xl px-1 py-1.5 z-50 bg-white dark:bg-gray-850 dark:text-white shadow-lg font-primary"
					sideOffset={6}
					side="bottom"
					align="end"
					transition={flyAndScale}
				>
					<DropdownMenu.Item
						class="flex gap-2 items-center px-3 py-2 text-sm cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800 rounded-md"
						on:click={() => {
							dispatch('edit', folder);
							show = false;
						}}
					>
						<Pencil strokeWidth="2" className="size-4" />
						<div class="flex items-center">{$i18n.t('Edit')}</div>
					</DropdownMenu.Item>
					
					<DropdownMenu.Item
						class="flex gap-2 items-center px-3 py-2 text-sm cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800 rounded-md"
						on:click={() => {
							if (confirm($i18n.t('Are you sure you want to delete this folder?'))) {
								dispatch('delete', folder.id);
							}
							show = false;
						}}
					>
						<GarbageBin strokeWidth="2" className="size-4" />
						<div class="flex items-center">{$i18n.t('Delete')}</div>
					</DropdownMenu.Item>
				</DropdownMenu.Content>
			</div>
		</Dropdown>
	</div>

	<div slot="content">
		{#if folders[folder.id]?.childrenIds}
			<div class="ml-3 pl-1 flex flex-col overflow-y-auto scrollbar-hidden">
				{#each folders[folder.id].childrenIds as childId}
					{#if folders[childId]}
						<svelte:self
							folder={folders[childId]}
							{folders}
							{shiftKey}
							on:select
							on:unselect
							on:change
							on:update
							on:click
							on:import
							on:delete
							on:edit
						/>
					{/if}
				{/each}
			</div>
		{/if}
	</div>
</Folder>