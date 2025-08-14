<script lang="ts">
	import { getContext } from 'svelte';
	import Tooltip from '../common/Tooltip.svelte';
	import RichTextInput from '../common/RichTextInput.svelte';

	const i18n = getContext('i18n');

	export let placeholder = $i18n.t('Send a Message');
	export let transparentBackground = false;
	export let id = null;

	let content = '';
	let chatInputElement;

	export let onSubmit: Function = (e) => {};
	export let onChange: Function = (e) => {};
	export let onStop: Function = (e) => {};

	export let scrollEnd = true;
	export let scrollToBottom: Function = () => {};

	export let acceptFiles = true;
	export let showFormattingButtons = true;

	const sendMessageHandler = async () => {
		if (content.trim() !== '') {
			const messageContent = content;
			content = '';
			chatInputElement.updateModel('');
			onSubmit(messageContent);
		}
	};
</script>

<div class="bg-gray-50 dark:bg-gray-850 relative">
	<div class="px-2.5 pt-2.5 pb-2.5 -mb-0.5 mx-auto max-w-6xl">
		<div class="flex flex-col relative">
			<div class="relative">
				<RichTextInput
					bind:this={chatInputElement}
					bind:value={content}
					{placeholder}
					{showFormattingButtons}
					on:submit={sendMessageHandler}
				/>
			</div>
		</div>
	</div>
</div>