<script lang="ts">
	import { onMount, tick, getContext, createEventDispatcher, onDestroy } from 'svelte';
	import { fade, fly } from 'svelte/transition';
	import { toast } from 'svelte-sonner';
	
	const dispatch = createEventDispatcher();
	const i18n = getContext('i18n');

	import {
		type Model,
		mobile,
		settings,
		models,
		config,
		tools,
		user
	} from '$lib/stores';

	import { uploadFile } from '$lib/apis/files';
	import { PASTED_TEXT_CHARACTER_LIMIT } from '$lib/constants';
	
	import InputMenu from './MessageInput/InputMenu.svelte';
	import VoiceRecording from './MessageInput/VoiceRecording.svelte';
	import Commands from './MessageInput/Commands.svelte';
	import ToolsMenu from './MessageInput/ToolsMenu.svelte';
	import TextToSpeech from './MessageInput/TextToSpeech.svelte';
	
	// Icons
	import ChevronDown from '$lib/components/icons/ChevronDown.svelte';
	import Plus from '$lib/components/icons/Plus.svelte';
	import GlobeAlt from '$lib/components/icons/GlobeAlt.svelte';
	import CodeBracket from '$lib/components/icons/CodeBracket.svelte';
	import PhotoSolid from '$lib/components/icons/PhotoSolid.svelte';

	// Props
	export let transparentBackground = false;
	export let onChange: Function = () => {};
	export let createMessagePair: Function;
	export let stopResponse: Function;
	export let autoScroll = false;
	export let atSelectedModel: Model | undefined = undefined;
	export let selectedModels: string[] = [];
	export let history;
	export let taskIds = null;
	export let prompt = '';
	export let files = [];
	export let toolServers = [];
	export let selectedToolIds = [];
	export let selectedFilterIds = [];
	export let imageGenerationEnabled = false;
	export let webSearchEnabled = false;
	export let codeInterpreterEnabled = false;
	export let loading = false;
	export let placeholder = '';

	// State
	let textareaRef: HTMLTextAreaElement;
	let selectedModelId = '';
	let showModelDropdown = false;
	let showCommandsMenu = false;
	let commandsElement = null;
	let command = '';
	let isComposing = false;
	let minHeight = 72;
	let maxHeight = 300;
	let filesInputElement;
	let _loading = false;
	let recording = false;

	$: selectedModelIds = atSelectedModel !== undefined ? [atSelectedModel.id] : selectedModels;
	$: fileUploadCapableModels = selectedModelIds.filter(id => {
		const model = $models.find(m => m.id === id);
		return model?.info?.meta?.capabilities?.vision || 
			   model?.info?.meta?.capabilities?.usage?.includes('vision');
	});
	
	// Handle click outside to close dropdowns
	function handleClickOutside(event: MouseEvent) {
		const modelDropdownEl = document.querySelector('.model-dropdown-container');
		if (modelDropdownEl && !modelDropdownEl.contains(event.target as Node)) {
			showModelDropdown = false;
		}
	}

	// Initialize selected model
	$: if (selectedModelIds.length > 0 && !selectedModelId) {
		selectedModelId = selectedModelIds[0];
	}

	// Model icons
	const MODEL_ICONS = {
		openai: `<svg class="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
			<path d="M22.282 9.821a5.985 5.985 0 0 0-.516-4.91 6.046 6.046 0 0 0-6.51-2.9A6.065 6.065 0 0 0 4.981 4.18a5.985 5.985 0 0 0-3.998 2.9 6.046 6.046 0 0 0 .743 7.097 5.975 5.975 0 0 0 .51 4.911 6.051 6.051 0 0 0 6.515 2.9A5.985 5.985 0 0 0 13.26 24a6.056 6.056 0 0 0 5.772-4.206 5.99 5.99 0 0 0 3.997-2.9 5.992 5.992 0 0 0-.747-7.073zM13.26 22.43a4.476 4.476 0 0 1-2.876-1.04l.141-.081 4.779-2.758a.795.795 0 0 0 .392-.681v-6.737l2.02 1.168a.071.071 0 0 1 .038.052v5.583a4.504 4.504 0 0 1-4.494 4.494zM3.6 18.304a4.47 4.47 0 0 1-.535-3.014l.142.085 4.783 2.759a.771.771 0 0 0 .78 0l5.843-3.369v2.332a.08.08 0 0 1-.033.062L9.74 19.95a4.5 4.5 0 0 1-6.14-1.646zM2.34 7.896a4.485 4.485 0 0 1 2.366-1.973V11.6a.766.766 0 0 0 .388.676l5.815 3.355-2.02 1.168a.076.076 0 0 1-.071 0l-4.83-2.786A4.504 4.504 0 0 1 2.34 7.872zm16.597 3.855l-5.833-3.387L15.119 7.2a.076.076 0 0 1 .071 0l4.83 2.791a4.494 4.494 0 0 1-.676 8.105v-5.678a.79.79 0 0 0-.407-.667zm2.01-3.023l-.141-.085-4.774-2.782a.776.776 0 0 0-.785 0L9.409 9.23V6.897a.066.066 0 0 1 .028-.061l4.83-2.787a4.5 4.5 0 0 1 6.68 4.66zm-12.64 4.135l-2.02-1.164a.08.08 0 0 1-.038-.057V6.075a4.5 4.5 0 0 1 7.375-3.453l-.142.08L8.704 5.46a.795.795 0 0 0-.393.681zm1.097-2.365l2.602-1.5 2.607 1.5v2.999l-2.597 1.5-2.607-1.5z"/>
		</svg>`,
		anthropic: `<svg class="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
			<path d="M13.827 3.52h3.603L24 20h-3.603l-6.57-16.48zm-7.258 0h3.767L16.906 20h-3.674l-1.343-3.461H5.017l-1.344 3.46H0L6.57 3.522zm4.132 9.959L8.453 7.687 6.205 13.48H10.7z"/>
		</svg>`,
		google: `<svg class="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
			<path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
			<path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
			<path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
			<path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
		</svg>`
	};

	// Auto-resize textarea
	function adjustHeight(reset = false) {
		if (!textareaRef) return;
		
		if (reset) {
			textareaRef.style.height = `${minHeight}px`;
			return;
		}
		
		textareaRef.style.height = `${minHeight}px`;
		const newHeight = Math.max(minHeight, Math.min(textareaRef.scrollHeight, maxHeight));
		textareaRef.style.height = `${newHeight}px`;
	}

	function handleInput() {
		adjustHeight();
		onChange(prompt);
		
		// Check for commands
		const lastSpaceIndex = prompt.lastIndexOf(' ');
		const textAfterLastSpace = prompt.slice(lastSpaceIndex + 1);
		
		if (textAfterLastSpace.startsWith('/')) {
			command = textAfterLastSpace.slice(1);
			showCommandsMenu = true;
		} else {
			command = '';
			showCommandsMenu = false;
		}
	}

	function handleKeyDown(e: KeyboardEvent) {
		const isCtrlPressed = e.ctrlKey || e.metaKey;
		
		if (showCommandsMenu && commandsElement) {
			if (e.key === 'ArrowUp') {
				e.preventDefault();
				commandsElement.selectUp();
			} else if (e.key === 'ArrowDown') {
				e.preventDefault();
				commandsElement.selectDown();
			} else if (e.key === 'Tab' || e.key === 'Enter') {
				e.preventDefault();
				const selectedButton = document.querySelector('.selected-command-option-button');
				selectedButton?.click();
			}
			return;
		}
		
		if (e.key === 'Enter' && !e.shiftKey) {
			if (isComposing) return;
			
			const enterPressed = ($settings?.ctrlEnterToSend ?? false)
				? isCtrlPressed
				: true;
				
			if (enterPressed) {
				e.preventDefault();
				handleSubmit();
			}
		}
		
		if (e.key === 'Escape') {
			atSelectedModel = undefined;
			selectedToolIds = [];
			selectedFilterIds = [];
			webSearchEnabled = false;
			imageGenerationEnabled = false;
			codeInterpreterEnabled = false;
		}
	}

	async function handlePaste(e: ClipboardEvent) {
		const clipboardData = e.clipboardData;
		if (!clipboardData) return;

		for (const item of clipboardData.items) {
			if (item.type.indexOf('image') !== -1) {
				const blob = item.getAsFile();
				if (!blob) continue;
				
				const reader = new FileReader();
				reader.onload = function (e) {
					files = [...files, {
						type: 'image',
						url: e.target?.result as string
					}];
				};
				reader.readAsDataURL(blob);
			} else if (item.kind === 'file') {
				const file = item.getAsFile();
				if (file) {
					await uploadFileHandler(file);
				}
			} else if (item.type === 'text/plain' && ($settings?.largeTextAsFile ?? false)) {
				const text = clipboardData.getData('text/plain');
				if (text.length > PASTED_TEXT_CHARACTER_LIMIT) {
					e.preventDefault();
					const blob = new Blob([text], { type: 'text/plain' });
					const file = new File([blob], `Pasted_Text_${Date.now()}.txt`, {
						type: 'text/plain'
					});
					await uploadFileHandler(file);
				}
			}
		}
	}

	async function uploadFileHandler(file: File) {
		if ($user?.role !== 'admin' && !($user?.permissions?.chat?.file_upload ?? true)) {
			toast.error($i18n.t('You do not have permission to upload files.'));
			return;
		}

		_loading = true;
		try {
			const uploadedFile = await uploadFile(localStorage.token, file);
			if (uploadedFile) {
				files = [...files, {
					collection_name: uploadedFile.collection_name,
					name: uploadedFile.filename,
					type: uploadedFile.type || 'file',
					size: file.size,
					url: uploadedFile.url || null,
					file: uploadedFile
				}];
			}
		} catch (error) {
			console.error('Upload error:', error);
			toast.error($i18n.t('Failed to upload file'));
		} finally {
			_loading = false;
		}
	}

	function handleSubmit() {
		if (prompt?.trim() === '' && files?.length === 0) return;
		
		if (createMessagePair) {
			createMessagePair(prompt);
		} else {
			dispatch('submit', prompt);
		}
		
		prompt = '';
		adjustHeight(true);
	}

	function getModelIcon(modelId: string) {
		const model = $models.find(m => m.id === modelId);
		if (!model) return '';
		
		const provider = model.owned_by?.toLowerCase() || '';
		if (provider.includes('openai')) return MODEL_ICONS.openai;
		if (provider.includes('anthropic') || provider.includes('claude')) return MODEL_ICONS.anthropic;
		if (provider.includes('google') || provider.includes('gemini')) return MODEL_ICONS.google;
		
		return '';
	}

	function getModelDisplayName(modelId: string) {
		const model = $models.find(m => m.id === modelId);
		return model?.name || modelId;
	}

	// Handlers for InputMenu
	const screenCaptureHandler = async () => {
		try {
			const stream = await navigator.mediaDevices.getDisplayMedia({
				video: { cursor: 'always' },
				audio: false
			});
			
			const video = document.createElement('video');
			video.srcObject = stream;
			video.play();
			
			video.onloadedmetadata = () => {
				const canvas = document.createElement('canvas');
				canvas.width = video.videoWidth;
				canvas.height = video.videoHeight;
				const ctx = canvas.getContext('2d');
				ctx?.drawImage(video, 0, 0, canvas.width, canvas.height);
				
				canvas.toBlob(async (blob) => {
					if (blob) {
						const file = new File([blob], `screenshot-${Date.now()}.png`, { type: 'image/png' });
						await uploadFileHandler(file);
					}
					stream.getTracks().forEach(track => track.stop());
				});
			};
		} catch (err) {
			console.error('Screen capture error:', err);
		}
	};

	const uploadFilesHandler = () => {
		filesInputElement?.click();
	};

	const inputFilesHandler = async (files: File[]) => {
		for (const file of files) {
			await uploadFileHandler(file);
		}
	};

	const uploadGoogleDriveHandler = async () => {
		toast.info($i18n.t('Google Drive integration coming soon'));
	};

	const uploadOneDriveHandler = async (type: string) => {
		toast.info($i18n.t('OneDrive integration coming soon'));
	};

	onMount(() => {
		if (textareaRef) {
			textareaRef.style.height = `${minHeight}px`;
		}
		
		// Add click outside listener
		document.addEventListener('click', handleClickOutside);
		
		return () => {
			document.removeEventListener('click', handleClickOutside);
		};
	});
