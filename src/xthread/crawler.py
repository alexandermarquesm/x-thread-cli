"""High-performance Twitter/X thread crawler and narrative reconstructor."""

import re
from datetime import datetime
from collections import defaultdict
from typing import AsyncGenerator
from twscrape import Tweet, API
from twscrape.models import MediaPhoto, MediaVideo, MediaAnimated

from xthread.auth import get_api
from xthread.models import Thread, TweetItem, MediaItem, QuotedTweet


def extract_tweet_id(url_or_id: str) -> int:
    """Extract numeric tweet ID from any X/Twitter URL or raw ID string."""
    cleaned = str(url_or_id).strip()
    match = re.search(r"(?:status(?:es)?|i/web/status)/(\d+)", cleaned)
    if match:
        return int(match.group(1))

    match_num = re.search(r"^\d+$", cleaned)
    if match_num:
        return int(cleaned)

    raise ValueError(f"Não foi possível extrair um ID de tweet válido de: '{url_or_id}'")


def get_best_media_urls(tweet: Tweet) -> list[MediaItem]:
    """Extract high-resolution media attachments from a Tweet."""
    media_items: list[MediaItem] = []

    if not tweet.media:
        return media_items

    # 1. Photos (Get full/original resolution)
    for photo in tweet.media.photos:
        orig_url = photo.url
        if "pbs.twimg.com/media" in orig_url:
            # Upgrade to original quality
            if "?" in orig_url:
                base = orig_url.split("?")[0]
                orig_url = f"{base}?name=orig"
            elif not orig_url.endswith(":orig"):
                orig_url = f"{orig_url}:orig"

        media_items.append(
            MediaItem(
                type="photo",
                url=orig_url,
            )
        )

    # 2. Videos (Select highest bitrate mp4)
    for video in tweet.media.videos:
        mp4_variants = [
            v for v in video.variants
            if getattr(v, "contentType", "") == "video/mp4" or "video/mp4" in getattr(v, "content_type", "")
        ]
        if mp4_variants:
            best = max(mp4_variants, key=lambda x: getattr(x, "bitrate", 0))
            media_items.append(
                MediaItem(
                    type="video",
                    url=best.url,
                    bitrate=best.bitrate,
                    duration_ms=video.duration,
                    thumbnail_url=video.thumbnailUrl,
                )
            )

    # 3. Animated GIFs
    for anim in tweet.media.animated:
        if anim.videoUrl:
            media_items.append(
                MediaItem(
                    type="animated_gif",
                    url=anim.videoUrl,
                    thumbnail_url=anim.thumbnailUrl,
                )
            )

    return media_items


def format_tweet_text(tweet: Tweet) -> str:
    """Clean and prepare tweet text."""
    text = tweet.rawContent or ""

    # Note tweets or long tweets sometimes end with t.co media links; keep text clean
    # Remove trailing media t.co links if they only link to the embedded media
    return text.strip()


def tweet_to_item(tweet: Tweet, order: int, is_author: bool) -> TweetItem:
    """Convert twscrape Tweet to internal TweetItem model."""
    quote_item = None
    if tweet.quotedTweet:
        qt = tweet.quotedTweet
        qt_author = qt.user.username if qt.user else "desconhecido"
        qt_name = qt.user.displayname if qt.user else qt_author
        quote_item = QuotedTweet(
            id=str(qt.id),
            author_name=qt_name,
            author_username=qt_author,
            text=qt.rawContent or "",
            url=qt.url,
            created_at=qt.date,
        )

    dt_str = tweet.date.strftime("%d/%m/%Y às %H:%M:%S") if tweet.date else ""

    return TweetItem(
        id=str(tweet.id),
        order=order,
        author_name=tweet.user.displayname if tweet.user else "Autor",
        author_username=tweet.user.username if tweet.user else "autor",
        author_avatar=tweet.user.profileImageUrl if tweet.user else "",
        is_author=is_author,
        created_at=tweet.date,
        created_at_formatted=dt_str,
        text=format_tweet_text(tweet),
        url=tweet.url,
        likes=tweet.likeCount or 0,
        retweets=tweet.retweetCount or 0,
        replies=tweet.replyCount or 0,
        views=tweet.viewCount,
        bookmarks=tweet.bookmarkedCount or 0,
        media=get_best_media_urls(tweet),
        reply_to_id=str(tweet.inReplyToTweetId) if tweet.inReplyToTweetId else None,
        quote=quote_item,
    )


