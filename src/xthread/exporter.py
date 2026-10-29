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


# SVG Assets for X and Steam
SVG_X_LOGO = '<svg viewBox="0 0 24 24" class="svg-icon x-logo-svg" fill="currentColor"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 24.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>'

SVG_VERIFIED = '<svg viewBox="0 0 24 24" class="svg-icon verified-badge" fill="currentColor"><path d="M22.25 12c0-1.43-.88-2.67-2.19-3.34.46-1.39.2-2.9-.81-3.91s-2.52-1.27-3.91-.81c-.67-1.31-1.91-2.19-3.34-2.19s-2.67.88-3.33 2.19c-1.4-.46-2.91-.2-3.92.81s-1.26 2.52-.8 3.91c-1.31.67-2.2 1.91-2.2 3.34s.89 2.67 2.2 3.34c-.46 1.39-.21 2.9.8 3.91s2.52 1.26 3.91.81c.67 1.31 1.91 2.19 3.34 2.19s2.67-.88 3.34-2.19c1.39.45 2.9.2 3.91-.81s1.27-2.52.81-3.91c1.31-.67 2.19-1.91 2.19-3.34zm-11.71 4.2L6.8 12.46l1.41-1.42 2.26 2.26 4.8-5.23 1.47 1.36-6.2 6.77z"/></svg>'

SVG_REPLY = '<svg viewBox="0 0 24 24" class="svg-icon" fill="currentColor"><path d="M1.751 10c0-4.42 3.584-8 8.005-8h4.366c4.49 0 8.129 3.64 8.129 8.13 0 2.96-1.607 5.68-4.196 7.11l-1.18.65v2.86c0 1.07-1.24 1.68-2.09 1.02l-3.69-2.89h-1.54c-4.42 0-8.004-3.58-8.004-8zm8.005-6c-3.317 0-6.005 2.69-6.005 6 0 3.32 2.688 6 6.005 6h2.094l3.15 2.47v-1.72l1.62-.89c1.99-1.1 3.23-3.19 3.23-5.46 0-3.38-2.74-6.13-6.129-6.13H9.756z"/></svg>'

SVG_RETWEET = '<svg viewBox="0 0 24 24" class="svg-icon" fill="currentColor"><path d="M4.5 3.88l4.432 4.14-1.364 1.46L5.5 7.55V16c0 1.1.896 2 2 2H13v2H7.5c-2.209 0-4-1.79-4-4V7.55L1.432 9.48.068 8.02 4.5 3.88zM16.5 20.12l-4.432-4.14 1.364-1.46 2.068 1.93V8c0-1.1-.896-2-2-2H11V4h5.5c2.209 0 4 1.79 4 4v8.45l2.068-1.93 1.364 1.46-4.432 4.14z"/></svg>'

SVG_LIKE = '<svg viewBox="0 0 24 24" class="svg-icon" fill="currentColor"><path d="M16.697 5.5c-1.222-.06-2.679.51-3.89 2.16l-.805 1.09-.806-1.09C9.984 6.01 8.526 5.44 7.304 5.5c-2.415.11-4.304 2.15-4.304 4.75 0 3.54 3.294 6.81 8.22 11.08l.78.67.78-.67c4.926-4.27 8.22-7.54 8.22-11.08 0-2.6-1.89-4.64-4.303-4.75zm-4.697 14.54C7.45 16.06 5 13.06 5 10.25c0-1.5 1.07-2.75 2.5-2.75 1.25 0 2.45 1.05 2.9 2.19h3.2c.45-1.14 1.65-2.19 2.9-2.19 1.43 0 2.5 1.25 2.5 2.75 0 2.81-2.45 5.81-7 9.79z"/></svg>'

SVG_VIEWS = '<svg viewBox="0 0 24 24" class="svg-icon" fill="currentColor"><path d="M8.75 21V3h2v18h-2zM18 21V8.5h2V21h-2zM4 21l.004-10h2L6 21H4zm9.248 0v-7h2v7h-2z"/></svg>'

SVG_SHARE = '<svg viewBox="0 0 24 24" class="svg-icon" fill="currentColor"><path d="M12 2.59l5.7 5.7-1.41 1.42L13 6.41V16h-2V6.41L7.71 9.71 6.3 8.29 12 2.59zM21 15l-.02 3.51c0 1.38-1.12 2.49-2.5 2.49H5.5C4.11 21 3 19.88 3 18.5V15h2v3.5c0 .28.22.5.5.5h12.98c.28 0 .5-.22.5-.5L19 15h2z"/></svg>'

SVG_STEAM_LOGO = '<svg viewBox="0 0 24 24" class="steam-logo-svg" fill="currentColor"><path d="M11.979 0C5.678 0 .511 4.86.022 11.037l6.432 2.658c.545-.371 1.203-.59 1.912-.59.063 0 .125.004.188.006l2.861-4.142V8.91c0-2.495 2.028-4.524 4.524-4.524 2.494 0 4.524 2.031 4.524 4.527s-2.03 4.525-4.524 4.525h-.105l-4.076 2.911c0 .052.005.105.005.159 0 1.875-1.515 3.396-3.39 3.396-1.635 0-3.016-1.173-3.331-2.727L.436 15.27C1.862 20.307 6.486 24 11.979 24c6.627 0 12-5.373 12-12S18.605 0 11.979 0zM7.54 18.217l-1.473-.61c.262.543.714.99 1.314 1.238.96.398 2.053.072 2.65-.746l-.004-.004-.849-.352c-.368.504-.988.707-1.638.474zm8.4-11.53c-1.25 0-2.268 1.018-2.268 2.268 0 1.25 1.018 2.268 2.268 2.268 1.25 0 2.268-1.018 2.268-2.268 0-1.25-1.018-2.268-2.268-2.268z"/></svg>'


