<script lang="ts">
	import { createEventDispatcher, getContext } from 'svelte';
	import { toast } from 'svelte-sonner';
	import { copyToClipboard, getMessageContentParts, removeAllDetails } from '$lib/utils';
	import { config, settings, TTSWorker } from '$lib/stores';
	import { synthesizeOpenAISpeech } from '$lib/apis/audio';
	import { generateOpenAIChatCompletion } from '$lib/apis/openai';
	import { KokoroWorker } from '$lib/workers/KokoroWorker';
	import Tooltip from '$lib/components/common/Tooltip.svelte';
	import DeleteConfirmDialog from '$lib/components/common/ConfirmDialog.svelte';

	const dispatch = createEventDispatcher();
	const i18n = getContext('i18n');

	export let noteContent = '';
	export let noteId = '';
	export let showDelete = true;
	export let showRegenerate = true;
	export let showContinue = false;
	export let showReadAloud = true;
	export let showCopy = true;
	export let showTags = true;
	export let isLoading = false;

	let audioParts: Record<number, HTMLAudioElement | null> = {};
	let speaking = false;
	let speakingIdx: number | undefined;
	let loadingSpeech = false;
	let showDeleteConfirm = false;
	let showPersonaDropdown = false;
	
	// TTS Personas simplificadas
	const ttsPersonas = [
		{
			id: 'normal',
			name: 'Leitura Completa',
			prompt: null
		},
		{
			id: 'educational',
			name: 'Educativo',
			prompt: `Transforme este conteúdo em uma explicação educativa clara e didática, usando linguagem acessível e exemplos quando apropriado:\n\n`
		},
		{
			id: 'summary',
			name: 'Resumido',
			prompt: `Faça um resumo claro e conciso deste conteúdo, destacando apenas os pontos principais:\n\n`
		}
	];

	const copyNoteContent = () => {
		if (noteContent.trim()) {
			copyToClipboard(noteContent);
			toast.success($i18n.t('Note content copied to clipboard'));
		}
	};

	const playAudio = (idx: number) => {
		return new Promise<void>((res) => {
			speakingIdx = idx;
			const audio = audioParts[idx];

			if (!audio) {
				return res();
			}

			audio.play();
			audio.onended = async () => {
				await new Promise((r) => setTimeout(r, 300));

				if (Object.keys(audioParts).length - 1 === idx) {
					speaking = false;
				}

				res();
			};
		});
	};

	// Função para processar conteúdo com IA baseado na persona
	const processContentWithPersona = async (content: string, persona: any) => {
		if (!persona.prompt) {
			return content; // Leitura normal, sem transformação
		}
		
		try {
			const fullPrompt = `${persona.prompt}\n\n${content}`;
			
			const response = await generateOpenAIChatCompletion(
				localStorage.getItem('token') || '',
				{
					messages: [
						{
							role: 'user',
							content: fullPrompt
						}
					],
					model: $config?.default_model || $config?.model || 'gpt-3.5-turbo',
					stream: false
				}
			);
			
			return response?.choices?.[0]?.message?.content || content;
		} catch (error) {
			console.error('Erro ao processar conteúdo com persona:', error);
			toast.error('Erro ao processar conteúdo. Usando texto original.');
			return content;
		}
	};

	const speakWithPersona = async (persona: any) => {
		showPersonaDropdown = false;
		
		if (speaking) {
			try {
				speechSynthesis.cancel();
				if (speakingIdx !== undefined && audioParts[speakingIdx]) {
					audioParts[speakingIdx]!.pause();
					audioParts[speakingIdx]!.currentTime = 0;
				}
			} catch {}
			speaking = false;
			speakingIdx = undefined;
			return;
		}

		if (!noteContent.trim()) {
			toast.info($i18n.t('No content to speak'));
			return;
		}

		speaking = true;
		loadingSpeech = true;
		
		// Processar conteúdo com a persona selecionada
		const processedContent = await processContentWithPersona(noteContent, persona);
		const content = removeAllDetails(processedContent);

		if ($config.audio.tts.engine === '') {
			let voices = [];
			const getVoicesLoop = setInterval(() => {
				voices = speechSynthesis.getVoices();
				if (voices.length > 0) {
					clearInterval(getVoicesLoop);

					const voice =
						voices
							?.filter(
								(v) => v.voiceURI === ($settings?.audio?.tts?.voice ?? $config?.audio?.tts?.voice)
							)
							?.at(0) ?? undefined;

					const speak = new SpeechSynthesisUtterance(content);
					speak.rate = $settings.audio?.tts?.playbackRate ?? 1;

					speak.onend = () => {
						speaking = false;
						loadingSpeech = false;
					};

					if (voice) {
						speak.voice = voice;
					}

					loadingSpeech = false;
					speechSynthesis.speak(speak);
				}
			}, 100);
		} else {
			const messageContentParts: string[] = getMessageContentParts(
				content,
				$config?.audio?.tts?.split_on ?? 'punctuation'
			);

			if (!messageContentParts.length) {
				console.log('No content to speak');
				toast.info($i18n.t('No content to speak'));
				speaking = false;
				loadingSpeech = false;
				return;
			}

			console.debug('Prepared note content for TTS', messageContentParts);

			audioParts = messageContentParts.reduce(
				(acc, _sentence, idx) => {
					acc[idx] = null;
					return acc;
				},
				{} as typeof audioParts
			);

			let lastPlayedAudioPromise = Promise.resolve();

			if ($settings.audio?.tts?.engine === 'browser-kokoro') {
				if (!$TTSWorker) {
					await TTSWorker.set(
						new KokoroWorker({
							dtype: $settings.audio?.tts?.engineConfig?.dtype ?? 'fp32'
						})
					);

					await $TTSWorker.init();
				}

				// Define valid Kokoro voices and implement fallback
				const validKokoroVoices = ['af_heart', 'af_alloy', 'af_aoede', 'af_sky', 'af_nova', 'af_luna'];
				const requestedVoice = $settings?.audio?.tts?.voice ?? $config?.audio?.tts?.voice;
				const kokoroVoice = validKokoroVoices.includes(requestedVoice) ? requestedVoice : 'af_heart';

				if (requestedVoice && !validKokoroVoices.includes(requestedVoice)) {
					console.warn(`Invalid Kokoro voice "${requestedVoice}", using fallback voice "af_heart"`);
				}

				for (const [idx, sentence] of messageContentParts.entries()) {
					const blob = await $TTSWorker
						.generate({
							text: sentence,
							voice: kokoroVoice
						})
						.catch((error) => {
							console.error(error);
							toast.error(`${error}`);

							speaking = false;
							loadingSpeech = false;
						});

					if (blob) {
						const audio = new Audio(blob);
						audio.playbackRate = $settings.audio?.tts?.playbackRate ?? 1;

						audioParts[idx] = audio;
						loadingSpeech = false;
						lastPlayedAudioPromise = lastPlayedAudioPromise.then(() => playAudio(idx));
					}
				}
			} else {
				for (const [idx, sentence] of messageContentParts.entries()) {
					const res = await synthesizeOpenAISpeech(
						localStorage.token,
						$settings?.audio?.tts?.defaultVoice === $config.audio.tts.voice
							? ($settings?.audio?.tts?.voice ?? $config?.audio?.tts?.voice)
							: $config?.audio?.tts?.voice,
						sentence
					).catch((error) => {
						console.error(error);
						toast.error(`${error}`);

						speaking = false;
						loadingSpeech = false;
					});

					if (res) {
						const blob = await res.blob();
						const blobUrl = URL.createObjectURL(blob);
						const audio = new Audio(blobUrl);
						audio.playbackRate = $settings.audio?.tts?.playbackRate ?? 1;

						audioParts[idx] = audio;
						loadingSpeech = false;
						lastPlayedAudioPromise = lastPlayedAudioPromise.then(() => playAudio(idx));
					}
				}
			}
		}
	};

	const toggleSpeakNote = async () => {
		if (speaking) {
			try {
				speechSynthesis.cancel();

				if (speakingIdx !== undefined && audioParts[speakingIdx]) {
					audioParts[speakingIdx]!.pause();
					audioParts[speakingIdx]!.currentTime = 0;
				}
			} catch {}

			speaking = false;
			speakingIdx = undefined;
			return;
		}

		if (!noteContent.trim()) {
			toast.info($i18n.t('No content to speak'));
			return;
		}

		// Mostrar dropdown de personas
		showPersonaDropdown = !showPersonaDropdown;
	};

	const handleRegenerate = () => {
		dispatch('regenerate', { noteId });
	};

	const handleContinue = () => {
		dispatch('continue', { noteId });
	};

	const handleDelete = () => {
		dispatch('delete', { noteId });
	};

	const confirmDelete = () => {
		showDeleteConfirm = false;
		handleDelete();
	};

	const handleTags = () => {
		dispatch('tags', { noteId });
	};

