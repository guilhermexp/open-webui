<script lang="ts">
	import { toast } from 'svelte-sonner';
	import { getContext, onDestroy, onMount, tick } from 'svelte';
	const i18n = getContext('i18n');

	import Modal from '$lib/components/common/Modal.svelte';
	import SearchNotesInput from './SearchNotesInput.svelte';
	import { getNoteById, getNoteList, getNoteListBySearchText } from '$lib/apis/notes';
	import Spinner from '../common/Spinner.svelte';

	import dayjs from '$lib/dayjs';
	import calendar from 'dayjs/plugin/calendar';
	import Loader from '../common/Loader.svelte';
	import { user } from '$lib/stores';
	dayjs.extend(calendar);

	export let show = false;
	export let onClose = () => {};

	let query = '';
	let page = 1;

	let noteList = null;

	let noteListLoading = false;
	let allNotesLoaded = false;

	let searchDebounceTimeout;

	let selectedIdx = 0;

	let selectedNote = null;

	const searchHandler = async () => {
		if (searchDebounceTimeout) {
			clearTimeout(searchDebounceTimeout);
		}

		page = 1;
		noteList = null;
		if (query === '') {
			noteList = await getNoteList(localStorage.token);
		} else {
			searchDebounceTimeout = setTimeout(async () => {
				noteList = await getNoteListBySearchText(localStorage.token, query, page);
			}, 500);
		}

		selectedNote = null;

		if ((noteList ?? []).length === 0) {
			allNotesLoaded = true;
		} else {
			allNotesLoaded = false;
		}
	};

	const loadMoreNotes = async () => {
		noteListLoading = true;
		page += 1;

		let newNoteList = [];

		if (query) {
			newNoteList = await getNoteListBySearchText(localStorage.token, query, page);
		} else {
			newNoteList = await getNoteList(localStorage.token);
		}

		// once the bottom of the list has been reached (no results) there is no need to continue querying
		allNotesLoaded = newNoteList.length === 0;

		if (newNoteList.length > 0) {
			noteList = [...noteList, ...newNoteList];
		}

		noteListLoading = false;
	};

	const init = () => {
		searchHandler();
	};

	const onKeyDown = (e) => {
		if (e.code === 'Escape') {
			show = false;
			onClose();
		} else if (e.code === 'Enter' && (noteList ?? []).length > 0) {
			const item = document.querySelector(`[data-arrow-selected="true"]`);
			if (item) {
				item?.click();
			}
		} else if (e.code === 'ArrowDown') {
			e.preventDefault();
			selectedIdx = Math.min((noteList ?? []).length - 1, selectedIdx + 1);
		} else if (e.code === 'ArrowUp') {
			e.preventDefault();
			selectedIdx = Math.max(0, selectedIdx - 1);
		}
	};

	onMount(() => {
		window.addEventListener('keydown', onKeyDown);
		init();
	});

	onDestroy(() => {
		window.removeEventListener('keydown', onKeyDown);
	});
</script>

<Modal bind:show size="4xl">
	<div slot="title" class="px-1 flex gap-2.5 items-center w-full">
		<div class="flex-1">
			<SearchNotesInput
				placeholder={$i18n.t('Search Notes')}
				bind:value={query}
				showClearButton={true}
				on:input={() => {
					searchHandler();
					selectedIdx = 0;
				}}
			/>
		</div>
	</div>
	<div class="px-6 flex flex-col w-full h-[68vh] max-h-[100dvh]">
		<div
			class="flex flex-col flex-1 h-full max-h-full rounded-lg {(noteList ?? []).length > 0
				? ''
				: 'justify-center'}"
		>
			{#if noteList !== null}
				{#if noteList.length > 0}
					<div class="flex overflow-y-auto h-full max-h-full mb-3">
						<div class="text-sm w-full h-full max-h-full">
							<div class="h-full max-h-full">
								{#each noteList as note, idx}
									<div
										data-arrow-selected={idx === selectedIdx}
										class="rounded-lg w-full transition hover:bg-gray-50 dark:hover:bg-gray-850 {idx ===
										selectedIdx
											? 'bg-gray-50 dark:bg-gray-850'
											: ''}"
									>
										<button
											class="flex justify-between px-5 py-3 w-full"
											on:click={() => {
												show = false;
												window.location.href = `/notes/${note.id}`;
											}}
										>
											<div class="flex flex-col justify-start w-full text-left">
												<div class="font-medium dark:text-gray-300 flex items-center">
													{note.title}
												</div>

												<div class="flex text-xs dark:text-gray-500 mt-1">
													{dayjs(note.updated_at / 1000000).fromNow()}
												</div>
											</div>
										</button>
									</div>
								{/each}

								<div class="">
									{#if !allNotesLoaded}
										<Loader
											on:visible={(e) => {
												console.log('visible');
												if (!noteListLoading) {
													loadMoreNotes();
												}
											}}
										>
											<div class="w-full flex justify-center py-2 text-xs animate-pulse items-center gap-2">
												{#if noteListLoading}
													<Spinner className="size-3" />
													{$i18n.t('Loading...')}
												{/if}
											</div>
										</Loader>
									{/if}
								</div>
							</div>
						</div>
					</div>
				{:else}
					<div class="flex flex-col justify-center h-full max-h-full">
						<div class="text-center text-muted-foreground dark:text-gray-500">
							{query ? $i18n.t('No results found') : $i18n.t('No notes')}
						</div>
					</div>
				{/if}
			{:else}
				<div class="flex flex-col justify-center h-full max-h-full">
					<Spinner className="size-6" />
				</div>
			{/if}
		</div>
	</div>
</Modal>