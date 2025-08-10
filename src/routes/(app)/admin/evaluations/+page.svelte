<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';

	onMount(() => {
		// Redirect to users since evaluations is removed
		goto('/admin/users');
	});
</script>

<div class="flex items-center justify-center h-full">
	<div class="text-center">
		<h1 class="text-2xl font-bold mb-4">Esta página foi removida</h1>
		<p>Redirecionando para Usuários...</p>
	</div>
</div>