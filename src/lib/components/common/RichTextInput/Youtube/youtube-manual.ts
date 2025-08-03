import { mergeAttributes, Node } from '@tiptap/core';

export interface YoutubeOptions {
	/**
	 * Controls if the iframe should be allowed to enter fullscreen
	 * @default true
	 * @example false
	 */
	allowFullscreen: boolean;

	/**
	 * Controls if the iframe should autoplay
	 * @default false
	 * @example true
	 */
	autoplay: boolean;

	/**
	 * HTML attributes to add to the YouTube iframe element
	 * @default {}
	 * @example { class: 'youtube-embed' }
	 */
	HTMLAttributes: Record<string, any>;

	/**
	 * Controls if the video should play inline on mobile devices
	 * @default false
	 * @example true
	 */
	inline: boolean;

	/**
	 * Controls the width of the iframe
	 * @default 640
	 * @example 560
	 */
	width: number;

	/**
	 * Controls the height of the iframe
	 * @default 360
	 * @example 315
	 */
	height: number;
}

declare module '@tiptap/core' {
	interface Commands<ReturnType> {
		youtube: {
			/**
			 * Insert a YouTube video
			 * @param options The YouTube video options
			 * @example
			 * editor.commands.setYoutubeVideo({
			 *   src: 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
			 * })
			 */
			setYoutubeVideo: (options: { src: string; start?: number }) => ReturnType;
			/**
			 * Convert all YouTube URLs in the document to video embeds
			 */
			convertYoutubeUrls: () => ReturnType;
		};
	}
}

const YOUTUBE_REGEX = /^(https?:\/\/)?(www\.|music\.)?(youtube\.com|youtu\.be)(?!.*\/channel\/)(?!\/@)(.+)?$/;
const YOUTUBE_REGEX_GLOBAL = /(https?:\/\/)?(www\.|music\.)?(youtube\.com|youtu\.be)(?!.*\/channel\/)(?!\/@)([^\s]+)/g;

