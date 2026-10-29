"""Configuration and paths management for xthread."""

import json
from pathlib import Path
from typing import Any

APP_NAME = "xthread"
APP_VERSION = "0.1.0"

# Directories
CONFIG_DIR = Path.home() / ".config" / APP_NAME
CONFIG_FILE = CONFIG_DIR / "config.json"
DB_FILE = CONFIG_DIR / "accounts.db"

DEFAULT_CONFIG: dict[str, Any] = {
    "default_output_dir": "./threads",
    "download_media": True,
    "default_formats": ["markdown", "html"],
    "concurrency": 6,
    "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
}


def ensure_config_dir() -> Path:
    """Ensure the configuration directory exists."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    return CONFIG_DIR


def get_db_path() -> Path:
    """Get the path to the accounts SQLite database."""
    ensure_config_dir()
    return DB_FILE


def load_config() -> dict[str, Any]:
    """Load user configuration from disk, falling back to defaults."""
    ensure_config_dir()
    if not CONFIG_FILE.exists():
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            merged = DEFAULT_CONFIG.copy()
            merged.update(data)
            return merged
    except Exception:
        return DEFAULT_CONFIG.copy()


def save_config(cfg: dict[str, Any]) -> None:
    """Save user configuration to disk."""
    ensure_config_dir()
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)


def has_thread_subdirs(p: Path) -> bool:
    """Check if directory contains at least one saved thread subdirectory."""
    if not p.exists() or not p.is_dir():
        return False
    try:
        return any(x.is_dir() and x.name != "media" for x in p.iterdir())
    except Exception:
        return False


def get_threads_dir() -> Path:
    """Get resolved threads directory, checking local ./threads and ~/threads."""
    cfg = load_config()
    p = Path(cfg.get("default_output_dir", "./threads")).expanduser()
    if has_thread_subdirs(p):
        return p.resolve()
    
    home_threads = Path.home() / "threads"
    if has_thread_subdirs(home_threads):
        return home_threads.resolve()
        
    return p.resolve()
