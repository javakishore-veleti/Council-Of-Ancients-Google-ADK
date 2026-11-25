from __future__ import annotations

import urllib.robotparser
from urllib.parse import urlparse


def allowed_by_robots(url: str, user_agent: str) -> bool:
    """Best-effort robots.txt check. Fail-open if robots cannot be fetched."""
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        return False
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(robots_url)
    try:
        rp.read()
    except Exception:
        return True
    try:
        return bool(rp.can_fetch(user_agent, url))
    except Exception:
        return True
