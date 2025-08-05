// Extension to detect standalone URLs and create link preview tokens
export default function linkPreviewExtension(options) {
    return {
        extensions: [
            {
                name: 'linkPreview',
                level: 'block',
                start(src) {
                    // Look for URLs at the start of a line
                    return src.match(/^https?:\/\//)?.index;
                },
                tokenizer(src, tokens) {
                    // Match URLs on their own line - more flexible regex
                    const match = src.match(/^(https?:\/\/[^\s<]+)(?:\s*$|\s*\n)/);
                    
                    if (match) {
                        const url = match[1];
                        console.log('Link preview block extension: URL detected:', url);
                        
                        return {
                            type: 'linkPreview',
                            raw: match[0],
                            url: url,
                            tokens: []
                        };
                    }
                    
                    return null;
                },
                renderer(token) {
                    console.log('Link preview block extension: Rendering token', token);
                    // This will be handled by MarkdownTokens.svelte
                    return '';
                }
            },
            {
                name: 'linkPreviewInline',
                level: 'inline',
                start(src) {
                    // Look for URLs that are standalone (not in markdown link syntax)
                    const match = src.match(/(?:^|\s)(https?:\/\/)/);
                    return match?.index;
                },
                tokenizer(src, tokens) {
                    // Match standalone URLs in text
                    const match = src.match(/^(https?:\/\/[^\s<\]]+)(?=\s|$)/);
                    
                    if (match) {
                        const url = match[1];
                        console.log('Link preview inline extension: URL detected:', url);
                        
                        // Check if this URL is on its own line
                        const fullText = this.lexer?.src || '';
                        const currentIndex = fullText.indexOf(src);
                        const beforeText = fullText.substring(0, currentIndex);
                        const afterText = src.substring(match[0].length);
                        
                        const isStandalone = (beforeText.endsWith('\n') || beforeText === '') && 
                                           (afterText.startsWith('\n') || afterText.startsWith('\r\n') || afterText === '');
                        
                        if (isStandalone) {
                            return {
                                type: 'linkPreviewInline',
                                raw: match[0],
                                url: url
                            };
                        }
                    }
                    
                    return null;
                },
                renderer(token) {
                    console.log('Link preview inline extension: Rendering token', token);
                    return `<span class="link-preview-inline" data-url="${token.url}"></span>`;
                }
            }
        ]
    };
}