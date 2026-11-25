from __future__ import annotations

import os
import ssl
import urllib.error
import urllib.request
import urllib.robotparser
from urllib.parse import urlparse


def _ssl_context() -> ssl.SSLContext:
    if os.environ.get("COA_KB_SSL_INSECURE", "").strip() in {"1", "true", "yes"}:
        return ssl._create_unverified_context()
    try:
        import certifi

        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return ssl.create_default_context()


def allowed_by_robots(url: str, user_agent: str) -> bool:
    """Best-effort robots.txt check. Fail-open if robots cannot be fetched."""
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        return False
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    try:
        req = urllib.request.Request(
            robots_url,
            headers={"User-Agent": user_agent or "CouncilOfAncientsKB/0.1"},
        )
        with urllib.request.urlopen(req, timeout=15, context=_ssl_context()) as resp:
            body = resp.read().decode("utf-8", errors="replace")
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError):
        # 401/403/network: RobotFileParser.read() would set disallow_all — fail open.
        return True

    rp = urllib.robotparser.RobotFileParser()
    rp.parse(body.splitlines())
    try:
        return bool(rp.can_fetch(user_agent, url))
    except Exception:
        return True
