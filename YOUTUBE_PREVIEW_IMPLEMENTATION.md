# YouTube Preview Implementation in Open WebUI Notes

## Overview
This implementation adds YouTube video preview functionality to the notes feature in Open WebUI. When users paste or type YouTube URLs in their notes, they are automatically converted to embedded video players with thumbnail previews.

## Implementation Details

### 1. YouTube Extension (`src/lib/components/common/RichTextInput/Youtube/`)
- **youtube.ts**: Core TipTap extension that detects YouTube URLs and converts them to embedded players
- **index.ts**: Export wrapper for the YouTube extension

### 2. Key Features
- **Automatic URL Detection**: Detects YouTube URLs when pasted or typed
- **Thumbnail Preview**: Shows video thumbnail with play button overlay
- **Lazy Loading**: Only loads iframe when user clicks play (better performance)
- **Multiple URL Format Support**:
  - Standard: `https://www.youtube.com/watch?v=VIDEO_ID`
  - Short: `https://youtu.be/VIDEO_ID`
  - Mobile: `https://m.youtube.com/watch?v=VIDEO_ID`
  - Embed: `https://www.youtube.com/embed/VIDEO_ID`
  - With timestamps: `?t=42` or `&t=42`
- **Responsive Design**: 16:9 aspect ratio maintained
- **Dark Mode Support**: Proper styling for both light and dark themes
- **Draggable**: Videos can be repositioned within the editor
- **Selectable/Deletable**: Standard editor operations work as expected

### 3. Integration Points
- **RichTextInput.svelte**: Added `youtube` prop and YouTube extension to editor
- **NoteEditor.svelte**: Enabled YouTube support with `youtube={true}`
- **app.css**: Added styling for YouTube containers and overlays

### 4. User Experience
1. User pastes/types a YouTube URL
2. URL is automatically converted to an embedded preview
3. Preview shows video thumbnail with play button
4. Clicking play loads the YouTube iframe and starts playback
5. Video can be selected, moved, or deleted like any other content

## Testing
Use the test file `test-youtube-urls.md` to verify different YouTube URL formats work correctly.

## Future Enhancements
- Add support for start/end time parameters
- Add video title fetching via YouTube API
- Add support for playlists
- Add privacy-enhanced mode (youtube-nocookie.com)
- Add size adjustment controls