# YouTube URL Test Examples

Test these different YouTube URL formats in the notes editor:

## Standard YouTube URLs
- https://www.youtube.com/watch?v=dQw4w9WgXcQ
- https://youtube.com/watch?v=dQw4w9WgXcQ
- http://youtube.com/watch?v=dQw4w9WgXcQ

## YouTube Short URLs
- https://youtu.be/dQw4w9WgXcQ
- http://youtu.be/dQw4w9WgXcQ

## YouTube URLs with timestamps
- https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=42
- https://youtu.be/dQw4w9WgXcQ?t=42

## YouTube Mobile URLs
- https://m.youtube.com/watch?v=dQw4w9WgXcQ
- http://m.youtube.com/watch?v=dQw4w9WgXcQ

## YouTube Embed URLs
- https://www.youtube.com/embed/dQw4w9WgXcQ
- https://youtube.com/embed/dQw4w9WgXcQ

## YouTube URLs with additional parameters
- https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf
- https://www.youtube.com/watch?v=dQw4w9WgXcQ&feature=youtu.be

## Expected Behavior
1. When you paste any of these URLs into the notes editor, they should automatically convert to embedded YouTube players
2. The embed should show a thumbnail preview with a play button
3. Clicking the play button should load the YouTube iframe and start playing
4. The video should respect the aspect ratio (16:9)
5. Dark mode should be properly supported
6. You should be able to select and delete the YouTube embed like any other content
7. The embed should be draggable within the editor