def export_html(thread: Thread, output_file: Path) -> None:
    """Export thread to an ultra-polished standalone HTML reader with X & Steam Old designs and multi-themes."""
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # 0. Scan other saved threads in library for the right sidebar
    base_dir = output_file.parent.parent
    sidebar_threads_html: list[str] = []
    try:
        from xthread.library import scan_saved_threads
        all_saved = scan_saved_threads(base_dir)
        current_dir_name = output_file.parent.name

        for t in all_saved[:7]:
            is_cur = (t["dir_name"] == current_dir_name)
            cur_class = " is-current" if is_cur else ""
            link_target = f"../{t['html_path']}" if not is_cur else "#"
            badge = " · (Lendo agora)" if is_cur else ""

            sidebar_threads_html.append(f"""
            <a href="{link_target}" class="x-trend-item{cur_class}">
                <div class="trend-category">
                    <span>Thread · @{t['author_username']}{badge}</span>
                    <span class="trend-dots">···</span>
                </div>
                <div class="trend-title">{t['title']}</div>
                <div class="trend-posts">{t['total_tweets']} posts · ❤️ {t['total_likes']:,} curtidas</div>
            </a>
            """)
    except Exception:
        pass

    if not sidebar_threads_html:
        sidebar_threads_html.append(f"""
        <div class="x-trend-item is-current">
            <div class="trend-category">
                <span>Thread · @{thread.author_username} · (Lendo agora)</span>
            </div>
            <div class="trend-title">{thread.title}</div>
            <div class="trend-posts">{thread.total_tweets} posts · ❤️ {thread.total_likes:,} curtidas</div>
        </div>
        """)

    # 1. Generate Tweet Elements for X Timeline
    x_tweets_html: list[str] = []
    steam_list_rows: list[str] = []
    steam_detail_cards: list[str] = []

    avatar_initial = (thread.author_name or "X")[0].upper()

    for idx, item in enumerate(thread.tweets):
        is_last = (idx == len(thread.tweets) - 1)
        line_class = "thread-connector" if not is_last else "thread-connector is-last"

        # Media HTML
        media_html_parts: list[str] = []
        for m_idx, media in enumerate(item.media, 1):
            src = f"media/{media.local_filename}" if media.local_filename else media.url
            if media.type in ("video", "animated_gif"):
                media_html_parts.append(
                    f'<div class="x-media-wrapper"><video controls preload="metadata" class="x-media-video" src="{src}"></video></div>'
                )
            else:
                media_html_parts.append(
                    f'<div class="x-media-wrapper"><a href="{src}" target="_blank" rel="noopener"><img class="x-media-img" src="{src}" loading="lazy" alt="Mídia {m_idx}" /></a></div>'
                )

        media_block = f'<div class="x-media-grid count-{len(item.media)}">{"".join(media_html_parts)}</div>' if media_html_parts else ""

        # Quoted Tweet
        quote_html = ""
        if item.quote:
            quote_html = f"""
            <div class="x-quote-card">
                <div class="x-quote-header">
                    <span class="x-quote-name">{item.quote.author_name}</span>
                    <span class="x-quote-handle">@{item.quote.author_username}</span>
                </div>
                <div class="x-quote-text">{item.quote.text}</div>
            </div>
            """

        formatted_text = "<p>" + item.text.replace("\n\n", "</p><p>").replace("\n", "<br>") + "</p>"

        # X Timeline Tweet Item
        x_tweets_html.append(f"""
        <article class="x-tweet" id="tweet-{item.order}">
            <div class="x-tweet-left">
                <div class="x-avatar">
                    <span>{avatar_initial}</span>
                </div>
                <div class="{line_class}"></div>
            </div>
            <div class="x-tweet-right">
                <div class="x-tweet-header">
                    <div class="x-user-info">
                        <strong class="x-display-name">{item.author_name}</strong>
                        {SVG_VERIFIED}
                        <span class="x-handle">@{item.author_username}</span>
                        <span class="x-dot">·</span>
                        <time class="x-time">{item.created_at_formatted.split(' às ')[-1] if ' às ' in item.created_at_formatted else item.created_at_formatted}</time>
                    </div>
                    <span class="x-order-pill">#{item.order}</span>
                </div>
                <div class="x-tweet-body">
                    {formatted_text}
                    {quote_html}
                    {media_block}
                </div>
                <div class="x-tweet-actions">
                    <div class="x-action action-reply">
                        {SVG_REPLY}
                        <span>{item.replies:,}</span>
                    </div>
                    <div class="x-action action-retweet">
                        {SVG_RETWEET}
                        <span>{item.retweets:,}</span>
                    </div>
                    <div class="x-action action-like">
                        {SVG_LIKE}
                        <span>{item.likes:,}</span>
                    </div>
                    <div class="x-action action-views">
                        {SVG_VIEWS}
                        <span>{item.views or 0:,}</span>
                    </div>
                    <a href="{item.url}" target="_blank" rel="noopener" class="x-action action-share" title="Ver post no X">
                        {SVG_SHARE}
                    </a>
                </div>
            </div>
        </article>
        """)

        # Steam List Row (Classic 2004 VGUI Table)
        preview_snippet = (item.text.split("\n")[0][:45] + "...") if len(item.text) > 45 else item.text
        preview_snippet = preview_snippet.replace('"', '&quot;')
        score = 90 + (idx % 8)

        steam_list_rows.append(f"""
        <tr class="steam-row" onclick="scrollToTweet({item.order})">
            <td class="col-game">
                <span class="steam-lambda-icon">λ</span>
                <span class="steam-game-title">Tweet #{item.order:02d}: {preview_snippet}</span>
            </td>
            <td class="col-status"><span class="steam-star">★</span> 100% - Ready</td>
            <td class="col-metrics">❤️ {item.likes} / 🔁 {item.retweets}</td>
            <td class="col-score"><span class="steam-score-badge">{score}</span></td>
            <td class="col-author">@{item.author_username}</td>
        </tr>
        """)

        # Steam Content Card (Full view in classic VGUI inset)
        steam_detail_cards.append(f"""
        <div class="steam-post-card" id="steam-tweet-{item.order}">
            <div class="steam-post-header">
                <div class="steam-post-title">
                    <span class="steam-badge">ENTRY #{item.order}</span>
                    <strong>{item.author_name}</strong> <span class="steam-muted">(@{item.author_username})</span>
                </div>
                <span class="steam-post-time">{item.created_at_formatted}</span>
            </div>
            <div class="steam-post-body">
                {formatted_text}
                {quote_html}
                {media_block}
            </div>
            <div class="steam-post-footer">
                <div class="steam-stats">
                    <span>STATUS: <strong>VERIFIED</strong></span>
                    <span>LIKES: <strong>{item.likes:,}</strong></span>
                    <span>RETWEETS: <strong>{item.retweets:,}</strong></span>
                    <span>VIEWS: <strong>{item.views or 0:,}</strong></span>
                </div>
                <a href="{item.url}" target="_blank" rel="noopener" class="steam-vgui-btn small">LAUNCH IN X ↗</a>
            </div>
        </div>
        """)

    html_content = f"""<!DOCTYPE html>
<html lang="pt-BR" data-theme="default" data-layout="x-original">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{thread.title} — Thread de @{thread.author_username}</title>
    <style>
        /* ==========================================================================
           COLOR PALETTES & CSS VARIABLES (THEMING ENGINE)
           ========================================================================== */
        :root {{
            /* Default: Authentic X Dark Mode */
            --bg: #000000;
            --surface: #16181c;
            --surface-hover: #1d1f23;
            --surface-active: #272c30;
            --border: #2f3336;
            --border-light: #202327;
            --text: #e7e9ea;
            --text-secondary: #71767b;
            --text-muted: #536471;
            --accent: #1d9bf0;
            --accent-hover: #1a8cd8;
            --accent-light: rgba(29, 155, 240, 0.1);
            --like-color: #f91880;
            --like-hover: rgba(249, 24, 128, 0.1);
            --rt-color: #00ba7c;
            --rt-hover: rgba(0, 186, 124, 0.1);
            --verified-color: #1d9bf0;
            --radius-sm: 8px;
            --radius-md: 16px;
            --radius-lg: 20px;
            --font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            
            /* Steam Old VGUI Authentic Colors */
            --steam-bg: #4c5844;
            --steam-header: #3e4637;
            --steam-chrome: #2d3328;
            --steam-inset: #23271f;
            --steam-card-bg: #353c30;
            --steam-border-light: #637258;
            --steam-border-dark: #1b2016;
            --steam-text: #e1e0b5;
            --steam-text-muted: #95a38a;
            --steam-yellow: #d8d598;
            --steam-yellow-bright: #fffe9a;
            --steam-blue: #7092b3;
            --steam-score: #7394b5;
            --steam-highlight: #58694f;
        }}

        /* Theme: Tokyo Night */
        html[data-theme="tokyo-night"] {{
            --bg: #1a1b26;
            --surface: #24283b;
            --surface-hover: #2f3549;
            --surface-active: #3b4261;
            --border: #292e42;
            --border-light: #1f2335;
            --text: #c0caf5;
            --text-secondary: #7aa2f7;
            --text-muted: #565f89;
            --accent: #7aa2f7;
            --accent-hover: #89b4fa;
            --accent-light: rgba(122, 162, 247, 0.15);
            --like-color: #f7768e;
            --rt-color: #9ece6a;
            --verified-color: #bb9af7;

            --steam-bg: #1f2335;
            --steam-header: #1a1b26;
            --steam-chrome: #16161e;
            --steam-inset: #13141c;
            --steam-card-bg: #24283b;
            --steam-border-light: #3b4261;
            --steam-border-dark: #101014;
            --steam-text: #c0caf5;
            --steam-text-muted: #565f89;
            --steam-yellow: #e0af68;
            --steam-yellow-bright: #ff9e64;
            --steam-blue: #7aa2f7;
            --steam-score: #7dcfff;
            --steam-highlight: #2f3549;
        }}

        /* Theme: Dracula */
        html[data-theme="dracula"] {{
            --bg: #282a36;
            --surface: #343746;
            --surface-hover: #44475a;
            --surface-active: #4a4d62;
            --border: #44475a;
            --border-light: #383a4c;
            --text: #f8f8f2;
            --text-secondary: #bd93f9;
            --text-muted: #6272a4;
            --accent: #bd93f9;
            --accent-hover: #ff79c6;
            --accent-light: rgba(189, 147, 249, 0.15);
            --like-color: #ff5555;
            --rt-color: #50fa7b;
            --verified-color: #ff79c6;

            --steam-bg: #282a36;
            --steam-header: #21222c;
            --steam-chrome: #191a21;
            --steam-inset: #191a21;
            --steam-card-bg: #343746;
            --steam-border-light: #6272a4;
            --steam-border-dark: #15161e;
            --steam-text: #f8f8f2;
            --steam-text-muted: #6272a4;
            --steam-yellow: #f1fa8c;
            --steam-yellow-bright: #ffb86c;
            --steam-blue: #8be9fd;
            --steam-score: #50fa7b;
            --steam-highlight: #44475a;
        }}

        /* Theme: Catppuccin Mocha */
        html[data-theme="catppuccin"] {{
            --bg: #1e1e2e;
            --surface: #252538;
            --surface-hover: #313244;
            --surface-active: #45475a;
            --border: #313244;
            --border-light: #252538;
            --text: #cdd6f4;
            --text-secondary: #bac2de;
            --text-muted: #a6adc8;
            --accent: #89b4fa;
            --accent-hover: #b4befe;
            --accent-light: rgba(137, 180, 250, 0.15);
            --like-color: #f38ba8;
            --rt-color: #a6e3a1;
            --verified-color: #cba6f7;

            --steam-bg: #252538;
            --steam-header: #1e1e2e;
            --steam-chrome: #181825;
            --steam-inset: #11111b;
            --steam-card-bg: #313244;
            --steam-border-light: #45475a;
            --steam-border-dark: #11111b;
            --steam-text: #cdd6f4;
            --steam-text-muted: #a6adc8;
            --steam-yellow: #f9e2af;
            --steam-yellow-bright: #fab387;
            --steam-blue: #89b4fa;
            --steam-score: #a6e3a1;
            --steam-highlight: #363a4f;
        }}

        /* Theme: Clean Daylight */
        html[data-theme="light"] {{
            --bg: #ffffff;
            --surface: #f7f9f9;
            --surface-hover: #eff3f4;
            --surface-active: #e1e8ed;
            --border: #eff3f4;
            --border-light: #f7f9f9;
            --text: #0f1419;
            --text-secondary: #536471;
            --text-muted: #8b98a5;
            --accent: #1d9bf0;
            --accent-hover: #1a8cd8;
            --accent-light: rgba(29, 155, 240, 0.08);
            --like-color: #f91880;
            --rt-color: #00ba7c;
            --verified-color: #1d9bf0;

            --steam-bg: #c0c0c0;
            --steam-header: #a0a0a0;
            --steam-chrome: #808080;
            --steam-inset: #ffffff;
            --steam-card-bg: #eaeaea;
            --steam-border-light: #ffffff;
            --steam-border-dark: #404040;
            --steam-text: #000000;
            --steam-text-muted: #505050;
            --steam-yellow: #806000;
            --steam-yellow-bright: #000080;
            --steam-blue: #000080;
            --steam-score: #005000;
            --steam-highlight: #000080;
        }}

        /* ==========================================================================
           GLOBAL BASE STYLES
           ========================================================================== */
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            background-color: var(--bg);
            color: var(--text);
            font-family: var(--font-family);
            line-height: 1.45;
            -webkit-font-smoothing: antialiased;
            transition: background-color 0.2s ease, color 0.2s ease;
        }}

        a {{
            color: var(--accent);
            text-decoration: none;
        }}

        a:hover {{
            text-decoration: underline;
        }}

        /* ==========================================================================
           STICKY CONTROL TOOLBAR (TOP NAV)
           ========================================================================== */
        .top-toolbar {{
            position: sticky;
            top: 0;
            z-index: 9999;
            background: rgba(15, 20, 25, 0.85);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border-bottom: 1px solid var(--border);
            padding: 8px 16px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
            font-size: 13px;
        }}

        html[data-theme="light"] .top-toolbar {{
            background: rgba(255, 255, 255, 0.88);
        }}

        .toolbar-group {{
            display: flex;
            align-items: center;
            gap: 6px;
        }}

        .toolbar-label {{
            font-size: 11px;
            font-weight: 700;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-right: 4px;
        }}

        .nav-btn {{
            background: var(--surface);
            border: 1px solid var(--border);
            color: var(--text);
            padding: 5px 12px;
            border-radius: 9999px;
            cursor: pointer;
            font-size: 12px;
            font-weight: 600;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            transition: all 0.15s ease;
            white-space: nowrap;
        }}

        .nav-btn:hover {{
            background: var(--surface-hover);
            border-color: var(--accent);
        }}

        .nav-btn.active {{
            background: var(--accent);
            border-color: var(--accent);
            color: #ffffff !important;
        }}

        .theme-select {{
            background: var(--surface);
            border: 1px solid var(--border);
            color: var(--text);
            padding: 5px 10px;
            border-radius: 9999px;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            outline: none;
        }}

        .theme-select:focus {{
            border-color: var(--accent);
        }}

        /* ==========================================================================
           LAYOUT 1: X (TWITTER) ORIGINAL TIMELINE & RIGHT SIDEBAR
           ========================================================================== */
        .layout-x-wrapper {{
            display: none;
            max-width: 1040px;
            margin: 0 auto;
            justify-content: center;
            gap: 30px;
        }}

        html[data-layout="x-original"] .layout-x-wrapper {{
            display: flex;
        }}

        .layout-x-container {{
            width: 600px;
            flex-shrink: 0;
            border-left: 1px solid var(--border);
            border-right: 1px solid var(--border);
            min-height: 100vh;
        }}

        /* X Right Sidebar (Trends & Author Widget) */
        .x-right-sidebar {{
            width: 350px;
            flex-shrink: 0;
            padding-top: 12px;
            display: flex;
            flex-direction: column;
            gap: 16px;
            position: sticky;
            top: 54px;
            height: fit-content;
            max-height: calc(100vh - 60px);
            overflow-y: auto;
        }}

        .x-sidebar-search {{
            position: relative;
            display: flex;
            align-items: center;
        }}

        .search-icon {{
            position: absolute;
            left: 14px;
            width: 18px;
            height: 18px;
            color: var(--text-muted);
            pointer-events: none;
        }}

        .x-sidebar-search input {{
            width: 100%;
            background: var(--surface);
            border: 1px solid var(--border);
            color: var(--text);
            border-radius: 9999px;
            padding: 10px 16px 10px 42px;
            font-size: 14px;
            outline: none;
            transition: border-color 0.15s ease;
        }}

        .x-sidebar-search input:focus {{
            border-color: var(--accent);
        }}

        .x-sidebar-card {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 16px;
            overflow: hidden;
        }}

        .x-card-heading {{
            font-size: 19px;
            font-weight: 800;
            padding: 12px 16px;
            color: var(--text);
            line-height: 1.3;
        }}

        .author-row {{
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 0 16px 14px 16px;
        }}

        .x-avatar.small {{
            width: 40px;
            height: 40px;
            font-size: 15px;
        }}

        .author-info {{
            flex-grow: 1;
            min-width: 0;
        }}

        .author-name-row {{
            display: flex;
            align-items: center;
            gap: 4px;
        }}

        .author-info .x-name {{
            font-size: 15px;
            font-weight: 700;
            color: var(--text);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}

        .author-info .x-handle {{
            font-size: 13px;
            color: var(--text-muted);
            display: block;
        }}

        .x-follow-btn {{
            background: var(--text);
            color: var(--bg) !important;
            border-radius: 9999px;
            padding: 6px 14px;
            font-size: 13px;
            font-weight: 700;
            text-decoration: none;
            white-space: nowrap;
            transition: opacity 0.15s ease;
        }}

        .x-follow-btn:hover {{
            opacity: 0.9;
            text-decoration: none;
        }}

        html[data-theme="light"] .x-follow-btn {{
            background: #0f1419;
            color: #ffffff !important;
        }}

        .x-trend-item {{
            display: block;
            padding: 10px 16px;
            text-decoration: none;
            transition: background-color 0.15s ease;
            border-top: 1px solid var(--border-light);
        }}

        .x-trend-item:hover {{
            background-color: var(--surface-hover);
            text-decoration: none;
        }}

        .x-trend-item.is-current {{
            background-color: var(--surface-hover);
        }}

        .trend-category {{
            font-size: 13px;
            color: var(--text-muted);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .trend-dots {{
            font-size: 16px;
            color: var(--text-muted);
        }}

        .trend-title {{
            font-size: 15px;
            font-weight: 700;
            color: var(--text);
            margin: 3px 0;
            line-height: 1.3;
            overflow: hidden;
            text-overflow: ellipsis;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
        }}

        .trend-posts {{
            font-size: 12px;
            color: var(--text-muted);
        }}

        .x-show-more {{
            display: block;
            padding: 14px 16px;
            color: var(--accent);
            font-size: 14px;
            text-decoration: none;
            border-top: 1px solid var(--border-light);
            transition: background-color 0.15s ease;
        }}

        .x-show-more:hover {{
            background-color: var(--surface-hover);
            text-decoration: none;
        }}

        .x-sidebar-footer {{
            padding: 0 16px 20px 16px;
            font-size: 12px;
            color: var(--text-muted);
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
        }}

        .x-sidebar-footer a {{
            color: var(--text-muted);
            text-decoration: none;
        }}

        .x-sidebar-footer a:hover {{
            text-decoration: underline;
        }}

        @media (max-width: 1024px) {{
            .x-right-sidebar {{
                display: none !important;
            }}
            .layout-x-wrapper {{
                justify-content: center;
            }}
            .layout-x-container {{
                width: 100%;
                max-width: 600px;
                border-left: none;
                border-right: none;
            }}
        }}

        /* X Top Feed Header */
        .x-feed-header {{
            position: sticky;
            top: 48px;
            z-index: 100;
            background: rgba(0, 0, 0, 0.75);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border-bottom: 1px solid var(--border);
            padding: 12px 16px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}

        html[data-theme="light"] .x-feed-header {{
            background: rgba(255, 255, 255, 0.85);
        }}

        .x-header-title {{
            font-size: 18px;
            font-weight: 800;
            color: var(--text);
            line-height: 1.2;
        }}

        .x-header-meta {{
            font-size: 12px;
            color: var(--text-muted);
        }}

        .x-header-logo svg {{
            width: 22px;
            height: 22px;
            color: var(--text);
        }}

        /* X Tweet Item */
        .x-tweet {{
            display: flex;
            padding: 14px 16px 8px 16px;
            border-bottom: 1px solid var(--border);
            position: relative;
            transition: background-color 0.15s ease;
        }}

        .x-tweet:hover {{
            background-color: var(--surface-hover);
        }}

        .x-tweet-left {{
            display: flex;
            flex-direction: column;
            align-items: center;
            margin-right: 12px;
            flex-shrink: 0;
            width: 40px;
        }}

        .x-avatar {{
            width: 40px;
            height: 40px;
            border-radius: 9999px;
            background: linear-gradient(135deg, var(--accent), #7928ca);
            color: #ffffff;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 16px;
            user-select: none;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            flex-shrink: 0;
        }}

        /* The authentic connecting vertical line */
        .thread-connector {{
            width: 2px;
            background-color: var(--border);
            flex-grow: 1;
            margin-top: 6px;
            border-radius: 1px;
        }}

        .thread-connector.is-last {{
            display: none;
        }}

        .x-tweet-right {{
            flex-grow: 1;
            min-width: 0;
        }}

        .x-tweet-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 4px;
        }}

        .x-user-info {{
            display: flex;
            align-items: center;
            gap: 4px;
            flex-wrap: wrap;
            font-size: 15px;
        }}

        .x-display-name {{
            font-weight: 700;
            color: var(--text);
        }}

        .verified-badge {{
            width: 17px;
            height: 17px;
            color: var(--verified-color);
            flex-shrink: 0;
        }}

        .x-handle, .x-dot, .x-time {{
            color: var(--text-muted);
            font-size: 14px;
        }}

        .x-order-pill {{
            font-size: 11px;
            font-weight: 700;
            background: var(--surface);
            color: var(--accent);
            border: 1px solid var(--border);
            padding: 2px 7px;
            border-radius: 9999px;
        }}

        .x-tweet-body {{
            font-size: 15px;
            line-height: 1.45;
            word-break: break-word;
            margin-bottom: 10px;
            color: var(--text);
        }}

        .x-tweet-body p {{
            margin-bottom: 8px;
        }}

        .x-tweet-body p:last-child {{
            margin-bottom: 0;
        }}

        /* Quoted Tweet */
        .x-quote-card {{
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 12px;
            margin: 10px 0;
            background: rgba(255, 255, 255, 0.02);
            transition: background 0.15s ease;
        }}

        .x-quote-card:hover {{
            background: rgba(255, 255, 255, 0.04);
        }}

        .x-quote-header {{
            display: flex;
            gap: 6px;
            font-size: 13px;
            margin-bottom: 6px;
        }}

        .x-quote-name {{
            font-weight: 700;
            color: var(--text);
        }}

        .x-quote-handle {{
            color: var(--text-muted);
        }}

        .x-quote-text {{
            font-size: 14px;
            line-height: 1.4;
            color: var(--text);
        }}

        /* Media Attachments */
        .x-media-grid {{
            margin: 12px 0 6px 0;
            border-radius: 16px;
            overflow: hidden;
            border: 1px solid var(--border);
        }}

        .x-media-wrapper {{
            width: 100%;
            background: #000;
            display: flex;
            justify-content: center;
        }}

        .x-media-img {{
            width: 100%;
            max-height: 540px;
            object-fit: cover;
            display: block;
            cursor: zoom-in;
            transition: opacity 0.15s ease;
        }}

        .x-media-img:hover {{
            opacity: 0.95;
        }}

        .x-media-video {{
            width: 100%;
            max-height: 520px;
            display: block;
            background: #000;
        }}

        /* X Action Bar */
        .x-tweet-actions {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            max-width: 440px;
            margin-top: 8px;
            color: var(--text-muted);
            font-size: 13px;
        }}

        .x-action {{
            display: flex;
            align-items: center;
            gap: 6px;
            cursor: pointer;
            transition: color 0.15s ease;
        }}

        .x-action svg {{
            width: 18px;
            height: 18px;
            transition: transform 0.15s ease;
        }}

        .x-action:hover svg {{
            transform: scale(1.1);
        }}

        .action-reply:hover {{ color: var(--accent); }}
        .action-retweet:hover {{ color: var(--rt-color); }}
        .action-like:hover {{ color: var(--like-color); }}
        .action-views:hover {{ color: var(--accent); }}
        .action-share:hover {{ color: var(--accent); }}

        /* ==========================================================================
           LAYOUT 2: STEAM CLASSIC (2004-2008 GREEN VGUI SKIN)
           ========================================================================== */
        .layout-steam-container {{
            display: none;
            max-width: 980px;
            margin: 20px auto 40px auto;
            background-color: var(--steam-bg);
            color: var(--steam-text);
            border: 2px solid;
            border-color: var(--steam-border-light) var(--steam-border-dark) var(--steam-border-dark) var(--steam-border-light);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6);
            font-family: Tahoma, "Segoe UI", Verdana, sans-serif;
            font-size: 11px;
        }}

        html[data-layout="steam-old"] .layout-steam-container {{
            display: block;
        }}

        /* Steam Window Header */
        .steam-titlebar {{
            background: var(--steam-header);
            padding: 4px 8px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-bottom: 1px solid var(--steam-border-dark);
            user-select: none;
        }}

        .steam-titlebar-left {{
            display: flex;
            align-items: center;
            gap: 6px;
            font-weight: bold;
            font-size: 11px;
            color: var(--steam-text);
            letter-spacing: 0.5px;
        }}

        .steam-logo-svg {{
            width: 14px;
            height: 14px;
            color: var(--steam-text);
        }}

        .steam-window-controls {{
            display: flex;
            gap: 3px;
        }}

        .steam-win-btn {{
            width: 16px;
            height: 14px;
            background: var(--steam-bg);
            border: 1px solid;
            border-color: var(--steam-border-light) var(--steam-border-dark) var(--steam-border-dark) var(--steam-border-light);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 9px;
            font-weight: bold;
            color: var(--steam-text);
            cursor: pointer;
        }}

        .steam-win-btn:active {{
            border-color: var(--steam-border-dark) var(--steam-border-light) var(--steam-border-light) var(--steam-border-dark);
        }}

        /* Steam Menu Bar */
        .steam-menubar {{
            background: var(--steam-bg);
            padding: 3px 8px;
            display: flex;
            gap: 12px;
            font-size: 11px;
            border-bottom: 1px solid var(--steam-border-dark);
        }}

        .steam-menu-item {{
            color: var(--steam-text);
            cursor: pointer;
        }}

        .steam-menu-item:hover {{
            color: var(--steam-yellow-bright);
        }}

        /* Steam Navigation & Tabs */
        .steam-nav-tabs {{
            padding: 6px 8px 0 8px;
            display: flex;
            align-items: flex-end;
            gap: 4px;
            background: var(--steam-bg);
        }}

        .steam-history-arrows {{
            display: flex;
            gap: 2px;
            margin-right: 8px;
            margin-bottom: 4px;
        }}

        .steam-arrow-btn {{
            width: 18px;
            height: 18px;
            background: var(--steam-header);
            border: 1px solid;
            border-color: var(--steam-border-light) var(--steam-border-dark) var(--steam-border-dark) var(--steam-border-light);
            color: var(--steam-text-muted);
            font-size: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
        }}

        .steam-tab {{
            background: var(--steam-header);
            border: 1px solid;
            border-color: var(--steam-border-light) var(--steam-border-dark) var(--steam-bg) var(--steam-border-light);
            padding: 5px 12px;
            font-size: 11px;
            font-weight: bold;
            color: var(--steam-text-muted);
            cursor: pointer;
            border-top-left-radius: 3px;
            border-top-right-radius: 3px;
        }}

        .steam-tab.active {{
            background: var(--steam-bg);
            border-bottom-color: var(--steam-bg);
            color: var(--steam-yellow);
            border-top: 2px solid var(--steam-yellow);
        }}

        /* Steam Games Table (The classic library list!) */
        .steam-library-container {{
            margin: 6px 8px;
            background: var(--steam-inset);
            border: 2px solid;
            border-color: var(--steam-border-dark) var(--steam-border-light) var(--steam-border-light) var(--steam-border-dark);
            max-height: 220px;
            overflow-y: auto;
        }}

        .steam-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 11px;
        }}

        .steam-table th {{
            background: var(--steam-header);
            padding: 4px 8px;
            text-align: left;
            font-weight: bold;
            color: var(--steam-text);
            border-bottom: 1px solid var(--steam-border-dark);
            border-right: 1px solid var(--steam-border-dark);
            cursor: pointer;
            user-select: none;
        }}

        .steam-category-header {{
            background: rgba(0, 0, 0, 0.2);
            color: var(--steam-yellow);
            font-weight: bold;
            padding: 4px 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border-bottom: 1px solid var(--steam-border-dark);
        }}

        .steam-row {{
            cursor: pointer;
            transition: background 0.1s ease;
        }}

        .steam-row:hover {{
            background: var(--steam-highlight);
            color: #ffffff;
        }}

        .steam-row td {{
            padding: 3px 8px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.04);
            white-space: nowrap;
        }}

        .col-game {{
            display: flex;
            align-items: center;
            gap: 6px;
        }}

        .steam-lambda-icon {{
            color: var(--steam-yellow-bright);
            font-weight: bold;
            font-size: 12px;
        }}

        .steam-game-title {{
            font-weight: bold;
        }}

        .steam-star {{
            color: var(--steam-yellow);
        }}

        .steam-score-badge {{
            color: var(--steam-blue);
            text-decoration: underline;
            font-weight: bold;
        }}

        /* Steam Detailed Reading Pane */
        .steam-reading-pane {{
            margin: 8px;
            background: var(--steam-inset);
            border: 2px solid;
            border-color: var(--steam-border-dark) var(--steam-border-light) var(--steam-border-light) var(--steam-border-dark);
            padding: 16px;
            max-height: 600px;
            overflow-y: auto;
        }}

        .steam-post-card {{
            background: var(--steam-card-bg);
            border: 1px solid;
            border-color: var(--steam-border-light) var(--steam-border-dark) var(--steam-border-dark) var(--steam-border-light);
            padding: 14px;
            margin-bottom: 16px;
            box-shadow: inset 1px 1px 0 rgba(255,255,255,0.05);
        }}

        .steam-post-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--steam-border-dark);
            padding-bottom: 6px;
            margin-bottom: 10px;
        }}

        .steam-badge {{
            background: var(--steam-yellow);
            color: #000;
            padding: 1px 6px;
            font-size: 10px;
            font-weight: bold;
            border-radius: 2px;
            margin-right: 6px;
        }}

        .steam-post-title strong {{
            color: var(--steam-yellow-bright);
            font-size: 12px;
        }}

        .steam-muted {{
            color: var(--steam-text-muted);
        }}

        .steam-post-time {{
            color: var(--steam-text-muted);
            font-size: 10px;
        }}

        .steam-post-body {{
            font-size: 12px;
            line-height: 1.5;
            color: var(--steam-text);
            margin-bottom: 12px;
        }}

        .steam-post-body p {{
            margin-bottom: 8px;
        }}

        .steam-post-footer {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-top: 1px solid var(--steam-border-dark);
            padding-top: 8px;
            font-size: 10px;
        }}

        .steam-stats {{
            display: flex;
            gap: 12px;
            color: var(--steam-text-muted);
        }}

        .steam-stats strong {{
            color: var(--steam-text);
        }}

        /* Steam VGUI Classic Beveled Buttons */
        .steam-action-buttons {{
            padding: 6px 8px 12px 8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .steam-btn-group {{
            display: flex;
            gap: 6px;
        }}

        .steam-vgui-btn {{
            background: var(--steam-bg);
            border: 2px solid;
            border-color: var(--steam-border-light) var(--steam-border-dark) var(--steam-border-dark) var(--steam-border-light);
            color: var(--steam-text);
            padding: 4px 14px;
            font-family: inherit;
            font-size: 11px;
            font-weight: bold;
            cursor: pointer;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }}

        .steam-vgui-btn:hover {{
            color: var(--steam-yellow-bright);
            text-decoration: none;
        }}

        .steam-vgui-btn:active {{
            border-color: var(--steam-border-dark) var(--steam-border-light) var(--steam-border-light) var(--steam-border-dark);
        }}

        .steam-vgui-btn.primary {{
            color: var(--steam-yellow);
        }}

        .steam-vgui-btn.small {{
            padding: 2px 8px;
            font-size: 10px;
        }}

        /* Steam Bottom Client Status Bar */
        .steam-client-footer {{
            background: var(--steam-chrome);
            border-top: 1px solid var(--steam-border-dark);
            padding: 10px 16px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 36px;
            font-size: 10px;
            color: var(--steam-text-muted);
            user-select: none;
        }}

        .steam-footer-icon-item {{
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 4px;
            cursor: pointer;
        }}

        .steam-footer-icon-item:hover {{
            color: var(--steam-yellow-bright);
        }}

        .steam-footer-symbol {{
            font-size: 16px;
        }}

        /* ==========================================================================
           PRINT STYLES
           ========================================================================== */
        @media print {{
            .top-toolbar, .steam-titlebar, .steam-menubar, .steam-nav-tabs, .steam-library-container, .steam-action-buttons, .steam-client-footer {{
                display: none !important;
            }}
            body {{
                background: #ffffff !important;
                color: #000000 !important;
            }}
            .layout-x-container {{
                display: block !important;
                border: none !important;
                max-width: 100% !important;
            }}
            .layout-steam-container {{
                display: none !important;
            }}
            .x-tweet {{
                border-bottom: 1px solid #ddd !important;
                page-break-inside: avoid;
            }}
        }}

        /* ==========================================================================
           RESPONSIVE
           ========================================================================== */
        @media (max-width: 700px) {{
            .top-toolbar {{
                flex-wrap: wrap;
                gap: 8px;
            }}
            .layout-x-container {{
                border-left: none;
                border-right: none;
            }}
            .layout-steam-container {{
                margin: 0;
                border: none;
            }}
            .steam-client-footer {{
                gap: 16px;
            }}
        }}
    </style>
</head>
<body>

    <!-- TOP CONTROL TOOLBAR -->
    <header class="top-toolbar">
        <div class="toolbar-group">
            <span class="toolbar-label">Layout:</span>
            <button class="nav-btn active" id="btn-layout-x" onclick="setLayout('x-original')">
                {SVG_X_LOGO} 𝕏 Original
            </button>
            <button class="nav-btn" id="btn-layout-steam" onclick="setLayout('steam-old')">
                {SVG_STEAM_LOGO} Steam Old (2004)
            </button>
        </div>

        <div class="toolbar-group">
            <span class="toolbar-label">Tema:</span>
            <select class="theme-select" id="theme-selector" onchange="setTheme(this.value)">
                <option value="default">🎨 Padrão (Sem tema)</option>
                <option value="tokyo-night">🌃 Tokyo Night</option>
                <option value="dracula">🧛 Dracula</option>
                <option value="catppuccin">☕ Catppuccin Mocha</option>
                <option value="light">☀️ Claro (Daylight)</option>
            </select>
            <button class="nav-btn" onclick="window.print()" title="Salvar em PDF ou Imprimir">
                🖨️ PDF
            </button>
            <a href="../index.html" class="nav-btn" title="Ver todas as threads salvas">
                📚 Biblioteca
            </a>
            <a href="{thread.original_url}" target="_blank" rel="noopener" class="nav-btn" title="Abrir no X original">
                ↗ X.com
            </a>
        </div>
    </header>

    <!-- ==========================================================================
         LAYOUT 1: X (TWITTER) ORIGINAL TIMELINE & RIGHT SIDEBAR
         ========================================================================== -->
    <div class="layout-x-wrapper">
        <main class="layout-x-container">
            <!-- Feed Top Bar -->
            <div class="x-feed-header">
                <div>
                    <h1 class="x-header-title">{thread.author_name}</h1>
                    <div class="x-header-meta">{thread.total_tweets} posts • {thread.created_at.strftime('%d de %b')} • ❤️ {thread.total_likes:,}</div>
                </div>
                <div class="x-header-logo">
                    {SVG_X_LOGO}
                </div>
            </div>

            <!-- Tweets List -->
            <section class="x-timeline-feed">
                {"".join(x_tweets_html)}
            </section>
        </main>

        <!-- RIGHT SIDEBAR (O QUE ESTÁ ACONTECENDO / THREADS SALVAS) -->
        <aside class="x-right-sidebar">
            <div class="x-sidebar-search">
                <svg viewBox="0 0 24 24" class="search-icon" fill="currentColor">
                    <path d="M10.25 3.75c-3.59 0-6.5 2.91-6.5 6.5s2.91 6.5 6.5 6.5c1.79 0 3.42-.73 4.6-1.9l4.47 4.47 1.41-1.41-4.47-4.47c1.17-1.18 1.9-2.81 1.9-4.6 0-3.59-2.91-6.5-6.5-6.5zm-4.5 6.5c0-2.48 2.02-4.5 4.5-4.5s4.5 2.02 4.5 4.5-2.02 4.5-4.5 4.5-4.5-2.02-4.5-4.5z"/>
                </svg>
                <input type="text" id="sidebarSearch" placeholder="Buscar nas threads..." oninput="filterSidebarThreads(this.value)" />
            </div>

            <!-- Pessoas relevantes / Autor -->
            <div class="x-sidebar-card author-card">
                <h3 class="x-card-heading">Pessoas relevantes</h3>
                <div class="author-row">
                    <div class="x-avatar small">
                        <span>{avatar_initial}</span>
                    </div>
                    <div class="author-info">
                        <div class="author-name-row">
                            <strong class="x-name">{thread.author_name}</strong>
                            {SVG_VERIFIED}
                        </div>
                        <span class="x-handle">@{thread.author_username}</span>
                    </div>
                    <a href="{thread.original_url}" target="_blank" rel="noopener" class="x-follow-btn">
                        Ver no X ↗
                    </a>
                </div>
            </div>

            <!-- O que você salvou / Threads Widget -->
            <div class="x-sidebar-card trends-card">
                <h3 class="x-card-heading">O que você salvou</h3>
                <div class="x-trends-list" id="sidebarThreadsList">
                    {"".join(sidebar_threads_html)}
                </div>
                <a href="../index.html" class="x-show-more">
                    Mostrar mais (Ver todas na Biblioteca) ➔
                </a>
            </div>

            <footer class="x-sidebar-footer">
                <a href="../index.html">Biblioteca Central</a>
                <span>·</span>
                <a href="{thread.original_url}" target="_blank">Post Original</a>
                <span>·</span>
                <span>xthread</span>
            </footer>
        </aside>
    </div>

    <!-- ==========================================================================
         LAYOUT 2: STEAM CLASSIC (2004-2008 GREEN VGUI SKIN)
         ========================================================================== -->
    <div class="layout-steam-container">
        <!-- Window Title Bar -->
        <div class="steam-titlebar">
            <div class="steam-titlebar-left">
                {SVG_STEAM_LOGO}
                <span>STEAM - XTHREAD // @{thread.author_username} - {thread.title[:40]}</span>
            </div>
            <div class="steam-window-controls">
                <div class="steam-win-btn" title="Minimize">_</div>
                <div class="steam-win-btn" title="Maximize">□</div>
                <div class="steam-win-btn" title="Close">✕</div>
            </div>
        </div>

        <!-- Menu Bar -->
        <div class="steam-menubar">
            <span class="steam-menu-item">File</span>
            <span class="steam-menu-item">View</span>
            <span class="steam-menu-item">Thread</span>
            <span class="steam-menu-item">Tools</span>
            <span class="steam-menu-item">Help</span>
        </div>

        <!-- Navigation Tabs -->
        <div class="steam-nav-tabs">
            <div class="steam-history-arrows">
                <div class="steam-arrow-btn">◀</div>
                <div class="steam-arrow-btn">▶</div>
            </div>
            <a href="../index.html" class="steam-tab" style="text-decoration:none;" title="Voltar para a Biblioteca">◀ Library Hub</a>
            <div class="steam-tab">Community</div>
            <div class="steam-tab active">My thread ({thread.total_tweets})</div>
            <div class="steam-tab">My media ({sum(len(t.media) for t in thread.tweets)})</div>
            <div class="steam-tab">Tools</div>
        </div>

        <!-- VGUI Classic Game Table -->
        <div class="steam-library-container">
            <table class="steam-table">
                <thead>
                    <tr>
                        <th style="width: 50%;">Games / Threads</th>
                        <th style="width: 20%;">Status ▲</th>
                        <th style="width: 15%;">Metrics</th>
                        <th style="width: 5%;">Score</th>
                        <th style="width: 10%;">Developer</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td colspan="5" class="steam-category-header">▼ MY THREAD ({thread.total_tweets} POSTS)</td>
                    </tr>
                    {"".join(steam_list_rows)}
                </tbody>
            </table>
        </div>

        <!-- Detailed Reading Area -->
        <div class="steam-reading-pane" id="steam-reading-pane">
            {"".join(steam_detail_cards)}
        </div>

        <!-- Bottom Action Buttons -->
        <div class="steam-action-buttons">
            <div class="steam-btn-group">
                <button class="steam-vgui-btn" onclick="copyThreadUrl()">Add non-Steam game...</button>
                <button class="steam-vgui-btn" onclick="window.print()">Activate a product on Steam...</button>
            </div>
            <div class="steam-btn-group">
                <button class="steam-vgui-btn" onclick="alert('Thread ID: {thread.root_id}\\nAutor: {thread.author_name} (@{thread.author_username})\\nTotal de posts: {thread.total_tweets}\\nLikes: {thread.total_likes}')">Properties</button>
                <a href="{thread.original_url}" target="_blank" rel="noopener" class="steam-vgui-btn primary">Launch in X ↗</a>
            </div>
        </div>

        <!-- Bottom Client Status Bar -->
        <div class="steam-client-footer">
            <div class="steam-footer-icon-item" onclick="alert('Você está lendo a thread de @{thread.author_username}')">
                <span class="steam-footer-symbol">📄</span>
                <span>News</span>
            </div>
            <div class="steam-footer-icon-item" onclick="alert('Conectado como {thread.author_username}')">
                <span class="steam-footer-symbol">👥</span>
                <span>Friends (1 Online)</span>
            </div>
            <div class="steam-footer-icon-item">
                <span class="steam-footer-symbol">🌐</span>
                <span>Servers</span>
            </div>
            <div class="steam-footer-icon-item" onclick="document.getElementById('theme-selector').focus()">
                <span class="steam-footer-symbol">☑️</span>
                <span>Settings</span>
            </div>
            <div class="steam-footer-icon-item" onclick="alert('xthread v0.1.0 - Downloader de Threads do X')">
                <span class="steam-footer-symbol">❓</span>
                <span>Support</span>
            </div>
        </div>
    </div>

    <!-- JAVASCRIPT: THEME & LAYOUT ENGINE -->
    <script>
        function setLayout(layoutName) {{
            document.documentElement.setAttribute('data-layout', layoutName);
            document.getElementById('btn-layout-x').classList.toggle('active', layoutName === 'x-original');
            document.getElementById('btn-layout-steam').classList.toggle('active', layoutName === 'steam-old');
            try {{
                localStorage.setItem('xthread_layout', layoutName);
            }} catch(e) {{}}
        }}

        function setTheme(themeName) {{
            document.documentElement.setAttribute('data-theme', themeName);
            const selector = document.getElementById('theme-selector');
            if (selector) selector.value = themeName;
            try {{
                localStorage.setItem('xthread_theme', themeName);
            }} catch(e) {{}}
        }}

        function scrollToTweet(order) {{
            const currentLayout = document.documentElement.getAttribute('data-layout');
            if (currentLayout === 'steam-old') {{
                const target = document.getElementById('steam-tweet-' + order);
                const pane = document.getElementById('steam-reading-pane');
                if (target && pane) {{
                    target.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
                }}
            }} else {{
                const target = document.getElementById('tweet-' + order);
                if (target) {{
                    target.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                }}
            }}
        }}

        function copyThreadUrl() {{
            navigator.clipboard.writeText(window.location.href).then(() => {{
                alert('Link copiado para a área de transferência!');
            }}).catch(() => {{
                alert('URL: ' + window.location.href);
            }});
        }}

        function filterSidebarThreads(query) {{
            const q = query.toLowerCase();
            const items = document.querySelectorAll('.x-trend-item');
            items.forEach(item => {{
                const text = item.textContent.toLowerCase();
                item.style.display = text.includes(q) ? 'block' : 'none';
            }});
        }}

        // Initialize saved preferences
        (function() {{
            try {{
                const savedLayout = localStorage.getItem('xthread_layout');
                if (savedLayout) setLayout(savedLayout);

                const savedTheme = localStorage.getItem('xthread_theme');
                if (savedTheme) setTheme(savedTheme);
            }} catch(e) {{}}
        }})();
    </script>
</body>
</html>
"""

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)
