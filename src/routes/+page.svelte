<script>
	import { onMount } from 'svelte';
	
	let loading = true;
	let error = null;
	const BACKEND_URL = 'http://localhost:8888';
	
	onMount(async () => {
		try {
			// Verificar se o backend está rodando
			const response = await fetch(BACKEND_URL);
			if (response.ok) {
				loading = false;
			} else {
				throw new Error('Backend não está respondendo');
			}
		} catch (err) {
			error = err.message;
			loading = false;
		}
	});
</script>

<svelte:head>
	<title>Notes App - Aplicação de Notas Avançada</title>
</svelte:head>

<div class="container">
	{#if loading}
		<div class="loading">
			<h1>📝 Notes App</h1>
			<p>Carregando aplicação...</p>
		</div>
	{:else if error}
		<div class="error">
			<h1>❌ Erro de Conexão</h1>
			<p>Não foi possível conectar ao backend: {error}</p>
			<p>Verifique se o servidor está rodando na porta 8888</p>
		</div>
	{:else}
		<div class="welcome">
			<h1>📝 Notes App</h1>
			<p>Aplicação especializada de notas baseada no Open WebUI</p>
			
			<div class="features">
				<div class="feature">
					<h3>✨ Editor Avançado</h3>
					<p>Editor completo com chat integrado</p>
				</div>
				
				<div class="feature">
					<h3>🎤 Transcrição de Áudio</h3>
					<p>Converta áudio em texto automaticamente</p>
				</div>
				
				<div class="feature">
					<h3>🔗 Processamento de URLs</h3>
					<p>Extraia conteúdo de links automaticamente</p>
				</div>
				
				<div class="feature">
					<h3>📁 Sistema de Pastas</h3>
					<p>Organize suas notas de forma inteligente</p>
				</div>
			</div>
			
			<div class="actions">
				<button class="btn-primary">Começar a Usar</button>
				<button class="btn-secondary">Ver Documentação</button>
			</div>
		</div>
	{/if}
</div>

<style>
	.container {
		min-height: 100vh;
		display: flex;
		align-items: center;
		justify-content: center;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		color: white;
		text-align: center;
		padding: 2rem;
	}
	
	.loading, .error, .welcome {
		max-width: 800px;
		width: 100%;
	}
	
	h1 {
		font-size: 3rem;
		margin-bottom: 1rem;
		font-weight: 700;
	}
	
	.features {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
		gap: 2rem;
		margin: 3rem 0;
	}
	
	.feature {
		background: rgba(255, 255, 255, 0.1);
		padding: 2rem;
		border-radius: 12px;
		backdrop-filter: blur(10px);
	}
	
	.feature h3 {
		margin-bottom: 1rem;
		font-size: 1.2rem;
	}
	
	.actions {
		display: flex;
		gap: 1rem;
		justify-content: center;
		flex-wrap: wrap;
		margin-top: 2rem;
	}
	
	.btn-primary, .btn-secondary {
		padding: 1rem 2rem;
		border: none;
		border-radius: 8px;
		font-size: 1.1rem;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.3s ease;
	}
	
	.btn-primary {
		background: #4f46e5;
		color: white;
	}
	
	.btn-primary:hover {
		background: #4338ca;
		transform: translateY(-2px);
	}
	
	.btn-secondary {
		background: rgba(255, 255, 255, 0.2);
		color: white;
		border: 2px solid rgba(255, 255, 255, 0.3);
	}
	
	.btn-secondary:hover {
		background: rgba(255, 255, 255, 0.3);
		transform: translateY(-2px);
	}
	
	.error {
		background: rgba(239, 68, 68, 0.1);
		padding: 2rem;
		border-radius: 12px;
		border: 2px solid rgba(239, 68, 68, 0.3);
	}
</style>
