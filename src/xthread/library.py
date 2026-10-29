"""Library manager and HTML hub generator for saved threads."""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from xthread.config import load_config, get_threads_dir


def scan_saved_threads(base_dir: Path | None = None) -> list[dict[str, Any]]:
    """Scan the threads directory for all saved threads and parse their metadata."""
    if base_dir is None:
        base_dir = get_threads_dir()

    if not base_dir.exists():
        return []

    threads: list[dict[str, Any]] = []

    for entry in base_dir.iterdir():
        if not entry.is_dir() or entry.name == "media":
            continue

        meta: dict[str, Any] = {
            "dir_name": entry.name,
            "dir_path": str(entry),
            "html_path": f"{entry.name}/index.html",
            "has_html": (entry / "index.html").exists(),
            "has_md": (entry / "thread.md").exists(),
            "media_count": 0,
            "thumbnail_url": None,
            "total_tweets": 1,
            "total_likes": 0,
            "total_retweets": 0,
            "total_views": 0,
            "title": entry.name,
            "author_name": "Autor Desconhecido",
            "author_username": "desconhecido",
            "created_at_str": "",
            "created_at_dt": datetime.min,
            "original_url": "",
        }

        # 1. Try reading thread.json first
        json_file = entry / "thread.json"
        if json_file.exists():
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    meta["title"] = data.get("title", meta["title"])
                    meta["author_name"] = data.get("author_name", meta["author_name"])
                    meta["author_username"] = data.get("author_username", meta["author_username"])
                    meta["total_tweets"] = data.get("total_tweets", 1)
                    meta["total_likes"] = data.get("total_likes", 0)
                    meta["total_retweets"] = data.get("total_retweets", 0)
                    meta["total_views"] = data.get("total_views", 0)
                    meta["original_url"] = data.get("original_url", "")
                    if "created_at" in data:
                        meta["created_at_str"] = data["created_at"]
                        try:
                            meta["created_at_dt"] = datetime.fromisoformat(data["created_at"].replace("Z", "+00:00"))
                        except Exception:
                            pass
            except Exception:
                pass

        # 2. If no thread.json, fallback to parsing thread.md frontmatter
        md_file = entry / "thread.md"
        if md_file.exists() and meta["author_name"] == "Autor Desconhecido":
            try:
                content = md_file.read_text(encoding="utf-8")
                match = re.search(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
                if match:
                    for line in match.group(1).splitlines():
                        if ":" in line:
                            k, v = line.split(":", 1)
                            key = k.strip()
                            val = v.strip().strip('"').strip("'")
                            if key == "title":
                                meta["title"] = val
                            elif key == "author":
                                meta["author_name"] = val
                            elif key == "author_handle":
                                meta["author_username"] = val.lstrip("@")
                            elif key == "total_tweets":
                                try:
                                    meta["total_tweets"] = int(val)
                                except ValueError:
                                    pass
                            elif key == "likes":
                                try:
                                    meta["total_likes"] = int(val)
                                except ValueError:
                                    pass
                            elif key == "retweets":
                                try:
                                    meta["total_retweets"] = int(val)
                                except ValueError:
                                    pass
                            elif key == "views":
                                try:
                                    meta["total_views"] = int(val)
                                except ValueError:
                                    pass
                            elif key == "url":
                                meta["original_url"] = val
                            elif key == "date":
                                meta["created_at_str"] = val
                                try:
                                    meta["created_at_dt"] = datetime.fromisoformat(val.replace("Z", "+00:00"))
                                except Exception:
                                    pass
            except Exception:
                pass

        # 3. Check media files & select first photo as thumbnail
        media_dir = entry / "media"
        if media_dir.exists():
            media_files = sorted(list(media_dir.glob("*")))
            meta["media_count"] = len(media_files)
            for mf in media_files:
                if mf.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp"):
                    meta["thumbnail_url"] = f"{entry.name}/media/{mf.name}"
                    break

        threads.append(meta)

    # Sort threads by date descending
    threads.sort(key=lambda x: x["created_at_dt"], reverse=True)
    return threads


def generate_library_hub_html(threads: list[dict[str, Any]], output_file: Path) -> None:
    """Generate the central Library Hub index.html with X and Steam Classic dual-views."""
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Calculate statistics
    total_threads = len(threads)
    total_posts = sum(t["total_tweets"] for t in threads)
    total_medias = sum(t["media_count"] for t in threads)
    total_likes = sum(t["total_likes"] for t in threads)

    # 1. Generate X Cards HTML
    x_cards_html: list[str] = []
    steam_list_rows: list[str] = []
    steam_detail_cards_js: list[dict[str, Any]] = []

    for idx, t in enumerate(threads):
        initial = (t["author_name"] or "X")[0].upper()
        date_display = t["created_at_dt"].strftime("%d/%m/%Y") if t["created_at_dt"] != datetime.min else "Recente"

        # Media thumbnail HTML
        thumb_html = ""
        if t["thumbnail_url"]:
            thumb_html = f"""
            <div class="x-card-thumb">
                <img src="{t['thumbnail_url']}" loading="lazy" alt="Preview da thread" />
            </div>
            """

        x_cards_html.append(f"""
        <article class="x-library-card" data-title="{t['title'].lower()}" data-author="{t['author_name'].lower()} @{t['author_username'].lower()}">
            <div class="x-card-left">
                <div class="x-avatar">
                    <span>{initial}</span>
                </div>
            </div>
            <div class="x-card-body">
                <div class="x-card-top">
                    <div class="x-user-meta">
                        <strong class="x-name">{t['author_name']}</strong>
                        <span class="x-handle">@{t['author_username']}</span>
                        <span class="x-dot">·</span>
                        <time class="x-date">{date_display}</time>
                    </div>
                    <span class="x-badge">{t['total_tweets']} tweets</span>
                </div>

                <h3 class="x-card-title">{t['title']}</h3>

                {thumb_html}

                <div class="x-card-metrics">
                    <span>❤️ {t['total_likes']:,}</span>
                    <span>🔁 {t['total_retweets']:,}</span>
                    <span>👁️ {t['total_views']:,}</span>
                    <span>🎬 {t['media_count']} mídias</span>
                </div>

                <div class="x-card-actions">
                    <a href="{t['html_path']}" class="x-open-btn">
                        <span>Ler Thread Completa</span> ➔
                    </a>
                    {f'<a href="{t["original_url"]}" target="_blank" rel="noopener" class="x-link-btn">Ver no X ↗</a>' if t['original_url'] else ''}
                </div>
            </div>
        </article>
        """)

        # Steam Library Row & Card
        steam_list_rows.append(f"""
        <tr class="steam-row" id="steam-row-{idx}" onclick="selectSteamGame({idx})">
            <td class="col-game">
                <span class="steam-lambda-icon">λ</span>
                <span class="steam-game-title">{t['title'][:50]}</span>
            </td>
            <td class="col-status"><span class="steam-star">★</span> 100% - Ready</td>
            <td class="col-posts">{t['total_tweets']} Posts</td>
            <td class="col-author">@{t['author_username']}</td>
        </tr>
        """)

        steam_detail_cards_js.append({
            "index": idx,
            "title": t["title"],
            "author_name": t["author_name"],
            "author_username": t["author_username"],
            "total_tweets": t["total_tweets"],
            "total_likes": t["total_likes"],
            "total_retweets": t["total_retweets"],
            "total_views": t["total_views"],
            "media_count": t["media_count"],
            "date": date_display,
            "html_path": t["html_path"],
            "original_url": t["original_url"],
            "thumbnail_url": t["thumbnail_url"],
            "dir_name": t["dir_name"],
        })

    json_threads_data = json.dumps(steam_detail_cards_js, ensure_ascii=False)

    html_content = f"""<!DOCTYPE html>
<html lang="pt-BR" data-theme="default" data-layout="x-original">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Biblioteca de Threads — xthread</title>
    <style>
        /* ==========================================================================
           COLOR PALETTES & THEMES
           ========================================================================== */
        :root {{
            --bg: #000000;
            --surface: #16181c;
            --surface-hover: #1d1f23;
            --border: #2f3336;
            --border-light: #202327;
            --text: #e7e9ea;
            --text-secondary: #71767b;
            --text-muted: #536471;
            --accent: #1d9bf0;
            --accent-hover: #1a8cd8;
            --font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            
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
            --steam-highlight: #58694f;
        }}

        html[data-theme="tokyo-night"] {{
            --bg: #1a1b26;
            --surface: #24283b;
            --surface-hover: #2f3549;
            --border: #292e42;
            --text: #c0caf5;
            --text-secondary: #7aa2f7;
            --text-muted: #565f89;
            --accent: #7aa2f7;
            --steam-bg: #1f2335;
            --steam-header: #1a1b26;
            --steam-chrome: #16161e;
            --steam-inset: #13141c;
            --steam-card-bg: #24283b;
            --steam-border-light: #3b4261;
            --steam-border-dark: #101014;
            --steam-text: #c0caf5;
            --steam-yellow: #e0af68;
            --steam-yellow-bright: #ff9e64;
        }}

        html[data-theme="dracula"] {{
            --bg: #282a36;
            --surface: #343746;
            --surface-hover: #44475a;
            --border: #44475a;
            --text: #f8f8f2;
            --text-secondary: #bd93f9;
            --text-muted: #6272a4;
            --accent: #bd93f9;
            --steam-bg: #282a36;
            --steam-header: #21222c;
            --steam-chrome: #191a21;
            --steam-inset: #191a21;
            --steam-card-bg: #343746;
            --steam-border-light: #6272a4;
            --steam-border-dark: #15161e;
            --steam-text: #f8f8f2;
            --steam-yellow: #f1fa8c;
            --steam-yellow-bright: #ffb86c;
        }}

        html[data-theme="catppuccin"] {{
            --bg: #1e1e2e;
            --surface: #252538;
            --surface-hover: #313244;
            --border: #313244;
            --text: #cdd6f4;
            --text-secondary: #bac2de;
            --text-muted: #a6adc8;
            --accent: #89b4fa;
            --steam-bg: #252538;
            --steam-header: #1e1e2e;
            --steam-chrome: #181825;
            --steam-inset: #11111b;
            --steam-card-bg: #313244;
            --steam-border-light: #45475a;
            --steam-border-dark: #11111b;
            --steam-text: #cdd6f4;
            --steam-yellow: #f9e2af;
            --steam-yellow-bright: #fab387;
        }}

        html[data-theme="light"] {{
            --bg: #ffffff;
            --surface: #f7f9f9;
            --surface-hover: #eff3f4;
            --border: #eff3f4;
            --text: #0f1419;
            --text-secondary: #536471;
            --text-muted: #8b98a5;
            --accent: #1d9bf0;
            --steam-bg: #c0c0c0;
            --steam-header: #a0a0a0;
            --steam-chrome: #808080;
            --steam-inset: #ffffff;
            --steam-card-bg: #eaeaea;
            --steam-border-light: #ffffff;
            --steam-border-dark: #404040;
            --steam-text: #000000;
            --steam-yellow: #806000;
            --steam-yellow-bright: #000080;
        }}

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
        }}

        a {{
            color: var(--accent);
            text-decoration: none;
        }}

        /* ==========================================================================
           TOP CONTROL TOOLBAR
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

        /* ==========================================================================
           LAYOUT 1: X (TWITTER) BOOKMARKS & LIBRARY
           ========================================================================== */
        .layout-x-container {{
            display: none;
            max-width: 680px;
            margin: 0 auto;
            border-left: 1px solid var(--border);
            border-right: 1px solid var(--border);
            min-height: 100vh;
        }}

        html[data-layout="x-original"] .layout-x-container {{
            display: block;
        }}

        .x-hub-header {{
            padding: 20px 16px 12px 16px;
            border-bottom: 1px solid var(--border);
        }}

        .x-hub-title {{
            font-size: 22px;
            font-weight: 800;
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 6px;
        }}

        .x-hub-subtitle {{
            font-size: 13px;
            color: var(--text-muted);
            margin-bottom: 14px;
        }}

        .x-search-box {{
            width: 100%;
            background: var(--surface);
            border: 1px solid var(--border);
            color: var(--text);
            border-radius: 9999px;
            padding: 10px 18px;
            font-size: 14px;
            outline: none;
            transition: border-color 0.15s ease;
        }}

        .x-search-box:focus {{
            border-color: var(--accent);
        }}

        .x-library-card {{
            display: flex;
            padding: 16px;
            border-bottom: 1px solid var(--border);
            transition: background-color 0.15s ease;
            gap: 12px;
        }}

        .x-library-card:hover {{
            background-color: var(--surface-hover);
        }}

        .x-card-left {{
            flex-shrink: 0;
        }}

        .x-avatar {{
            width: 44px;
            height: 44px;
            border-radius: 9999px;
            background: linear-gradient(135deg, var(--accent), #7928ca);
            color: #ffffff;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 16px;
        }}

        .x-card-body {{
            flex-grow: 1;
            min-width: 0;
        }}

        .x-card-top {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 4px;
        }}

        .x-user-meta {{
            display: flex;
            align-items: center;
            gap: 4px;
            font-size: 14px;
        }}

        .x-name {{
            font-weight: 700;
            color: var(--text);
        }}

        .x-handle, .x-date, .x-dot {{
            color: var(--text-muted);
            font-size: 13px;
        }}

        .x-badge {{
            font-size: 11px;
            font-weight: 700;
            background: var(--surface);
            color: var(--accent);
            border: 1px solid var(--border);
            padding: 2px 8px;
            border-radius: 9999px;
        }}

        .x-card-title {{
            font-size: 15px;
            font-weight: 600;
            color: var(--text);
            margin: 6px 0 10px 0;
            line-height: 1.4;
        }}

        .x-card-thumb {{
            margin: 10px 0;
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid var(--border);
            max-height: 240px;
        }}

        .x-card-thumb img {{
            width: 100%;
            height: auto;
            max-height: 240px;
            object-fit: cover;
            display: block;
        }}

        .x-card-metrics {{
            display: flex;
            gap: 14px;
            font-size: 12px;
            color: var(--text-muted);
            margin-bottom: 12px;
        }}

        .x-card-actions {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .x-open-btn {{
            background: var(--accent);
            color: #ffffff !important;
            padding: 6px 14px;
            border-radius: 9999px;
            font-size: 13px;
            font-weight: 700;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            transition: opacity 0.15s ease;
        }}

        .x-open-btn:hover {{
            opacity: 0.9;
            text-decoration: none;
        }}

        .x-link-btn {{
            color: var(--text-muted);
            font-size: 12px;
        }}

        .x-link-btn:hover {{
            color: var(--accent);
        }}

        /* ==========================================================================
           LAYOUT 2: STEAM CLASSIC GAMES LIBRARY (2004-2008)
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

        .steam-titlebar {{
            background: var(--steam-header);
            padding: 4px 8px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-bottom: 1px solid var(--steam-border-dark);
            font-weight: bold;
        }}

        .steam-menubar {{
            background: var(--steam-bg);
            padding: 3px 8px;
            display: flex;
            gap: 12px;
            border-bottom: 1px solid var(--steam-border-dark);
        }}

        .steam-nav-tabs {{
            padding: 6px 8px 0 8px;
            display: flex;
            gap: 4px;
            background: var(--steam-bg);
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
        }}

        .steam-tab.active {{
            background: var(--steam-bg);
            color: var(--steam-yellow);
            border-top: 2px solid var(--steam-yellow);
        }}

        .steam-main-split {{
            display: grid;
            grid-template-columns: 55% 45%;
            margin: 6px 8px;
            gap: 6px;
        }}

        .steam-table-container {{
            background: var(--steam-inset);
            border: 2px solid;
            border-color: var(--steam-border-dark) var(--steam-border-light) var(--steam-border-light) var(--steam-border-dark);
            height: 380px;
            overflow-y: auto;
        }}

        .steam-table {{
            width: 100%;
            border-collapse: collapse;
        }}

        .steam-table th {{
            background: var(--steam-header);
            padding: 4px 6px;
            text-align: left;
            font-size: 10px;
            color: var(--steam-text);
            border-bottom: 1px solid var(--steam-border-dark);
        }}

        .steam-category-header {{
            background: rgba(0, 0, 0, 0.2);
            color: var(--steam-yellow);
            font-weight: bold;
            padding: 4px 6px;
        }}

        .steam-row {{
            cursor: pointer;
        }}

        .steam-row:hover, .steam-row.selected {{
            background: var(--steam-highlight);
            color: #ffffff;
        }}

        .steam-row td {{
            padding: 4px 6px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.04);
            white-space: nowrap;
        }}

        .col-game {{
            display: flex;
            align-items: center;
            gap: 4px;
        }}

        .steam-lambda-icon {{
            color: var(--steam-yellow-bright);
            font-weight: bold;
        }}

        .steam-detail-pane {{
            background: var(--steam-card-bg);
            border: 2px solid;
            border-color: var(--steam-border-light) var(--steam-border-dark) var(--steam-border-dark) var(--steam-border-light);
            padding: 14px;
            height: 380px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
        }}

        .steam-pane-thumb {{
            width: 100%;
            height: 120px;
            background: var(--steam-inset);
            border: 1px solid var(--steam-border-dark);
            margin-bottom: 12px;
            overflow: hidden;
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        .steam-pane-thumb img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}

        .steam-pane-title {{
            color: var(--steam-yellow-bright);
            font-size: 14px;
            font-weight: bold;
            margin-bottom: 6px;
            line-height: 1.3;
        }}

        .steam-pane-meta {{
            font-size: 11px;
            color: var(--steam-text-muted);
            margin-bottom: 14px;
        }}

        .steam-pane-stats {{
            background: var(--steam-inset);
            border: 1px solid var(--steam-border-dark);
            padding: 8px;
            font-size: 11px;
            margin-bottom: 16px;
            line-height: 1.6;
        }}

        .steam-pane-actions {{
            margin-top: auto;
            display: flex;
            gap: 8px;
        }}

        .steam-vgui-btn {{
            background: var(--steam-bg);
            border: 2px solid;
            border-color: var(--steam-border-light) var(--steam-border-dark) var(--steam-border-dark) var(--steam-border-light);
            color: var(--steam-text);
            padding: 6px 14px;
            font-size: 11px;
            font-weight: bold;
            cursor: pointer;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            justify-content: center;
        }}

        .steam-vgui-btn.primary {{
            color: var(--steam-yellow-bright);
            background: #55624d;
        }}

        .steam-vgui-btn:hover {{
            color: var(--steam-yellow-bright);
            text-decoration: none;
        }}

        .steam-client-footer {{
            background: var(--steam-chrome);
            border-top: 1px solid var(--steam-border-dark);
            padding: 8px 16px;
            display: flex;
            justify-content: center;
            gap: 32px;
            font-size: 10px;
            color: var(--steam-text-muted);
        }}

        @media (max-width: 768px) {{
            .steam-main-split {{
                grid-template-columns: 1fr;
            }}
            .steam-table-container, .steam-detail-pane {{
                height: 280px;
            }}
        }}
    </style>
</head>
<body>

    <!-- TOP TOOLBAR -->
    <header class="top-toolbar">
        <div class="toolbar-group">
            <span class="toolbar-label">Layout:</span>
            <button class="nav-btn active" id="btn-layout-x" onclick="setLayout('x-original')">
                𝕏 Original
            </button>
            <button class="nav-btn" id="btn-layout-steam" onclick="setLayout('steam-old')">
                🎮 Steam Old
            </button>
        </div>

        <div class="toolbar-group">
            <span class="toolbar-label">Tema:</span>
            <select class="theme-select" id="theme-selector" onchange="setTheme(this.value)">
                <option value="default">🎨 Padrão</option>
                <option value="tokyo-night">🌃 Tokyo Night</option>
                <option value="dracula">🧛 Dracula</option>
                <option value="catppuccin">☕ Catppuccin</option>
                <option value="light">☀️ Claro</option>
            </select>
        </div>
    </header>

    <!-- ==========================================================================
         LAYOUT 1: X (TWITTER) BOOKMARKS & LIBRARY
         ========================================================================== -->
    <main class="layout-x-container">
        <div class="x-hub-header">
            <h1 class="x-hub-title">
                📚 Threads Salvas
            </h1>
            <p class="x-hub-subtitle">
                {total_threads} threads arquivadas • {total_posts} tweets • {total_medias} mídias
            </p>
            <input type="text" id="xSearchInput" class="x-search-box" placeholder="Pesquisar por autor, título ou palavra-chave..." oninput="filterXCards(this.value)" />
        </div>

        <section id="x-cards-list">
            {"".join(x_cards_html) if x_cards_html else '<p style="padding: 30px; text-align: center; color: var(--text-muted);">Nenhuma thread salva ainda. Baixe com: xthread &lt;url&gt;</p>'}
        </section>
    </main>

    <!-- ==========================================================================
         LAYOUT 2: STEAM CLASSIC GAMES LIBRARY (2004-2008)
         ========================================================================== -->
    <div class="layout-steam-container">
        <div class="steam-titlebar">
            <span>STEAM - XTHREAD // GAMES & ARCHIVE LIBRARY</span>
            <span style="font-size: 10px;">_ □ ✕</span>
        </div>

        <div class="steam-menubar">
            <span>File</span>
            <span>View</span>
            <span>Games</span>
            <span>Tools</span>
            <span>Help</span>
        </div>

        <div class="steam-nav-tabs">
            <div class="steam-tab">Store</div>
            <div class="steam-tab">Community</div>
            <div class="steam-tab active">My games ({total_threads})</div>
            <div class="steam-tab">My media ({total_medias})</div>
            <div class="steam-tab">Tools</div>
        </div>

        <div class="steam-main-split">
            <!-- Left: Table of Threads -->
            <div class="steam-table-container">
                <table class="steam-table">
                    <thead>
                        <tr>
                            <th style="width: 50%;">Games / Threads</th>
                            <th style="width: 25%;">Status</th>
                            <th style="width: 10%;">Posts</th>
                            <th style="width: 15%;">Author</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td colspan="4" class="steam-category-header">▼ INSTALLED THREADS ({total_threads})</td>
                        </tr>
                        {"".join(steam_list_rows)}
                    </tbody>
                </table>
            </div>

            <!-- Right: Selected Thread Pane -->
            <div class="steam-detail-pane" id="steamDetailPane">
                <div class="steam-pane-thumb" id="paneThumb">
                    <span style="color: var(--steam-text-muted);">λ XTHREAD ENGINE</span>
                </div>
                <h2 class="steam-pane-title" id="paneTitle">Selecione uma thread</h2>
                <div class="steam-pane-meta" id="paneMeta">Autor: -</div>
                <div class="steam-pane-stats" id="paneStats">
                    Métricas indisponíveis.
                </div>
                <div class="steam-pane-actions">
                    <a href="#" id="paneLaunchBtn" class="steam-vgui-btn primary">▶ LAUNCH / LER THREAD</a>
                </div>
            </div>
        </div>

        <div class="steam-client-footer">
            <span>📄 News</span>
            <span>👥 Friends ({total_threads} Installed)</span>
            <span>🌐 Servers</span>
            <span>☑️ Settings</span>
            <span>❓ Support</span>
        </div>
    </div>

    <!-- JAVASCRIPT: LOGIC & FILTERING -->
    <script>
        const THREADS_DATA = {json_threads_data};

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

        function filterXCards(query) {{
            const q = query.toLowerCase();
            const cards = document.querySelectorAll('.x-library-card');
            cards.forEach(card => {{
                const title = card.getAttribute('data-title') || '';
                const author = card.getAttribute('data-author') || '';
                const match = title.includes(q) || author.includes(q);
                card.style.display = match ? 'flex' : 'none';
            }});
        }}

        function selectSteamGame(idx) {{
            const data = THREADS_DATA[idx];
            if (!data) return;

            document.querySelectorAll('.steam-row').forEach(r => r.classList.remove('selected'));
            const row = document.getElementById('steam-row-' + idx);
            if (row) row.classList.add('selected');

            document.getElementById('paneTitle').textContent = data.title;
            document.getElementById('paneMeta').textContent = 'Developer: ' + data.author_name + ' (@' + data.author_username + ') • ' + data.date;

            document.getElementById('paneStats').innerHTML = 
                'Total de Posts: <strong>' + data.total_tweets + '</strong><br>' +
                'Métricas: ❤️ ' + data.total_likes.toLocaleString() + '  |  🔁 ' + data.total_retweets.toLocaleString() + '  |  👁️ ' + data.total_views.toLocaleString() + '<br>' +
                'Mídias salvas: <strong>' + data.media_count + ' arquivos</strong><br>' +
                'Diretório: <span style="color: var(--steam-yellow);">' + data.dir_name + '</span>';

            const thumbDiv = document.getElementById('paneThumb');
            if (data.thumbnail_url) {{
                thumbDiv.innerHTML = '<img src="' + data.thumbnail_url + '" alt="Cover" />';
            }} else {{
                thumbDiv.innerHTML = '<span style="color: var(--steam-text-muted);">λ ' + data.author_username + '</span>';
            }}

            const launchBtn = document.getElementById('paneLaunchBtn');
            launchBtn.href = data.html_path;
        }}

        // Init
        (function() {{
            try {{
                const savedLayout = localStorage.getItem('xthread_layout');
                if (savedLayout) setLayout(savedLayout);

                const savedTheme = localStorage.getItem('xthread_theme');
                if (savedTheme) setTheme(savedTheme);
            }} catch(e) {{}}

            if (THREADS_DATA.length > 0) {{
                selectSteamGame(0);
            }}
        }})();
    </script>
</body>
</html>
"""

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)