</script>

<div class="w-full py-2">
	{#if showCommandsMenu && command}
		<div class="absolute bottom-full left-0 right-0 mb-2 z-50">
			<Commands
				bind:this={commandsElement}
				{command}
				on:select={(e) => {
					const selected = e.detail;
					prompt = prompt.substring(0, prompt.lastIndexOf('/')) + selected.content;
					showCommandsMenu = false;
					textareaRef?.focus();
				}}
			/>
		</div>
	{/if}

	<div class="bg-black/5 dark:bg-white/5 rounded-2xl relative">
		<div class="relative flex flex-col">
			<!-- Textarea Area -->
			<div class="overflow-y-auto" style="max-height: 400px">
				<textarea
					bind:this={textareaRef}
					bind:value={prompt}
					placeholder={placeholder || $i18n.t("What can I do for you?")}
					class="w-full px-4 py-3 bg-transparent border-none 
						   dark:text-white placeholder:text-black/70 dark:placeholder:text-white/70 
						   resize-none focus:outline-none focus:ring-0 min-h-[72px]"
					on:keydown={handleKeyDown}
					on:input={handleInput}
					on:paste={handlePaste}
					on:compositionstart={() => (isComposing = true)}
					on:compositionend={() => (isComposing = false)}
					rows="1"
				/>
			</div>

			<!-- Bottom Bar -->
			<div class="px-3 pb-3 flex items-center justify-between">
						<div class="flex items-center gap-2">
							<!-- Attachment Button -->
							<InputMenu
								{selectedModels}
								bind:selectedToolIds
								{fileUploadCapableModels}
								{screenCaptureHandler}
								{uploadFilesHandler}
								{inputFilesHandler}
								{uploadGoogleDriveHandler}
								{uploadOneDriveHandler}
								onClose={() => {}}
							>
								<button
									type="button"
									class="rounded-lg p-2 cursor-pointer
										   hover:bg-black/10 dark:hover:bg-white/10 
										   focus:outline-none focus:ring-1 focus:ring-blue-500
										   text-black/40 dark:text-white/40 hover:text-black dark:hover:text-white
										   transition-colors"
									aria-label={$i18n.t('Attach file')}
								>
									<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
											  d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
									</svg>
								</button>
							</InputMenu>

							<!-- Tools Menu -->
							<ToolsMenu
								bind:selectedToolIds
								onClose={() => {}}
							/>

							<!-- Web Search -->
							{#if $config?.features?.enable_web_search && ($user?.role === 'admin' || $user?.permissions?.features?.web_search)}
								<button
									type="button"
									class="rounded-lg p-2 cursor-pointer
										   hover:bg-black/10 dark:hover:bg-white/10 
										   focus:outline-none focus:ring-1 focus:ring-blue-500
										   transition-colors {webSearchEnabled ? 'text-green-500' : 'text-black/40 dark:text-white/40 hover:text-black dark:hover:text-white'}"
									aria-label={$i18n.t('Web Search')}
									on:click={() => (webSearchEnabled = !webSearchEnabled)}
								>
									<GlobeAlt className="w-4 h-4" />
								</button>
							{/if}

							<!-- Code Interpreter -->
							{#if $config?.features?.enable_code_interpreter && ($user?.role === 'admin' || $user?.permissions?.features?.code_interpreter)}
								<button
									type="button"
									class="rounded-lg p-2 cursor-pointer
										   hover:bg-black/10 dark:hover:bg-white/10 
										   focus:outline-none focus:ring-1 focus:ring-blue-500
										   transition-colors {codeInterpreterEnabled ? 'text-orange-500' : 'text-black/40 dark:text-white/40 hover:text-black dark:hover:text-white'}"
									aria-label={$i18n.t('Code Interpreter')}
									on:click={() => (codeInterpreterEnabled = !codeInterpreterEnabled)}
								>
									<CodeBracket className="w-4 h-4" />
								</button>
							{/if}

							<!-- Image Generation -->
							{#if $config?.features?.enable_image_generation && ($user?.role === 'admin' || $user?.permissions?.features?.image_generation)}
								<button
									type="button"
									class="rounded-lg p-2 cursor-pointer
										   hover:bg-black/10 dark:hover:bg-white/10 
										   focus:outline-none focus:ring-1 focus:ring-blue-500
										   transition-colors {imageGenerationEnabled ? 'text-purple-500' : 'text-black/40 dark:text-white/40 hover:text-black dark:hover:text-white'}"
									aria-label={$i18n.t('Image Generation')}
									on:click={() => (imageGenerationEnabled = !imageGenerationEnabled)}
								>
									<PhotoSolid className="w-4 h-4" />
								</button>
							{/if}

							<!-- Voice Recording -->
							{#if $settings?.audio?.stt?.enabled}
								<VoiceRecording
									bind:recording
									on:start={() => (recording = true)}
									on:stop={(e) => {
										recording = false;
										if (e.detail?.text) {
											prompt += (prompt ? ' ' : '') + e.detail.text;
											adjustHeight();
										}
									}}
								>
									<button
										type="button"
										class="rounded-lg p-2 cursor-pointer
											   hover:bg-black/10 dark:hover:bg-white/10 
											   focus:outline-none focus:ring-1 focus:ring-blue-500
											   transition-colors {recording ? 'text-red-500' : 'text-black/40 dark:text-white/40 hover:text-black dark:hover:text-white'}"
										aria-label={$i18n.t('Voice input')}
									>
										{#if recording}
											<div class="w-4 h-4 bg-red-500 rounded-full animate-pulse" />
										{:else}
											<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
													  d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
											</svg>
										{/if}
									</button>
								</VoiceRecording>
							{/if}

							<!-- Text to Speech -->
							{#if prompt?.length > 0}
								<TextToSpeech
									text={prompt}
									on:start={() => {}}
									on:stop={() => {}}
								/>
							{/if}
						</div>

						<!-- Submit Button -->
						<button
							type="button"
							class="rounded-lg p-2
								   hover:bg-black/10 dark:hover:bg-white/10 
								   focus:outline-none focus:ring-1 focus:ring-blue-500
								   transition-all duration-200
								   {prompt?.trim() || files?.length > 0 ? '' : 'opacity-30 cursor-not-allowed'}"
							aria-label={$i18n.t('Send message')}
							disabled={!prompt?.trim() && files?.length === 0}
							on:click={handleSubmit}
						>
							{#if loading || _loading}
								<svg class="w-4 h-4 dark:text-white animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
										  d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
								</svg>
							{:else}
								<svg class="w-4 h-4 dark:text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
								</svg>
							{/if}
						</button>
				</div>
			</div>
		</div>
	</div>

	<!-- Hidden file input -->
	<input
		bind:this={filesInputElement}
		type="file"
		multiple
		class="hidden"
		on:change={(e) => {
			const target = e.currentTarget;
			if (target.files) {
				inputFilesHandler(Array.from(target.files));
				target.value = '';
			}
		}}
	/>


	<!-- Files Preview -->
	{#if files?.length > 0}
		<div class="flex flex-wrap gap-2 mt-2">
			{#each files as file, idx}
				<div class="relative group bg-gray-100 dark:bg-gray-800 rounded-lg p-2 text-xs">
					<span>{file.name}</span>
					<button
						type="button"
						class="absolute -top-1 -right-1 bg-red-500 text-white rounded-full p-0.5 
							   opacity-0 group-hover:opacity-100 transition-opacity"
						on:click={() => (files = files.filter((_, i) => i !== idx))}
					>
						<svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
						</svg>
					</button>
				</div>
			{/each}
		</div>
	{/if}

	<!-- Feature Indicators -->
	{#if selectedModelIds?.length > 0 || webSearchEnabled || imageGenerationEnabled || codeInterpreterEnabled || selectedToolIds?.length > 0}
		<div class="flex flex-wrap gap-2 mt-2 text-xs">
			{#if atSelectedModel}
				<span class="px-2 py-1 rounded-full bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300">
					@{atSelectedModel.name}
				</span>
			{/if}
			
			{#if webSearchEnabled}
				<span class="px-2 py-1 rounded-full bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300">
					{$i18n.t('Web Search')}
				</span>
			{/if}
			
			{#if imageGenerationEnabled}
				<span class="px-2 py-1 rounded-full bg-purple-100 dark:bg-purple-900 text-purple-700 dark:text-purple-300">
					{$i18n.t('Image Generation')}
				</span>
			{/if}
			
			{#if codeInterpreterEnabled}
				<span class="px-2 py-1 rounded-full bg-orange-100 dark:bg-orange-900 text-orange-700 dark:text-orange-300">
					{$i18n.t('Code Interpreter')}
				</span>
			{/if}
			
			{#if selectedToolIds?.length > 0}
				<span class="px-2 py-1 rounded-full bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300">
					{selectedToolIds.length} {$i18n.t('tools')}
				</span>
			{/if}
		</div>
	{/if}

<style>
	/* Remove default textarea styling */
	textarea {
		field-sizing: content;
		-webkit-appearance: none;
		-moz-appearance: none;
		appearance: none;
	}
	
	/* Custom scrollbar */
	textarea::-webkit-scrollbar {
		width: 4px;
	}
	
	textarea::-webkit-scrollbar-track {
		background: transparent;
	}
	
	textarea::-webkit-scrollbar-thumb {
		background-color: rgba(0, 0, 0, 0.2);
		border-radius: 2px;
	}
	
	:global(.dark) textarea::-webkit-scrollbar-thumb {
		background-color: rgba(255, 255, 255, 0.2);
	}
</style>