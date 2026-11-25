from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import license_gate, paths

USER_AGENT = "CouncilOfAncientsKB/0.1 (+local-airflow; foundations-ingest)"


def load_allowlist(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def fetch_source(topic_id: str, source: dict[str, Any], pause_s: float = 0.75) -> dict[str, Any]:
    """Download one allowlisted URL into KB_LOCAL_ROOT/raw/..."""
    source_id = source["source_id"]
    license_id = source.get("license")
    if not license_gate.allowed(license_id):
        return {
            "source_id": source_id,
            "status": "denied_license",
            "license": license_id,
        }

    dest = paths.topic_raw(topic_id, source_id)
    dest.mkdir(parents=True, exist_ok=True)
    meta_path = dest / "meta.json"
    body_path = dest / "original.html"

    url = source["url"]
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            raw = resp.read()
            ctype = resp.headers.get("Content-Type", "text/html")
            etag = resp.headers.get("ETag")
            final_url = resp.geturl()
    except urllib.error.HTTPError as exc:
        return {"source_id": source_id, "status": "http_error", "code": exc.code, "url": url}
    except urllib.error.URLError as exc:
        return {"source_id": source_id, "status": "url_error", "error": str(exc.reason), "url": url}

    suffix = ".html"
    if "pdf" in ctype.lower() or final_url.lower().endswith(".pdf"):
        suffix = ".pdf"
        body_path = dest / f"original{suffix}"

    body_path.write_bytes(raw)
    meta = {
        "source_id": source_id,
        "topic_id": topic_id,
        "url": url,
        "final_url": final_url,
        "title": source.get("title"),
        "license": license_id,
        "subcategory": source.get("subcategory"),
        "content_type": ctype,
        "etag": etag,
        "bytes": len(raw),
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "status": "fetched",
    }
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    time.sleep(pause_s)
    return meta


def fetch_allowlist(allowlist_path: str | Path) -> list[dict[str, Any]]:
    data = load_allowlist(Path(allowlist_path))
    topic_id = data["topic_id"]
    results: list[dict[str, Any]] = []
    for source in data.get("sources", []):
        if source.get("status") != "active":
            continue
        results.append(fetch_source(topic_id, source))
    summary = paths.kb_root() / "derived" / topic_id / "_fetch_summary.json"
    summary.parent.mkdir(parents=True, exist_ok=True)
    summary.write_text(json.dumps(results, indent=2), encoding="utf-8")
    return results