</script>

<DeleteConfirmDialog
	bind:show={showDeleteConfirm}
	title={$i18n.t('Delete note?')}
	on:confirm={confirmDelete}
/>

<div
	class="flex justify-start overflow-x-auto buttons text-gray-600 dark:text-gray-500 mt-2 mb-1"
	style="scrollbar-width: none; -ms-overflow-style: none;"
>
	{#if showCopy}
		<Tooltip content={$i18n.t('Copy')} placement="bottom">
			<button
				aria-label={$i18n.t('Copy')}
				class="p-1.5 hover:bg-black/5 dark:hover:bg-white/5 rounded-lg dark:hover:text-white hover:text-black transition"
				disabled={!noteContent.trim()}
				on:click={copyNoteContent}
			>
				<svg
					xmlns="http://www.w3.org/2000/svg"
					fill="none"
					aria-hidden="true"
					viewBox="0 0 24 24"
					stroke-width="2.3"
					stroke="currentColor"
					class="w-4 h-4"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						d="M15.666 3.888A2.25 2.25 0 0013.5 2.25h-3c-1.03 0-1.9.693-2.166 1.638m7.332 0c.055.194.084.4.084.612v0a.75.75 0 01-.75.75H9a.75.75 0 01-.75-.75v0c0-.212.03-.418.084-.612m7.332 0c.646.049 1.288.11 1.927.184 1.1.128 1.907 1.077 1.907 2.185V19.5a2.25 2.25 0 01-2.25 2.25H6.75A2.25 2.25 0 014.5 19.5V6.257c0-1.108.806-2.057 1.907-2.185a48.208 48.208 0 011.927-.184"
					/>
				</svg>
			</button>
		</Tooltip>
	{/if}

	{#if showReadAloud}
		<div class="relative">
			<Tooltip content={$i18n.t('Read Aloud')} placement="bottom">
				<button
					aria-label={$i18n.t('Read Aloud')}
					class="p-1.5 hover:bg-black/5 dark:hover:bg-white/5 rounded-lg dark:hover:text-white hover:text-black transition"
					disabled={loadingSpeech || !noteContent.trim()}
					on:click={() => {
						if (!loadingSpeech) {
							toggleSpeakNote();
						}
					}}
				>
					{#if loadingSpeech}
						<svg
							aria-hidden="true"
							class=" w-4 h-4"
							fill="currentColor"
							viewBox="0 0 24 24"
							xmlns="http://www.w3.org/2000/svg"
						>
							<style>
								.spinner_S1WN {
									animation: spinner_MGfb 0.8s linear infinite;
									animation-delay: -0.8s;
								}

								.spinner_Km9P {
									animation-delay: -0.65s;
								}

								.spinner_JApP {
									animation-delay: -0.5s;
								}

								@keyframes spinner_MGfb {
									93.75%,
									100% {
										opacity: 0.2;
									}
								}
							</style>
							<circle class="spinner_S1WN" cx="4" cy="12" r="3" />
							<circle class="spinner_S1WN spinner_Km9P" cx="12" cy="12" r="3" />
							<circle class="spinner_S1WN spinner_JApP" cx="20" cy="12" r="3" />
						</svg>
					{:else if speaking}
						<svg
							xmlns="http://www.w3.org/2000/svg"
							fill="none"
							viewBox="0 0 24 24"
							aria-hidden="true"
							stroke-width="2.3"
							stroke="currentColor"
							class="w-4 h-4"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								d="M17.25 9.75 19.5 12m0 0 2.25 2.25M19.5 12l2.25-2.25M19.5 12l-2.25 2.25m-10.5-6 4.72-4.72a.75.75 0 0 1 1.28.53v15.88a.75.75 0 0 1-1.28.53l-4.72-4.72H4.51c-.88 0-1.704-.507-1.938-1.354A9.009 9.009 0 0 1 2.25 12c0-.83.112-1.633.322-2.396C2.806 8.756 3.63 8.25 4.51 8.25H6.75Z"
							/>
						</svg>
					{:else}
						<svg
							xmlns="http://www.w3.org/2000/svg"
							fill="none"
							viewBox="0 0 24 24"
							aria-hidden="true"
							stroke-width="2.3"
							stroke="currentColor"
							class="w-4 h-4"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								d="M19.114 5.636a9 9 0 010 12.728M16.463 8.288a5.25 5.25 0 010 7.424M6.75 8.25l4.72-4.72a.75.75 0 011.28.53v15.88a.75.75 0 01-1.28.53l-4.72-4.72H4.51c-.88 0-1.704-.507-1.938-1.354A9.01 9.01 0 012.25 12c0-.83.112-1.633.322-2.396C2.806 8.756 3.63 8.25 4.51 8.25H6.75z"
							/>
						</svg>
					{/if}
				</button>
			</Tooltip>

			<!-- Dropdown de opções TTS -->
			{#if showPersonaDropdown}
				<div style="position: absolute; bottom: 100%; margin-bottom: 4px; left: 0; background: white; border: 1px solid #d1d5db; border-radius: 6px; box-shadow: 0 2px 8px rgba(0,0,0,0.15); z-index: 9999; min-width: 140px;">
					{#each ttsPersonas as persona}
						<button 
							style="display: block; width: 100%; text-align: left; padding: 8px 12px; border: none; background: transparent; cursor: pointer; font-size: 13px; color: #374151;"
							class="hover:bg-gray-100 dark:hover:bg-gray-700 dark:text-gray-200"
							on:click={() => speakWithPersona(persona)}
						>
							{persona.name}
						</button>
					{/each}
				</div>
				
				<!-- Overlay para fechar -->
				<div style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; z-index: 9998;" on:click={() => showPersonaDropdown = false}></div>
			{/if}
		</div>
	{/if}

	{#if showContinue}
		<Tooltip content={$i18n.t('Continue Response')} placement="bottom">
			<button
				aria-label={$i18n.t('Continue Response')}
				class="p-1.5 hover:bg-black/5 dark:hover:bg-white/5 rounded-lg dark:hover:text-white hover:text-black transition"
				disabled={isLoading}
				on:click={handleContinue}
			>
				<svg
					aria-hidden="true"
					xmlns="http://www.w3.org/2000/svg"
					fill="none"
					viewBox="0 0 24 24"
					stroke-width="2.3"
					stroke="currentColor"
					class="w-4 h-4"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						d="M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z"
					/>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						d="M15.91 11.672a.375.375 0 0 1 0 .656l-5.603 3.113a.375.375 0 0 1-.557-.328V8.887c0-.286.307-.466.557-.327l5.603 3.112Z"
					/>
				</svg>
			</button>
		</Tooltip>
	{/if}

	{#if showRegenerate}
		<Tooltip content={$i18n.t('Regenerate')} placement="bottom">
			<button
				aria-label={$i18n.t('Regenerate')}
				class="p-1.5 hover:bg-black/5 dark:hover:bg-white/5 rounded-lg dark:hover:text-white hover:text-black transition"
				disabled={isLoading}
				on:click={handleRegenerate}
			>
				<svg
					xmlns="http://www.w3.org/2000/svg"
					fill="none"
					viewBox="0 0 24 24"
					stroke-width="2.3"
					aria-hidden="true"
					stroke="currentColor"
					class="w-4 h-4"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182m0-4.991v4.99"
					/>
				</svg>
			</button>
		</Tooltip>
	{/if}

	{#if showTags}
		<Tooltip content={$i18n.t('Tags')} placement="bottom">
			<button
				aria-label={$i18n.t('Tags')}
				class="p-1.5 hover:bg-black/5 dark:hover:bg-white/5 rounded-lg dark:hover:text-white hover:text-black transition"
				disabled={isLoading}
				on:click={handleTags}
			>
				<svg
					xmlns="http://www.w3.org/2000/svg"
					fill="none"
					viewBox="0 0 24 24"
					stroke-width="2.3"
					stroke="currentColor"
					aria-hidden="true"
					class="w-4 h-4"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						d="M9.568 3H5.25A2.25 2.25 0 003 5.25v4.318c0 .597.237 1.17.659 1.591l9.581 9.581c.699.699 1.78.872 2.607.33a18.095 18.095 0 005.223-5.223c.542-.827.369-1.908-.33-2.607L11.16 3.66A2.25 2.25 0 009.568 3z"
					/>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						d="M6 6h.008v.008H6V6z"
					/>
				</svg>
			</button>
		</Tooltip>
	{/if}

	{#if showDelete}
		<Tooltip content={$i18n.t('Delete')} placement="bottom">
			<button
				aria-label={$i18n.t('Delete')}
				class="p-1.5 hover:bg-black/5 dark:hover:bg-white/5 rounded-lg dark:hover:text-white hover:text-black transition"
				disabled={isLoading}
				on:click={() => (showDeleteConfirm = true)}
			>
				<svg
					xmlns="http://www.w3.org/2000/svg"
					fill="none"
					viewBox="0 0 24 24"
					stroke-width="2"
					stroke="currentColor"
					aria-hidden="true"
					class="w-4 h-4"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0"
					/>
				</svg>
			</button>
		</Tooltip>
	{/if}
</div>

<style>
	.buttons::-webkit-scrollbar {
		display: none;
	}
</style>