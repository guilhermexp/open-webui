<script lang="ts">
	import { toast } from 'svelte-sonner';
	import { goto } from '$app/navigation';
	import {
		user,
		showSidebar,
		mobile,
		config
	} from '$lib/stores';
	import { onMount, getContext } from 'svelte';

	const i18n = getContext('i18n');

	import { createNewNoteFolder, getNoteFolders } from '$lib/apis/note-folders';
	import { WEBUI_BASE_URL } from '$lib/constants';

	import UserMenu from './Sidebar/UserMenu.svelte';
	import NoteFolders from './Sidebar/NoteFolders.svelte';
	import NoteFolderModal from './Sidebar/NoteFolders/NoteFolderModal.svelte';
	import Spinner from '../common/Spinner.svelte';

	let loaded = false;
	let noteFolders = [];
	let showCreateFolderModal = false;

	const init = async () => {
		noteFolders = await getNoteFolders(localStorage.token);
		loaded = true;
	};

	const createFolderHandler = async (folder) => {
		const res = await createNewNoteFolder(localStorage.token, folder).catch((error) => {
			toast.error(`${error}`);
			return null;
		});
		
		if (res) {
			await init();
		}
	};

	onMount(async () => {
		if ($user !== undefined) {
			await init();
		}
	});

	$: if (loaded && $user !== undefined) {
		// Recarregar pastas se necessário
	}
</script>

<div
	class="h-screen max-h-[100dvh] min-h-96 select-none {$showSidebar
		? 'lg:relative w-[260px]'
		: '-translate-x-[260px] w-[260px]'} bg-gray-50 text-gray-700 dark:bg-gray-850 dark:text-gray-100 text-sm transition fixed z-50 top-0 left-0 lg:sticky lg:top-0 flex flex-col justify-between"
>
	<div class="px-2.5 pt-2.5 pb-2 flex justify-between space-x-1">
		<a
			class="flex-grow flex items-center justify-center bg-gray-100 hover:bg-gray-200 dark:bg-gray-800 dark:hover:bg-gray-700 transition rounded-xl px-3 py-2"
			href="/notes"
		>
			<div class="flex items-center gap-2">
				<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-4">
					<path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
				</svg>
				<div class="text-sm font-medium">{$i18n.t('Notes')}</div>
			</div>
		</a>
	</div>

	<div class="px-2.5 flex-1 flex flex-col space-y-1 overflow-y-auto scrollbar-hidden">
		{#if loaded}
			<div class="flex flex-col space-y-1">
				<div class="flex items-center justify-between px-3 py-2">
					<div class="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
						{$i18n.t('Folders')}
					</div>
					<button
						class="text-xs text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200"
						on:click={() => {
							showCreateFolderModal = true;
						}}
					>
						<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-4">
							<path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
						</svg>
					</button>
				</div>

				{#if noteFolders.length > 0}
					<NoteFolders
						folders={noteFolders}
						onDelete={() => {
							init();
						}}
					/>
				{:else}
					<div class="px-3 py-2 text-xs text-gray-500 dark:text-gray-400">
						{$i18n.t('No folders')}
					</div>
				{/if}
			</div>
		{:else}
			<div class="flex justify-center items-center h-full">
				<Spinner className="size-4" />
			</div>
		{/if}
	</div>

	<div class="px-2.5 pb-2">
		{#if $user !== undefined && $user !== null}
			<UserMenu
				className="w-full"
				role={$user?.role}
				help={false}
			>
				<button
					class="select-none flex rounded-xl p-2.5 w-full hover:bg-gray-100 dark:hover:bg-gray-850 transition"
					aria-label="User Menu"
				>
					<div class="flex items-center gap-3">
						<img
							src={$user?.profile_image_url}
							class="size-6 object-cover rounded-full"
							alt="User profile"
							draggable="false"
						/>
						<div class="text-left">
							<div class="font-medium line-clamp-1">{$user?.name}</div>
							<div class="text-xs text-gray-500 dark:text-gray-400 line-clamp-1">{$user?.email}</div>
						</div>
					</div>
				</button>
			</UserMenu>
		{/if}
	</div>
</div>

<NoteFolderModal
	bind:show={showCreateFolderModal}
	onSubmit={createFolderHandler}
/>