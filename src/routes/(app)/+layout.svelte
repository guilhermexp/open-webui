<script lang="ts">
	import { onMount, getContext } from 'svelte';
	import { goto } from '$app/navigation';

	import { getUserSettings } from '$lib/apis/users';

	import {
		config,
		user,
		settings
	} from '$lib/stores';

	import Spinner from '$lib/components/common/Spinner.svelte';

	const i18n = getContext('i18n');

	let loaded = false;

	onMount(async () => {
		if ($user === undefined || $user === null) {
			await goto('/auth');
		} else if (['user', 'admin'].includes($user?.role)) {
			// Carregar configurações do usuário
			const userSettings = await getUserSettings(localStorage.token).catch((error) => {
				console.error(error);
				return null;
			});

			if (userSettings) {
				settings.set(userSettings.ui);
			} else {
				let localStorageSettings = {} as Parameters<(typeof settings)['set']>[0];

				try {
					localStorageSettings = JSON.parse(localStorage.getItem('settings') ?? '{}');
				} catch (e: unknown) {
					console.error('Failed to parse settings from localStorage', e);
				}

				settings.set(localStorageSettings);
			}
		}

		loaded = true;
	});
</script>

{#if loaded}
	<div class="app relative">
		<div class="text-gray-700 dark:text-gray-100 bg-white dark:bg-gray-900 h-screen max-h-[100dvh] overflow-auto flex flex-row justify-end">
			<slot />
		</div>
	</div>
{:else}
	<div class="app bg-white dark:bg-gray-900">
		<div class="w-full h-screen flex items-center justify-center">
			<Spinner className="size-8" />
		</div>
	</div>
{/if}

<style>
	.app {
		min-height: 100dvh;
	}
</style>