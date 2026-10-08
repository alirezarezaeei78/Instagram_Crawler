"""Pure validation helpers; importing this module never opens a browser."""
import re
from urllib.parse import urlsplit

RESERVED = {"accounts", "explore", "direct", "p", "reel", "reels", "stories", "about", "legal"}


def profile_username(href):
    """Return a username only for a single-segment Instagram profile URL."""
    if not href:
        return None
    parsed = urlsplit(href)
    if parsed.scheme not in {"", "https"}:
        return None
    if parsed.netloc and parsed.hostname not in {"instagram.com", "www.instagram.com"}:
        return None
    parts = parsed.path.strip("/").split("/")
    if len(parts) != 1 or parts[0].lower() in RESERVED:
        return None
    return parts[0] if re.fullmatch(r"[A-Za-z0-9_.]{1,30}", parts[0]) else None


def validate_configuration(username, password, target, scroll_limit):
    if not username or not password:
        raise ValueError("Set INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD in your environment or .env file.")
    if profile_username('/' + target.strip('/') + '/') != target:
        raise ValueError("Set TARGET_USER to a valid Instagram username without a URL or @ prefix.")
    if scroll_limit < 1:
        raise ValueError("SCROLL_LIMIT must be positive.")
