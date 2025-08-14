<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';

	onMount(() => {
		goto('/notes');
	});
</script>

<div class="w-full h-screen flex items-center justify-center">
	<div class="text-center">
		<div class="text-lg font-medium mb-2">Redirecionando para Notas...</div>
		<div class="text-sm text-gray-500">Se não for redirecionado automaticamente, <a href="/notes" class="text-blue-500 hover:text-blue-700">clique aqui</a>.</div>
	</div>
</div>
