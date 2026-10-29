"""Authentication management using session cookies."""

from typing import Any
from twscrape import API, AccountsPool
from twscrape.utils import parse_cookies
from twscrape.account import has_required_cookies
from twscrape.logger import set_log_level
from xthread.config import get_db_path

# Mute noisy internal logging by default
set_log_level("ERROR")


def get_pool() -> AccountsPool:
    """Get the twscrape AccountsPool instance configured with xthread's DB."""
    db_file = str(get_db_path())
    return AccountsPool(db_file=db_file)


def get_api() -> API:
    """Get the twscrape API instance."""
    pool = get_pool()
    return API(pool=pool)


async def add_session(
    auth_token: str | None = None,
    ct0: str | None = None,
    raw_cookies: str | None = None,
    username: str = "minha_conta",
) -> bool:
    """Add or update an account with session cookies."""
    pool = get_pool()

    if raw_cookies:
        parsed = parse_cookies(raw_cookies)
    elif auth_token and ct0:
        parsed = parse_cookies(f"auth_token={auth_token.strip()}; ct0={ct0.strip()}")
    else:
        raise ValueError("É necessário informar auth_token e ct0, ou a string completa de cookies.")

    if not has_required_cookies(parsed):
        raise ValueError("Os cookies fornecidos não contêm auth_token e ct0 válidos.")

    cookie_str = "; ".join(f"{k}={v}" for k, v in parsed.items())
    await pool.add_account_cookies(username=username, cookies=cookie_str)
    return True


async def check_auth_status() -> dict[str, Any]:
    """Check the current authentication status and verify if session works."""
    pool = get_pool()
    accounts = await pool.accounts_info()

    if not accounts:
        return {
            "authenticated": False,
            "accounts_count": 0,
            "active_count": 0,
            "message": "Nenhuma conta ou cookie configurado ainda.",
            "accounts": [],
        }

    active_count = sum(1 for a in accounts if a.get("active"))
    api = get_api()

    # Try a fast query to verify session validity
    is_valid = False
    test_msg = ""
    try:
        # Jack's first tweet (id: 20)
        test_tweet = await api.tweet_details(20)
        if test_tweet:
            is_valid = True
            test_msg = "Sessão válida e respondendo perfeitamente ao X."
        else:
            test_msg = "Aviso: A requisição não retornou dados. Os cookies podem ter expirado."
    except Exception as e:
        test_msg = f"Erro na conexão com o X: {e}"

    return {
        "authenticated": is_valid,
        "accounts_count": len(accounts),
        "active_count": active_count,
        "message": test_msg,
        "accounts": accounts,
    }


async def clear_all_sessions() -> bool:
    """Clear all stored accounts and sessions."""
    db_path = get_db_path()
    if db_path.exists():
        try:
            db_path.unlink()
            return True
        except Exception:
            return False
    return True
