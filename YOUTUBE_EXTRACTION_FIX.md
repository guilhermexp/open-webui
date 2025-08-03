# YouTube Extraction Fix for Open WebUI

## Problem
The YouTube extraction feature was failing with a 429 (Too Many Requests) error when trying to extract transcripts from YouTube videos.

## Solution Implemented

### 1. Enhanced Error Handling
Updated the YouTube loader to provide better error messages:
- Rate limit errors (429) now show a clear message
- Access forbidden errors (403) indicate private/age-restricted videos
- Not found errors (404) suggest checking the URL

### 2. Fallback Mechanism
Created a fallback loader that extracts basic metadata when the transcript API is rate limited:
- Video title
- Channel name
- Description
- Provides a summary when full transcript is unavailable

### 3. Improved Content Formatting
Updated the note enhancement prompt to create well-structured notes:
- Hierarchical headings with # ## ###
- Bold text for important concepts
- Organized sections for YouTube videos
- Better integration of extracted content

## Configuration

### Setting up a YouTube Proxy (Recommended)
To avoid rate limits, you can configure a proxy for YouTube requests:

```bash
# In backend/dev.sh or as environment variable
export YOUTUBE_LOADER_PROXY_URL="http://your-proxy-server:port"
```

### Proxy Options
1. **Public Proxies**: Free but unreliable
2. **Residential Proxies**: More reliable, paid services like:
   - Bright Data
   - Smartproxy
   - Oxylabs
3. **VPN with Proxy**: Use your VPN's proxy server

## Testing

1. Create a new note in Open WebUI
2. Add a YouTube URL (e.g., https://www.youtube.com/watch?v=dQw4w9WgXcQ)
3. Click the "Enhance" button
4. The system will:
   - Try to extract the full transcript
   - Fall back to metadata if rate limited
   - Format the content nicely

## Files Modified

1. `/backend/open_webui/retrieval/loaders/youtube.py` - Better error handling
2. `/backend/open_webui/retrieval/loaders/youtube_fallback.py` - New fallback loader
3. `/backend/open_webui/routers/retrieval.py` - Integration of fallback mechanism
4. `/src/lib/components/notes/NoteEditor.svelte` - Improved formatting prompt

## Current Status

The feature is now working with:
- ✅ Better error messages for rate limits
- ✅ Fallback to metadata extraction when rate limited
- ✅ Improved content formatting
- ⚠️ Full transcript extraction requires proxy configuration to avoid rate limits

## Next Steps

To get full transcript extraction working:
1. Configure a proxy server (see Configuration section)
2. Set the `YOUTUBE_LOADER_PROXY_URL` environment variable
3. Restart the backend server

This will allow the YouTube Transcript API to work without hitting rate limits.