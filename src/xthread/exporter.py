"""Exporters for Markdown, HTML, JSON, and plain text formats."""

import json
from pathlib import Path
from xthread.models import Thread


def export_markdown(thread: Thread, output_file: Path) -> None:
    """Export thread to rich GitHub-flavored Markdown."""
    lines: list[str] = []

    # Frontmatter (YAML metadata for Obsidian / Static Site Generators)
    lines.append("---")
    lines.append(f'title: "{thread.title.replace('"', '\\"')}"')
    lines.append(f'author: "{thread.author_name}"')
    lines.append(f"author_handle: \"@{thread.author_username}\"")
    lines.append(f"root_tweet_id: \"{thread.root_id}\"")
    lines.append(f"total_tweets: {thread.total_tweets}")
    lines.append(f"date: {thread.created_at.isoformat()}")
    lines.append(f"likes: {thread.total_likes}")
    lines.append(f"retweets: {thread.total_retweets}")
    lines.append(f"views: {thread.total_views}")
    lines.append(f'url: "{thread.original_url}"')
    lines.append("---\n")

    # Header
    lines.append(f"# 🧵 {thread.title}\n")
    lines.append(f"**Autor:** [{thread.author_name} (@{thread.author_username})](https://x.com/{thread.author_username})  ")
    lines.append(f"**Data da Publicação:** {thread.created_at.strftime('%d/%m/%Y às %H:%M:%S')}  ")
    lines.append(f"**Thread Original:** [{thread.original_url}]({thread.original_url})  ")
    lines.append(f"**Métricas:** ❤️ {thread.total_likes:,} | 🔁 {thread.total_retweets:,} | 👁️ {thread.total_views:,}\n")
    lines.append("---\n")

    # Tweets
    for item in thread.tweets:
        author_badge = ""
        if not item.is_author:
            author_badge = f" *(Resposta de @{item.author_username})*"

        lines.append(f"### Tweet {item.order}/{thread.total_tweets} • {item.created_at_formatted}{author_badge}\n")

        # Text
        lines.append(f"{item.text}\n")

        # Quoted tweet
        if item.quote:
            lines.append("> 💬 **Citação de @" + item.quote.author_username + "**:")
            for q_line in item.quote.text.split("\n"):
                lines.append(f"> {q_line}")
            lines.append(f">\n> 🔗 [Ver tweet citado]({item.quote.url})\n")

        # Media attachments
        for m_idx, media in enumerate(item.media, 1):
            target = f"media/{media.local_filename}" if media.local_filename else media.url
            if media.type in ("video", "animated_gif"):
                lines.append(f'<video controls src="{target}" width="100%"></video>\n')
            else:
                lines.append(f"![Foto {m_idx}]({target})\n")

        # Tweet metrics & link
        views_str = f" • 👁️ {item.views:,}" if item.views else ""
        lines.append(f"<small>❤️ {item.likes:,} • 🔁 {item.retweets:,}{views_str} • [🔗 Ver no X]({item.url})</small>\n")
        lines.append("---\n")

    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def export_json(thread: Thread, output_file: Path) -> None:
    """Export thread to structured JSON."""
    output_file.parent.mkdir(parents=True, exist_ok=True)
    data = thread.model_dump(mode="json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def export_txt(thread: Thread, output_file: Path) -> None:
    """Export thread to plain text transcript."""
    lines: list[str] = [
        f"THREAD POR @{thread.author_username} ({thread.author_name})",
        f"Data: {thread.created_at.strftime('%d/%m/%Y às %H:%M:%S')}",
        f"URL: {thread.original_url}",
        f"Total de Tweets: {thread.total_tweets}",
        "=" * 60,
        "",
    ]

    for item in thread.tweets:
        lines.append(f"[{item.order}/{thread.total_tweets}] @{item.author_username} - {item.created_at_formatted}")
        lines.append(item.text)
        if item.quote:
            lines.append(f"  [Citação de @{item.quote.author_username}]: {item.quote.text}")
        lines.append("-" * 40)
        lines.append("")

    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def export_html(thread: Thread, output_file: Path) -> None:
    """Export thread to a modern, self-contained standalone HTML reader."""
    output_file.parent.mkdir(parents=True, exist_ok=True)

    tweets_html: list[str] = []
    for item in thread.tweets:
        media_html_parts = []
        for media in item.media:
            src = f"media/{media.local_filename}" if media.local_filename else media.url
            if media.type in ("video", "animated_gif"):
                media_html_parts.append(
                    f'<div class="media-container"><video controls src="{src}"></video></div>'
                )
            else:
                media_html_parts.append(
                    f'<div class="media-container"><a href="{src}" target="_blank"><img src="{src}" loading="lazy" /></a></div>'
                )

        quote_html = ""
        if item.quote:
            quote_html = f"""
            <div class="quote-card">
                <div class="quote-header"><strong>@{item.quote.author_username}</strong></div>
                <div class="quote-text">{item.quote.text}</div>
            </div>
            """

        formatted_text = "<p>" + item.text.replace("\n\n", "</p><p>").replace("\n", "<br>") + "</p>"

        tweets_html.append(f"""
        <article class="tweet-card">
            <header class="tweet-header">
                <div class="tweet-author">
                    <span class="order-badge">#{item.order}</span>
                    <strong class="name">{item.author_name}</strong>
                    <span class="handle">@{item.author_username}</span>
                </div>
                <time class="time">{item.created_at_formatted}</time>
            </header>
            <div class="tweet-content">
                {formatted_text}
                {quote_html}
                {''.join(media_html_parts)}
            </div>
            <footer class="tweet-footer">
                <span>❤️ {item.likes:,}</span>
                <span>🔁 {item.retweets:,}</span>
                <span>👁️ {item.views or 0:,}</span>
                <a href="{item.url}" target="_blank" class="orig-link">Ver no X ↗</a>
            </footer>
        </article>
        """)

    html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{thread.title} - Thread de @{thread.author_username}</title>
    <style>
        :root {{
            --bg: #0f1419;
            --surface: #1e2732;
            --surface-hover: #273340;
            --text: #f7f9f9;
            --text-secondary: #8b98a5;
            --accent: #1d9bf0;
            --border: #2f3336;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            background-color: var(--bg);
            color: var(--text);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6;
            padding: 2rem 1rem;
        }}
        .container {{
            max-width: 680px;
            margin: 0 auto;
        }}
        .thread-meta {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 1.5rem;
            margin-bottom: 2rem;
        }}
        .thread-meta h1 {{
            font-size: 1.4rem;
            margin-bottom: 0.75rem;
            line-height: 1.3;
        }}
        .meta-stats {{
            display: flex;
            gap: 1rem;
            font-size: 0.9rem;
            color: var(--text-secondary);
            margin-top: 0.5rem;
        }}
        .tweet-card {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 1.25rem;
            margin-bottom: 1.25rem;
            position: relative;
        }}
        .tweet-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.75rem;
            font-size: 0.95rem;
        }}
        .order-badge {{
            background: var(--accent);
            color: #fff;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: bold;
            margin-right: 0.4rem;
        }}
        .tweet-author .handle, .time {{
            color: var(--text-secondary);
            font-size: 0.85rem;
        }}
        .tweet-content {{
            font-size: 1.05rem;
            margin-bottom: 1rem;
            word-break: break-word;
        }}
        .quote-card {{
            background: rgba(0, 0, 0, 0.25);
            border-left: 3px solid var(--accent);
            border-radius: 8px;
            padding: 0.75rem 1rem;
            margin: 1rem 0;
            font-size: 0.95rem;
        }}
        .media-container {{
            margin: 0.85rem 0;
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid var(--border);
        }}
        .media-container img, .media-container video {{
            width: 100%;
            height: auto;
            display: block;
        }}
        .tweet-footer {{
            display: flex;
            gap: 1.25rem;
            align-items: center;
            border-top: 1px solid var(--border);
            padding-top: 0.75rem;
            font-size: 0.85rem;
            color: var(--text-secondary);
        }}
        .orig-link {{
            margin-left: auto;
            color: var(--accent);
            text-decoration: none;
        }}
        .orig-link:hover {{ text-decoration: underline; }}
        @media print {{
            body {{ background: #fff; color: #000; }}
            .tweet-card, .thread-meta {{ border-color: #ddd; background: #fff; }}
        }}
    </style>
</head>
<body>
    <main class="container">
        <header class="thread-meta">
            <h1>🧵 {thread.title}</h1>
            <p><strong>{thread.author_name}</strong> (@{thread.author_username}) • {thread.created_at.strftime('%d/%m/%Y às %H:%M')}</p>
            <div class="meta-stats">
                <span>{thread.total_tweets} tweets</span>
                <span>❤️ {thread.total_likes:,}</span>
                <span>🔁 {thread.total_retweets:,}</span>
                <span>👁️ {thread.total_views:,}</span>
            </div>
        </header>

        <section class="timeline">
            {''.join(tweets_html)}
        </section>
    </main>
</body>
</html>
"""
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)
