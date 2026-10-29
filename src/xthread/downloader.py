"""High-performance parallel media downloader."""

import asyncio
from pathlib import Path
from typing import Callable
import httpx
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn, TransferSpeedColumn

from xthread.models import Thread, MediaItem


def get_extension(url: str, default: str = ".jpg") -> str:
    """Extract file extension from URL or query parameters."""
    clean_url = url.split("?")[0]
    path_suffix = Path(clean_url).suffix.lower()
    if path_suffix in (".jpg", ".jpeg", ".png", ".webp", ".gif", ".mp4", ".mov"):
        return path_suffix

    # Check query params like format=jpg
    if "format=jpg" in url or "format=jpeg" in url:
        return ".jpg"
    if "format=png" in url:
        return ".png"
    if "format=webp" in url:
        return ".webp"
    if "format=mp4" in url:
        return ".mp4"

    return default


class MediaDownloader:
    """Asynchronous media downloader for photos and videos."""

    def __init__(self, concurrency: int = 6, timeout: float = 30.0):
        self.semaphore = asyncio.Semaphore(concurrency)
        self.timeout = timeout
        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            "Referer": "https://x.com/",
        }

    async def _download_single(
        self,
        client: httpx.AsyncClient,
        media: MediaItem,
        dest_path: Path,
        on_progress: Callable[[int], None] | None = None,
    ) -> bool:
        """Download one media file asynchronously."""
        async with self.semaphore:
            try:
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                async with client.stream("GET", media.url) as response:
                    if response.status_code != 200:
                        return False

                    with open(dest_path, "wb") as f:
                        async for chunk in response.aiter_bytes(chunk_size=16384):
                            f.write(chunk)
                            if on_progress:
                                on_progress(len(chunk))

                media.local_path = str(dest_path)
                media.local_filename = dest_path.name
                return True
            except Exception:
                return False

    async def download_thread_media(
        self,
        thread: Thread,
        output_dir: Path,
        show_progress: bool = True,
    ) -> int:
        """Download all media for the given thread concurrently."""
        media_dir = output_dir / "media"
        tasks: list[tuple[MediaItem, Path]] = []

        for tweet in thread.tweets:
            for m_idx, media in enumerate(tweet.media, 1):
                ext = ".mp4" if media.type in ("video", "animated_gif") else get_extension(media.url, ".jpg")
                filename = f"tweet_{tweet.order:02d}_{media.type}_{m_idx}{ext}"
                dest_path = media_dir / filename
                tasks.append((media, dest_path))

        if not tasks:
            return 0

        async with httpx.AsyncClient(headers=self.headers, timeout=self.timeout, follow_redirects=True) as client:
            if show_progress:
                with Progress(
                    TextColumn("[bold cyan]{task.description}"),
                    BarColumn(),
                    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                    TransferSpeedColumn(),
                    TimeRemainingColumn(),
                ) as progress:
                    prog_task = progress.add_task(f"Baixando {len(tasks)} mídias...", total=len(tasks))

                    async def worker(item: MediaItem, path: Path):
                        success = await self._download_single(client, item, path)
                        progress.advance(prog_task, 1)
                        return success

                    results = await asyncio.gather(*(worker(m, p) for m, p in tasks))
            else:
                results = await asyncio.gather(*(self._download_single(client, m, p) for m, p in tasks))

        return sum(1 for r in results if r)
