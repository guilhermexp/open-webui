<script>
	// import { knowledge, prompts } from '$lib/stores'; // Removed in notes-only app

	import { removeLastWordFromString } from '$lib/utils';
	// import { getPrompts } from '$lib/apis/prompts'; // Removed in notes-only app
	// import { getKnowledgeBases } from '$lib/apis/knowledge'; // Removed in notes-only app

	// import Prompts from './Commands/Prompts.svelte'; // Removed in notes-only app
	// import Knowledge from './Commands/Knowledge.svelte'; // Removed in notes-only app
	import Models from './Commands/Models.svelte';
	import Spinner from '$lib/components/common/Spinner.svelte';

	export let show = false;

	export let files = [];
	export let command = '';

	export let onSelect = (e) => {};
	export let onUpload = (e) => {};

	export let insertTextHandler = (text) => {};

	let loading = false;
	let commandElement = null;

	export const selectUp = () => {
		commandElement?.selectUp();
	};

	export const selectDown = () => {
		commandElement?.selectDown();
	};

	$: if (show) {
		init();
	}

	const init = async () => {
		loading = true;
		// No longer need to load prompts and knowledge in notes-only app
		// await Promise.all([
		// 	(async () => {
		// 		prompts.set(await getPrompts(localStorage.token));
		// 	})(),
		// 	(async () => {
		// 		knowledge.set(await getKnowledgeBases(localStorage.token));
		// 	})()
		// ]);
		loading = false;
	};
</script>

{#if show}
	{#if !loading}
		{#if command?.charAt(0) === '@'}
			<Models
				bind:this={commandElement}
				{command}
				onSelect={(e) => {
					const { type, data } = e;

					if (type === 'model') {
						insertTextHandler('');

						onSelect({
							type: 'model',
							data: data
						});
					}
				}}
			/>
		{/if}
	{:else}
		<div
			id="commands-container"
			class="px-2 mb-2 text-left w-full absolute bottom-0 left-0 right-0 z-10"
		>
			<div class="flex w-full rounded-xl border border-gray-100 dark:border-gray-850">
				<div
					class="max-h-60 flex flex-col w-full rounded-xl bg-white dark:bg-gray-900 dark:text-gray-100"
				>
					<Spinner />
				</div>
			</div>
		</div>
	{/if}
{/if}
