"""Data models representing tweets and threads."""

from datetime import datetime
from typing import Any, Literal
from pydantic import BaseModel, Field


class MediaItem(BaseModel):
    """Represents a media attachment in a tweet."""
    type: Literal["photo", "video", "animated_gif"]
    url: str
    local_filename: str | None = None
    local_path: str | None = None
    bitrate: int | None = None
    duration_ms: int | None = None
    thumbnail_url: str | None = None


class QuotedTweet(BaseModel):
    """Summary of a quoted tweet."""
    id: str
    author_name: str
    author_username: str
    text: str
    url: str
    created_at: datetime | None = None


class TweetItem(BaseModel):
    """Represents a single tweet inside a thread."""
    id: str
    order: int = 1
    author_name: str
    author_username: str
    author_avatar: str = ""
    is_author: bool = True
    created_at: datetime
    created_at_formatted: str = ""
    text: str
    url: str
    likes: int = 0
    retweets: int = 0
    replies: int = 0
    views: int | None = None
    bookmarks: int = 0
    media: list[MediaItem] = Field(default_factory=list)
    reply_to_id: str | None = None
    quote: QuotedTweet | None = None


class Thread(BaseModel):
    """Represents a complete reconstructed thread."""
    root_id: str
    author_name: str
    author_username: str
    author_avatar: str = ""
    title: str
    created_at: datetime
    original_url: str
    total_tweets: int
    tweets: list[TweetItem]
    total_likes: int = 0
    total_retweets: int = 0
    total_views: int = 0
    fetched_at: datetime = Field(default_factory=datetime.now)

    @property
    def slug(self) -> str:
        """Safe directory/file name slug for the thread."""
        safe_title = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in self.title[:40])
        safe_title = safe_title.strip("_").lower() or "thread"
        return f"{self.author_username}_{self.root_id}_{safe_title}"
