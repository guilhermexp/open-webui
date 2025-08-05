<script lang="ts">
	import { DropdownMenu } from 'bits-ui';
	import { flyAndScale } from '$lib/utils/transitions';
	import { getContext } from 'svelte';

	import { config, user, mobile } from '$lib/stores';

	import Dropdown from '$lib/components/common/Dropdown.svelte';
	import Tooltip from '$lib/components/common/Tooltip.svelte';
	import DocumentArrowUpSolid from '$lib/components/icons/DocumentArrowUpSolid.svelte';
	import CameraSolid from '$lib/components/icons/CameraSolid.svelte';
	import PhotoSolid from '$lib/components/icons/PhotoSolid.svelte';

	const i18n = getContext('i18n');

	export let selectedModels: string[] = [];
	export let fileUploadCapableModels: string[] = [];

	export let screenCaptureHandler: Function;
	export let uploadFilesHandler: Function;
	export let inputFilesHandler: Function;

	export let uploadGoogleDriveHandler: Function;
	export let uploadOneDriveHandler: Function;

	export let onClose: Function;

	let show = false;
	let cameraInputElement;

	let fileUploadEnabled = true;
	$: fileUploadEnabled =
		fileUploadCapableModels.length === selectedModels.length &&
		($user?.role === 'admin' || $user?.permissions?.chat?.file_upload);

	const detectMobile = () => {
		return mobile;
	};

	const onDrop = async (e) => {
		e.preventDefault();

		if (e.dataTransfer?.files) {
			let files = Array.from(e.dataTransfer.files);

			if (files.length > 0) {
				e.stopPropagation();
			}

			inputFilesHandler(files);

			onClose();
			show = false;
		}
	};

	const handleGoogleDriveUpload = () => {
		show = false;
		uploadGoogleDriveHandler();
	};

	const handleOneDriveUpload = (type?: string) => {
		show = false;
		uploadOneDriveHandler(type);
	};
</script>

<Dropdown bind:show on:change={(e) => (e.detail === false ? onClose() : '')}>
	<Tooltip content={$i18n.t('More')}>
		<slot />
	</Tooltip>
	<div slot="content">
		<DropdownMenu.Content
			class="w-full max-w-[200px] rounded-xl px-1 py-1 border border-gray-300/30 dark:border-gray-700/50 z-50 bg-white dark:bg-gray-850 dark:text-white shadow-sm"
			sideOffset={10}
			alignOffset={-8}
			side="bottom"
			align="start"
			transition={flyAndScale}
		>
			<Tooltip
				content={fileUploadCapableModels.length !== selectedModels.length
					? $i18n.t('Model(s) do not support file upload')
					: !fileUploadEnabled
						? $i18n.t('You do not have permission to upload files.')
						: ''}
				className="w-full"
			>
				<DropdownMenu.Item
					class="flex gap-2 items-center px-3 py-2 text-sm  font-medium cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800  rounded-xl {!fileUploadEnabled
						? 'opacity-50'
						: ''}"
					on:click={() => {
						if (fileUploadEnabled) {
							if (!detectMobile()) {
								screenCaptureHandler();
							} else {
								const cameraInputElement = document.getElementById('camera-input');

								if (cameraInputElement) {
									cameraInputElement.click();
								}
							}
						}
					}}
				>
					<CameraSolid />
					<div class=" line-clamp-1">{$i18n.t('Capture')}</div>
				</DropdownMenu.Item>
			</Tooltip>

			<Tooltip
				content={fileUploadCapableModels.length !== selectedModels.length
					? $i18n.t('Model(s) do not support file upload')
					: !fileUploadEnabled
						? $i18n.t('You do not have permission to upload files.')
						: ''}
				className="w-full"
			>
				<DropdownMenu.Item
					class="flex gap-2 items-center px-3 py-2 text-sm font-medium cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800 rounded-xl {!fileUploadEnabled
						? 'opacity-50'
						: ''}"
					on:click={() => {
						if (fileUploadEnabled) {
							uploadFilesHandler();
						}
					}}
				>
					<DocumentArrowUpSolid />
					<div class=" line-clamp-1">{$i18n.t('Upload Files')}</div>
				</DropdownMenu.Item>
			</Tooltip>

			{#if $config?.features?.google_drive_integration && $config?.google_drive?.client_id && $config?.google_drive?.api_key}
				<DropdownMenu.Item
					class="flex gap-2 items-center px-3 py-2 text-sm font-medium cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800 rounded-xl"
					on:click={handleGoogleDriveUpload}
				>
					<PhotoSolid />
					<div class=" line-clamp-1">{$i18n.t('Google Drive')}</div>
				</DropdownMenu.Item>
			{/if}

			{#if $config?.features?.onedrive_integration}
				{#if $config?.features?.onedrive_directory_support}
					<DropdownMenu.Sub>
						<DropdownMenu.SubTrigger
							class="flex gap-2 items-center px-3 py-2 text-sm font-medium cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800 rounded-xl"
						>
							<PhotoSolid />
							<div class=" line-clamp-1">{$i18n.t('OneDrive')}</div>
						</DropdownMenu.SubTrigger>
						<DropdownMenu.SubContent
							transition={flyAndScale}
							transitionConfig={{ x: -10, y: 0 }}
							class="w-full rounded-xl px-1 py-1 border border-gray-300/30 dark:border-gray-700/50 z-50 bg-white dark:bg-gray-850 dark:text-white shadow-sm"
						>
							<DropdownMenu.Item
								class="flex gap-2 items-center px-3 py-2 text-sm font-medium cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800 rounded-xl"
								on:click={() => handleOneDriveUpload('files')}
							>
								<div class=" line-clamp-1">{$i18n.t('Select Files')}</div>
							</DropdownMenu.Item>
							<DropdownMenu.Item
								class="flex gap-2 items-center px-3 py-2 text-sm font-medium cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800 rounded-xl"
								on:click={() => handleOneDriveUpload('directory')}
							>
								<div class=" line-clamp-1">{$i18n.t('Select a Directory')}</div>
							</DropdownMenu.Item>
						</DropdownMenu.SubContent>
					</DropdownMenu.Sub>
				{:else}
					<DropdownMenu.Item
						class="flex gap-2 items-center px-3 py-2 text-sm font-medium cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800 rounded-xl"
						on:click={handleOneDriveUpload}
					>
						<PhotoSolid />
						<div class=" line-clamp-1">{$i18n.t('Microsoft OneDrive')}</div>
					</DropdownMenu.Item>
				{/if}
			{/if}
		</DropdownMenu.Content>
	</div>
</Dropdown>

<!-- Camera input for mobile -->
<input
	id="camera-input"
	bind:this={cameraInputElement}
	type="file"
	accept="image/*"
	capture="environment"
	style="display: none;"
	on:change={async (e) => {
		if (e.target.files && e.target.files.length > 0) {
			const file = e.target.files[0];
			inputFilesHandler([file]);
		}
		e.target.value = '';
	}}
/>

<div
	class=" fixed w-full h-full flex z-50 touch-none pointer-events-none"
	on:drop={onDrop}
	on:dragover={(e) => {
		e.preventDefault();
	}}
/>

<style>
	input[type='file']::file-selector-button {
		display: none;
	}
</style>