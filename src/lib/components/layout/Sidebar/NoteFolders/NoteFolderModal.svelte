<script lang="ts">
	import { getContext } from 'svelte';
	import Modal from '$lib/components/common/Modal.svelte';

	const i18n = getContext('i18n');

	export let show = false;
	export let edit = false;
	export let folder = null;

	export let onSubmit = () => {};

	let name = '';
	let data = {};

	$: if (edit && folder) {
		name = folder.name;
		data = folder.data ?? {};
	}

	const submitHandler = () => {
		onSubmit({
			name,
			data
		});
		show = false;
		name = '';
		data = {};
	};
</script>

<Modal bind:show size="sm">
	<div class="px-4 pt-4 pb-5 w-full">
		<form
			on:submit|preventDefault={() => {
				submitHandler();
			}}
		>
			<div class=" flex flex-col justify-center">
				<div class=" text-lg font-medium mb-2.5">
					{edit ? $i18n.t('Edit Folder') : $i18n.t('Create Folder')}
				</div>

				<div class="flex flex-col w-full">
					<div class=" mb-2 text-xs text-gray-500">{$i18n.t('Name')}</div>

					<div class="flex-1">
						<input
							class="w-full rounded-lg py-2 px-3 text-sm dark:text-gray-300 dark:bg-gray-850 outline-none"
							type="text"
							bind:value={name}
							placeholder={$i18n.t('Folder Name')}
							autocomplete="off"
							required
						/>
					</div>
				</div>
			</div>

			<div class="mt-4 flex justify-end gap-1.5">
				<button
					class="px-3.5 py-1.5 text-sm font-medium bg-black hover:bg-gray-900 text-white dark:bg-white dark:text-black dark:hover:bg-gray-100 transition rounded-full"
					type="submit"
				>
					{edit ? $i18n.t('Save') : $i18n.t('Create')}
				</button>

				<button
					class="px-3.5 py-1.5 text-sm font-medium hover:bg-gray-100 dark:bg-gray-800 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-200 transition rounded-full"
					type="button"
					on:click={() => {
						show = false;
					}}
				>
					{$i18n.t('Cancel')}
				</button>
			</div>
		</form>
	</div>
</Modal>