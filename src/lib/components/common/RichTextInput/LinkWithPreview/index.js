import { Link } from '@tiptap/extension-link';
import { Plugin, PluginKey } from 'prosemirror-state';
import { Decoration, DecorationSet } from 'prosemirror-view';

export default Link.extend({
  name: 'link', // Keep the name as 'link' for compatibility with existing content

  addOptions() {
    return {
      ...this.parent?.(),
      openOnClick: false,
      onPreviewClick: null,
      HTMLAttributes: {
        class: 'text-blue-600 dark:text-blue-400 hover:underline cursor-pointer',
      },
    };
  },

  onCreate() {
    // Force update decorations when extension is created
    setTimeout(() => {
      if (this.editor && this.editor.view) {
        this.editor.view.updateState(this.editor.state);
      }
    }, 0);
  },

  addProseMirrorPlugins() {
    const parent = this.parent?.() || [];
    const extensionOptions = this.options;
    
    return [
      ...parent,
      new Plugin({
        key: new PluginKey('linkPreview'),
        state: {
          init(_, state) {
            return DecorationSet.empty;
          },
          apply(tr, decorationSet, oldState, newState) {
            // Rebuild decorations on every transaction
            const decorations = [];
            const { doc } = newState;
            
            doc.descendants((node, pos) => {
              if (node.isText) {
                // Check all marks on this text node
                node.marks.forEach(mark => {
                  if (mark.type.name === 'link') {
                    const href = mark.attrs.href;
                    if (!href) return;
                    
                    // Check if it's a YouTube link
                    const youtubeRegex = /(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]+)/;
                    const isYouTube = youtubeRegex.test(href);
                    
                    if (isYouTube || href.startsWith('http')) {
                      // Create a decoration that adds a preview button after the text
                      const endPos = pos + node.nodeSize;
                      const deco = Decoration.widget(endPos, () => {
                        const button = document.createElement('button');
                        button.className = 'link-preview-button';
                        button.style.cssText = 'display: inline-flex; align-items: center; justify-content: center; width: 20px; height: 20px; padding: 2px; margin-left: 4px; border-radius: 4px; background: transparent; border: none; cursor: pointer; vertical-align: middle; color: currentColor;';
                        button.innerHTML = `
                          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" style="width: 14px; height: 14px;">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z" />
                            <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                          </svg>
                        `;
                        button.title = isYouTube ? 'Preview YouTube video' : 'Preview link';
                        button.contentEditable = 'false';
                        
                        // Add hover effect with dark mode support
                        button.onmouseenter = () => {
                          const isDark = document.documentElement.classList.contains('dark');
                          button.style.background = isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)';
                        };
                        button.onmouseleave = () => {
                          button.style.background = 'transparent';
                        };
                        
                        button.onclick = (e) => {
                          e.preventDefault();
                          e.stopPropagation();
                          
                          if (extensionOptions.onPreviewClick) {
                            extensionOptions.onPreviewClick(href, endPos, isYouTube);
                          }
                        };
                        return button;
                      }, { side: 0 });
                      
                      decorations.push(deco);
                    }
                  }
                });
              }
            });
            
            return DecorationSet.create(doc, decorations);
          }
        },
        props: {
          decorations(state) {
            return this.getState(state);
          },
        },
      })
    ];
  },
});