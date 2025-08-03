# How to Enable Web Search in Open WebUI

The web search/browsing functionality is disabled by default in Open WebUI. Here's how to enable it:

## Method 1: Environment Variable (Recommended for Docker)

Set the environment variable when starting Open WebUI:

```bash
ENABLE_WEB_SEARCH=true docker-compose up -d
```

Or add it to your `docker-compose.yml`:

```yaml
services:
  open-webui:
    environment:
      - ENABLE_WEB_SEARCH=true
```

## Method 2: Through the Admin Settings UI

1. Log in as an admin user
2. Navigate to **Settings** → **Admin Settings** → **Web Search**
3. Toggle the **Web Search** switch to enable it
4. Select a search engine from the dropdown:
   - **DuckDuckGo** (no API key required - easiest option)
   - **Tavily** (requires API key from tavily.com)
   - **Searxng** (requires self-hosted instance)
   - **Google PSE** (requires Google API key)
   - **Brave** (requires Brave Search API key)
   - And many others...

5. Configure the selected search engine (if required)
6. Click **Save** at the bottom

## Method 3: Direct Configuration File

Edit the configuration directly:

```bash
# For local development
export ENABLE_WEB_SEARCH=true
python backend/open_webui/main.py
```

## Recommended Search Engines

### For Quick Setup (No API Key Required):
- **DuckDuckGo** - Works out of the box, no configuration needed

### For Better Results (API Key Required):
- **Tavily** - Optimized for AI applications, good results
  - Get API key from: https://tavily.com
- **Perplexity** - Excellent for research queries
  - Get API key from: https://www.perplexity.ai/settings/api

## Troubleshooting

1. **Web Search Toggle Not Visible**: Make sure you're logged in as an admin user
2. **Search Not Working After Enabling**: 
   - Check that you've selected a search engine
   - For engines requiring API keys, ensure the key is valid
   - Restart the application after making changes
3. **DuckDuckGo Not Working**: This is usually the most reliable option without API keys

## Testing Web Search

After enabling:
1. Start a new chat
2. Ask a question that requires current information, like "What's the weather today in New York?"
3. The AI should indicate it's searching the web and provide current results

## Security Note

Web search allows the AI to access external websites. Ensure you trust the search engine provider and understand the privacy implications.