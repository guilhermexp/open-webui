<script lang="ts">
	import { createEventDispatcher, getContext } from 'svelte';
	import { config, settings, user, TTSWorker } from '$lib/stores';
	import { synthesizeOpenAISpeech } from '$lib/apis/audio';
	import { KokoroWorker } from '$lib/workers/KokoroWorker';
	import { removeAllDetails } from '$lib/utils';
	import Tooltip from '$lib/components/common/Tooltip.svelte';

	const i18n = getContext('i18n');
	const dispatch = createEventDispatcher();

	export let text = '';
	export let speaking = false;

	let loadingSpeech = false;
	let speechSynthesis = window.speechSynthesis;
	let currentAudio: HTMLAudioElement | null = null;

	const stopSpeaking = () => {
		try {
			if (speechSynthesis) {
				speechSynthesis.cancel();
			}
			if (currentAudio) {
				currentAudio.pause();
				currentAudio.currentTime = 0;
				currentAudio = null;
			}
		} catch (e) {
			console.error('Error stopping speech:', e);
		}
		speaking = false;
		loadingSpeech = false;
	};

	const speakText = async () => {
		if (speaking) {
			stopSpeaking();
			return;
		}

		const cleanText = removeAllDetails(text).trim();
		if (!cleanText) {
			return;
		}

		speaking = true;
		loadingSpeech = true;

		try {
			if ($config.audio.tts.engine === '') {
				// Use browser's built-in TTS
				const utterance = new SpeechSynthesisUtterance(cleanText);
				
				// Set voice if available
				const voices = speechSynthesis.getVoices();
				const selectedVoice = voices.find(
					(v) => v.voiceURI === ($settings?.audio?.tts?.voice ?? $config?.audio?.tts?.voice)
				);
				if (selectedVoice) {
					utterance.voice = selectedVoice;
				}
				
				utterance.rate = $settings.audio?.tts?.playbackRate ?? 1;
				utterance.onend = () => {
					speaking = false;
				};
				
				loadingSpeech = false;
				speechSynthesis.speak(utterance);
			} else if ($settings.audio?.tts?.engine === 'browser-kokoro') {
				// Use Kokoro TTS
				if (!$TTSWorker) {
					await TTSWorker.set(
						new KokoroWorker({
							dtype: $settings.audio?.tts?.engineConfig?.dtype ?? 'fp32'
						})
					);
					await $TTSWorker.init();
				}

				const blob = await $TTSWorker.generate({
					text: cleanText,
					voice: $settings?.audio?.tts?.voice ?? $config?.audio?.tts?.voice
				});

				const audio = new Audio(URL.createObjectURL(blob));
				audio.playbackRate = $settings.audio?.tts?.playbackRate ?? 1;
				
				currentAudio = audio;
				loadingSpeech = false;
				
				audio.onended = () => {
					speaking = false;
					currentAudio = null;
				};
				
				await audio.play();
			} else {
				// Use OpenAI TTS
				const res = await synthesizeOpenAISpeech(
					localStorage.token,
					$settings?.audio?.tts?.defaultVoice === $config.audio.tts.voice
						? ($settings?.audio?.tts?.voice ?? $config?.audio?.tts?.voice)
						: $config?.audio?.tts?.voice,
					cleanText
				);

				if (res?.blob) {
					const audio = new Audio(URL.createObjectURL(res.blob));
					audio.playbackRate = $settings.audio?.tts?.playbackRate ?? 1;
					
					currentAudio = audio;
					loadingSpeech = false;
					
					audio.onended = () => {
						speaking = false;
						currentAudio = null;
					};
					
					await audio.play();
				}
			}
		} catch (error) {
			console.error('TTS error:', error);
			stopSpeaking();
		}
	};
</script>

{#if $user?.role === 'admin' || ($user?.permissions?.chat?.tts ?? true)}
	<Tooltip content={$i18n.t(speaking ? 'Stop' : 'Read Aloud')} placement="top">
		<slot>
			<button
				type="button"
				class="rounded-lg p-2 bg-black/5 dark:bg-white/5 cursor-pointer
					   hover:bg-black/10 dark:hover:bg-white/10 
					   focus:outline-none focus:ring-1 focus:ring-blue-500
					   transition-colors {speaking ? 'text-red-500' : 'text-black/40 dark:text-white/40 hover:text-black dark:hover:text-white'}"
				aria-label={$i18n.t(speaking ? 'Stop' : 'Read Aloud')}
				on:click={speakText}
			>
				{#if loadingSpeech}
					<svg class="w-4 h-4 animate-spin" fill="currentColor" viewBox="0 0 24 24">
						<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none" />
						<path class="opacity-75" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
					</svg>
				{:else if speaking}
					<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2.3" stroke="currentColor" class="w-4 h-4">
						<path stroke-linecap="round" stroke-linejoin="round" d="M17.25 9.75 19.5 12m0 0 2.25 2.25M19.5 12l2.25-2.25M19.5 12l-2.25 2.25m-10.5-6 4.72-4.72a.75.75 0 0 1 1.28.53v15.88a.75.75 0 0 1-1.28.53l-4.72-4.72H4.51c-.88 0-1.704-.507-1.938-1.354A9.009 9.009 0 0 1 2.25 12c0-.83.112-1.633.322-2.396C2.806 8.756 3.63 8.25 4.51 8.25H6.75Z" />
					</svg>
				{:else}
					<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2.3" stroke="currentColor" class="w-4 h-4">
						<path stroke-linecap="round" stroke-linejoin="round" d="M19.114 5.636a9 9 0 010 12.728M16.463 8.288a5.25 5.25 0 010 7.424M6.75 8.25l4.72-4.72a.75.75 0 011.28.53v15.88a.75.75 0 01-1.28.53l-4.72-4.72H4.51c-.88 0-1.704-.507-1.938-1.354A9.01 9.01 0 012.25 12c0-.83.112-1.633.322-2.396C2.806 8.756 3.63 8.25 4.51 8.25H6.75z" />
					</svg>
				{/if}
			</button>
		</slot>
	</Tooltip>
{/if}