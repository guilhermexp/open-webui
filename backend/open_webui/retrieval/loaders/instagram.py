import logging
import os
import tempfile
from typing import Optional, List, Dict
from urllib.parse import urlparse
import instaloader
from pathlib import Path

from open_webui.env import SRC_LOG_LEVELS

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["RAG"])

ALLOWED_INSTAGRAM_DOMAINS = {
    "instagram.com",
    "www.instagram.com",
    "instagr.am"
}


def _parse_reel_id(url: str) -> Optional[str]:
    """Parse an Instagram URL and return the reel shortcode if valid."""
    try:
        parsed_url = urlparse(url)
        
        if parsed_url.netloc not in ALLOWED_INSTAGRAM_DOMAINS:
            return None
        
        path_parts = parsed_url.path.strip('/').split('/')
        
        # Instagram Reels URLs are typically:
        # https://www.instagram.com/reel/SHORTCODE/
        # https://www.instagram.com/reels/SHORTCODE/
        # https://www.instagram.com/p/SHORTCODE/ (posts that might be reels)
        
        if len(path_parts) >= 2:
            if path_parts[0] in ['reel', 'reels', 'p']:
                return path_parts[1]
        
        return None
    except Exception as e:
        log.error(f"Error parsing Instagram URL: {e}")
        return None


class InstagramReelLoader:
    """Load Instagram Reels and extract audio for transcription."""
    
    def __init__(self):
        self.loader = instaloader.Instaloader(
            download_comments=False,
            download_geotags=False,
            download_video_thumbnails=False,
            save_metadata=False,
            compress_json=False,
            quiet=True
        )
        
    def load(self, url: str) -> List[Dict]:
        """Download Instagram Reel and prepare for transcription."""
        shortcode = _parse_reel_id(url)
        
        if not shortcode:
            log.error(f"Invalid Instagram URL: {url}")
            return []
        
        try:
            # Create temporary directory for download
            with tempfile.TemporaryDirectory() as temp_dir:
                try:
                    # Get post/reel by shortcode
                    post = instaloader.Post.from_shortcode(self.loader.context, shortcode)
                    
                    if not post.is_video:
                        log.warning(f"URL is not a video/reel: {url}")
                        return []
                    
                    # Download the video
                    target_path = Path(temp_dir) / shortcode
                    self.loader.download_post(post, target=target_path)
                    
                    # Find the downloaded video file
                    video_files = list(target_path.glob("*.mp4"))
                    if not video_files:
                        log.error(f"No video file found after download for: {url}")
                        return []
                    
                    video_path = video_files[0]
                    
                    # Extract basic metadata
                    metadata = {
                        "source": url,
                        "type": "instagram_reel",
                        "author": post.owner_username,
                        "caption": post.caption if post.caption else "",
                        "date": post.date_utc.isoformat() if post.date_utc else None,
                        "video_path": str(video_path),
                        "needs_transcription": True
                    }
                    
                    # Return the video file path for audio extraction
                    # The transcription will be handled by the existing whisper integration
                    return [metadata]
                    
                except instaloader.exceptions.InstaloaderException as e:
                    log.error(f"Instaloader error for {url}: {e}")
                    # If it's a login required error, provide helpful message
                    if "Login required" in str(e):
                        log.info("Instagram Reel might be private. Public reels only are supported.")
                    return []
                    
        except Exception as e:
            log.error(f"Unexpected error loading Instagram Reel {url}: {e}")
            return []


def get_instagram_reel_metadata(url: str) -> Optional[Dict]:
    """Get metadata for an Instagram Reel without downloading."""
    shortcode = _parse_reel_id(url)
    
    if not shortcode:
        return None
    
    try:
        loader = instaloader.Instaloader(quiet=True)
        post = instaloader.Post.from_shortcode(loader.context, shortcode)
        
        return {
            "url": url,
            "author": post.owner_username,
            "caption": post.caption if post.caption else "",
            "is_video": post.is_video,
            "date": post.date_utc.isoformat() if post.date_utc else None
        }
    except Exception as e:
        log.error(f"Error getting Instagram metadata: {e}")
        return None