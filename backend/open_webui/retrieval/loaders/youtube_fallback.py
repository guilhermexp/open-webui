import logging
import re
from typing import List, Optional
from langchain_core.documents import Document
import requests
from bs4 import BeautifulSoup
from open_webui.env import SRC_LOG_LEVELS

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["RAG"])


class YoutubeFallbackLoader:
    """Fallback loader for YouTube videos when transcript API is rate limited."""
    
    def __init__(self, video_url: str):
        self.video_url = video_url
        self.video_id = self._extract_video_id(video_url)
        
    def _extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from YouTube URL."""
        patterns = [
            r'(?:v=|/)([0-9A-Za-z_-]{11}).*',
            r'(?:embed/)([0-9A-Za-z_-]{11})',
            r'(?:youtu\.be/)([0-9A-Za-z_-]{11})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def load(self) -> List[Document]:
        """Load video metadata from YouTube page."""
        try:
            # Try to get basic video information from the page
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(self.video_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract title
            title = None
            title_meta = soup.find('meta', property='og:title')
            if title_meta:
                title = title_meta.get('content', '')
            
            # Extract description
            description = None
            desc_meta = soup.find('meta', property='og:description')
            if desc_meta:
                description = desc_meta.get('content', '')
            
            # Extract channel name
            channel = None
            channel_link = soup.find('link', itemprop='name')
            if channel_link:
                channel = channel_link.get('content', '')
            
            # Build content
            content_parts = []
            if title:
                content_parts.append(f"Title: {title}")
            if channel:
                content_parts.append(f"Channel: {channel}")
            if description:
                content_parts.append(f"Description: {description}")
            
            if content_parts:
                content = "\n\n".join(content_parts)
                content += f"\n\nNote: Full transcript unavailable due to rate limiting. This is a summary based on video metadata."
                content += f"\n\nVideo URL: {self.video_url}"
                
                metadata = {
                    "source": self.video_url,
                    "title": title or "Unknown",
                    "type": "youtube_metadata"
                }
                
                return [Document(page_content=content, metadata=metadata)]
            else:
                raise Exception("Could not extract any metadata from YouTube page")
                
        except Exception as e:
            log.error(f"Failed to load YouTube metadata: {e}")
            # Return minimal document with just the URL
            content = f"YouTube Video: {self.video_url}\n\nUnable to extract content due to rate limiting. Please try again later or configure a proxy."
            metadata = {
                "source": self.video_url,
                "type": "youtube_fallback"
            }
            return [Document(page_content=content, metadata=metadata)]