<script>
	export let show = false;
</script>

{#if show}
	<div
		class="fixed inset-0 z-[9999] bg-black/50 backdrop-blur-sm flex items-center justify-center"
		on:click={() => (show = false)}
		on:keydown={(e) => e.key === 'Escape' && (show = false)}
		tabindex="0"
		role="button"
	>
		<div class="bg-white dark:bg-gray-800 p-8 rounded-lg max-w-md w-full mx-4">
			<div class="text-center">
				<div class="text-4xl mb-4">📁</div>
				<div class="text-lg font-medium mb-2">Arraste arquivos aqui</div>
				<div class="text-sm text-gray-500 dark:text-gray-400">
					Solte os arquivos para fazer upload
				</div>
			</div>
		</div>
	</div>
{/if}