function getYoutubeVideoId(url: string): string | null {
	// Remove any trailing slash
	url = url.replace(/\/$/, '');

	// Extract video ID from various YouTube URL formats
	const patterns = [
		/(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/|youtube\.com\/v\/|youtube\.com\/watch\?.*&v=)([^#&?]*).*/,
		/^([^#&?]*).*/
	];

	for (const pattern of patterns) {
		const match = url.match(pattern);
		if (match && match[1] && match[1].length === 11) {
			return match[1];
		}
	}

	// If URL is already just the video ID
	if (url.length === 11 && /^[\w-]+$/.test(url)) {
		return url;
	}

	return null;
}

function getEmbedUrlFromYoutubeUrl(url: string): string | null {
	const videoId = getYoutubeVideoId(url);
	if (!videoId) {
		return null;
	}

	// Extract start time if present
	const timeMatch = url.match(/[?&]t=(\d+)/);
	const startTime = timeMatch ? timeMatch[1] : null;

	return `https://www.youtube.com/embed/${videoId}${startTime ? `?start=${startTime}` : ''}`;
}

export const YoutubeManual = Node.create<YoutubeOptions>({
	name: 'youtube',

	addOptions() {
		return {
			allowFullscreen: true,
			autoplay: false,
			HTMLAttributes: {},
			inline: false,
			width: 480,
			height: 270
		};
	},

	inline() {
		return this.options.inline;
	},

	group() {
		return this.options.inline ? 'inline' : 'block';
	},

	draggable: true,

	addAttributes() {
		return {
			src: {
				default: null
			},
			start: {
				default: 0
			},
			width: {
				default: this.options.width
			},
			height: {
				default: this.options.height
			}
		};
	},

	parseHTML() {
		return [
			{
				tag: 'div[data-youtube-video] iframe'
			}
		];
	},

	renderHTML({ HTMLAttributes }) {
		const embedUrl = getEmbedUrlFromYoutubeUrl(HTMLAttributes.src);
		if (!embedUrl) {
			return ['div', { class: 'youtube-error' }, 'Invalid YouTube URL'];
		}

		const videoId = getYoutubeVideoId(HTMLAttributes.src);
		const thumbnailUrl = `https://img.youtube.com/vi/${videoId}/maxresdefault.jpg`;

		return [
			'div',
			{
				'data-youtube-video': '',
				class: 'youtube-container relative rounded-lg overflow-hidden bg-gray-100 dark:bg-gray-800'
			},
			[
				'div',
				{
					class: 'youtube-wrapper relative w-full',
					style: `padding-bottom: ${(HTMLAttributes.height / HTMLAttributes.width) * 100}%`
				},
				[
					'iframe',
					mergeAttributes(
						{
							src: embedUrl,
							frameborder: 0,
							allow: 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture',
							allowfullscreen: this.options.allowFullscreen,
							class: 'absolute top-0 left-0 w-full h-full'
						},
						this.options.HTMLAttributes,
						HTMLAttributes
					)
				]
			]
		];
	},

	addNodeView() {
		return ({ node, editor, getPos }) => {
			const dom = document.createElement('div');
			dom.setAttribute('data-youtube-video', '');
			dom.classList.add(
				'youtube-container',
				'relative',
				'rounded-lg',
				'overflow-hidden',
				'bg-gray-100',
				'dark:bg-gray-800',
				'my-4'
			);

			const videoId = getYoutubeVideoId(node.attrs.src);
			if (!videoId) {
				dom.textContent = 'Invalid YouTube URL';
				return { dom };
			}

			const embedUrl = getEmbedUrlFromYoutubeUrl(node.attrs.src);
			const thumbnailUrl = `https://img.youtube.com/vi/${videoId}/maxresdefault.jpg`;

			// Create wrapper for aspect ratio
			const wrapper = document.createElement('div');
			wrapper.classList.add('youtube-wrapper', 'relative', 'w-full');
			wrapper.style.paddingBottom = `${(node.attrs.height / node.attrs.width) * 100}%`;

			// Create placeholder with thumbnail
			const placeholder = document.createElement('div');
			placeholder.classList.add(
				'youtube-placeholder',
				'absolute',
				'top-0',
				'left-0',
				'w-full',
				'h-full',
				'cursor-pointer',
				'group'
			);

			// Add thumbnail
			const thumbnail = document.createElement('img');
			thumbnail.src = thumbnailUrl;
			thumbnail.alt = 'YouTube video thumbnail';
			thumbnail.classList.add('w-full', 'h-full', 'object-cover');
			
			// Add fallback for failed thumbnail loads
			thumbnail.onerror = () => {
				thumbnail.src = `https://img.youtube.com/vi/${videoId}/hqdefault.jpg`;
			};

			// Add play button overlay
			const playButton = document.createElement('div');
			playButton.classList.add(
				'absolute',
				'top-1/2',
				'left-1/2',
				'transform',
				'-translate-x-1/2',
				'-translate-y-1/2',
				'bg-black',
				'bg-opacity-60',
				'rounded-full',
				'w-12',
				'h-12',
				'flex',
				'items-center',
				'justify-center',
				'group-hover:bg-opacity-80',
				'transition-all'
			);

			const playIcon = document.createElement('svg');
			playIcon.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
			playIcon.setAttribute('width', '20');
			playIcon.setAttribute('height', '20');
			playIcon.setAttribute('viewBox', '0 0 24 24');
			playIcon.setAttribute('fill', 'white');
			playIcon.style.cssText = 'margin-left: 2px; color: white;';
			playIcon.innerHTML = '<path d="M8 5v14l11-7z" fill="white" stroke="none"/>';

			playButton.appendChild(playIcon);
			placeholder.appendChild(thumbnail);
			placeholder.appendChild(playButton);

			// Handle click to load iframe
			let iframeLoaded = false;
			placeholder.addEventListener('click', () => {
				if (!iframeLoaded) {
					const iframe = document.createElement('iframe');
					iframe.src = embedUrl + (embedUrl.includes('?') ? '&' : '?') + 'autoplay=1';
					iframe.setAttribute('frameborder', '0');
					iframe.setAttribute(
						'allow',
						'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture'
					);
					iframe.setAttribute('allowfullscreen', 'true');
					iframe.classList.add('absolute', 'top-0', 'left-0', 'w-full', 'h-full');

					wrapper.removeChild(placeholder);
					wrapper.appendChild(iframe);
					iframeLoaded = true;
				}
			});

			// Add title bar with URL
			const titleBar = document.createElement('div');
			titleBar.classList.add(
				'youtube-title-bar',
				'absolute',
				'top-0',
				'left-0',
				'right-0',
				'bg-black',
				'bg-opacity-70',
				'text-white',
				'text-sm',
				'px-3',
				'py-1',
				'opacity-0',
				'group-hover:opacity-100',
				'transition-opacity'
			);
			titleBar.textContent = node.attrs.src;

			wrapper.appendChild(placeholder);
			wrapper.appendChild(titleBar);
			dom.appendChild(wrapper);

			return {
				dom,
				ignoreMutation: () => true
			};
		};
	},

	addCommands() {
		return {
			setYoutubeVideo:
				(options) =>
				({ commands }) => {
					if (!isValidYoutubeUrl(options.src)) {
						return false;
					}

					return commands.insertContent({
						type: this.name,
						attrs: options
					});
				},
			convertYoutubeUrls:
				() =>
				({ state, dispatch, tr }) => {
					const { doc } = state;
					const transaction = tr || state.tr;
					let hasChanges = false;

					doc.descendants((node, pos) => {
						if (node.isText && node.text) {
							const matches = [...node.text.matchAll(YOUTUBE_REGEX_GLOBAL)];
							
							// Process matches in reverse order to maintain correct positions
							for (let i = matches.length - 1; i >= 0; i--) {
								const match = matches[i];
								const url = match[0];
								const startPos = pos + (match.index || 0);
								
								if (isValidYoutubeUrl(url)) {
									const youtubeNode = state.schema.nodes.youtube.create({
										src: url
									});
									
									transaction.replaceWith(
										startPos,
										startPos + url.length,
										youtubeNode
									);
									hasChanges = true;
								}
							}
						}
					});

					if (hasChanges && dispatch) {
						dispatch(transaction);
					}

					return hasChanges;
				}
		};
	},

	// Remove automatic conversion rules
	addPasteRules() {
		return [];
	},

	// Remove automatic conversion rules
	addInputRules() {
		return [];
	}
});

function isValidYoutubeUrl(url: string): boolean {
	return YOUTUBE_REGEX.test(url) && getYoutubeVideoId(url) !== null;
}