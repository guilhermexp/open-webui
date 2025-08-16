<script>
	import '../app.css';
</script>

<main>
	<slot />
</main>

<style>
	:global(body) {
		margin: 0;
		padding: 0;
		font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
	}
	
	main {
		min-height: 100vh;
		display: flex;
		flex-direction: column;
	}
</style>