class ThreadCrawler:
    """Orchestrates thread discovery, timeline pagination, and narrative reconstruction."""

    def __init__(self, api: API | None = None):
        self.api = api or get_api()

    async def fetch_thread(
        self,
        url_or_id: str,
        include_all_replies: bool = False,
        limit: int = 150,
    ) -> Thread:
        """Fetch and reconstruct an entire thread starting from any tweet in it."""
        tweet_id = extract_tweet_id(url_or_id)

        # 1. Fetch initial target tweet
        target_tweet = await self.api.tweet_details(tweet_id)
        if not target_tweet:
            raise RuntimeError(
                f"Tweet {tweet_id} não encontrado. Verifique se o link está correto, se o tweet não foi apagado ou se a sessão está autenticada."
            )

        root_id = target_tweet.conversationId or target_tweet.id

        # 2. If the user provided a reply tweet, fetch the true root tweet
        if root_id != target_tweet.id:
            root_tweet = await self.api.tweet_details(root_id)
            if not root_tweet:
                root_tweet = target_tweet
        else:
            root_tweet = target_tweet

        author_username = root_tweet.user.username.lower()
        author_display = root_tweet.user.displayname
        author_avatar = root_tweet.user.profileImageUrl or ""

        # 3. Collect all tweets in the conversation
        collected_map: dict[int, Tweet] = {root_tweet.id: root_tweet, target_tweet.id: target_tweet}

        try:
            async for reply in self.api.tweet_thread(root_id, limit=limit):
                collected_map[reply.id] = reply
        except Exception as e:
            # Twscrape can occasionally complete with no more pages or minor exception
            pass

        # 4. Filter according to mode (author only vs all replies)
        if not include_all_replies:
            tweets_pool = [
                t for t in collected_map.values()
                if t.user and t.user.username.lower() == author_username
            ]
        else:
            tweets_pool = list(collected_map.values())

        # 5. Narrative Tree Reconstruction
        # The author's thread forms a tree starting at root_id.
        children_map: dict[int, list[Tweet]] = defaultdict(list)
        for t in tweets_pool:
            if t.id == root_tweet.id:
                continue
            parent = t.inReplyToTweetId or root_tweet.id
            children_map[parent].append(t)

        # Sort children by creation date
        for parent_id in children_map:
            children_map[parent_id].sort(key=lambda x: x.date if x.date else datetime.min)

        # Depth-First Search traversal to reconstruct chronological thread sequence
        ordered_tweets: list[Tweet] = [root_tweet]
        visited: set[int] = {root_tweet.id}

        def traverse(current_id: int):
            for child in children_map.get(current_id, []):
                if child.id not in visited:
                    visited.add(child.id)
                    ordered_tweets.append(child)
                    traverse(child.id)

        traverse(root_tweet.id)

        # Append any leftover unlinked author tweets in chronological order
        leftovers = [t for t in tweets_pool if t.id not in visited]
        leftovers.sort(key=lambda x: x.date if x.date else datetime.min)
        for t in leftovers:
            ordered_tweets.append(t)

        # 6. Build structured models
        tweet_items: list[TweetItem] = []
        total_likes = 0
        total_retweets = 0
        total_views = 0

        for idx, t in enumerate(ordered_tweets, 1):
            is_author = bool(t.user and t.user.username.lower() == author_username)
            item = tweet_to_item(t, order=idx, is_author=is_author)
            tweet_items.append(item)

            total_likes += item.likes
            total_retweets += item.retweets
            if item.views:
                total_views += item.views

        # Generate a concise, readable title from the first line of the root tweet
        first_line = (root_tweet.rawContent or "").strip().split("\n")[0][:80]
        title = first_line or f"Thread de @{author_username}"

        return Thread(
            root_id=str(root_tweet.id),
            author_name=author_display,
            author_username=author_username,
            author_avatar=author_avatar,
            title=title,
            created_at=root_tweet.date,
            original_url=root_tweet.url,
            total_tweets=len(tweet_items),
            tweets=tweet_items,
            total_likes=total_likes,
            total_retweets=total_retweets,
            total_views=total_views,
        )
