from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .extract.base import ExtractResult
from .paths import source_store_dir


def write_extract_artifacts(
    *,
    category_code: str,
    subcategory_code: str,
    source_id: str,
    result: ExtractResult,
    extra_meta: dict[str, Any] | None = None,
) -> Path:
    """Persist extract output under KnowledgeBase UUID leaf."""
    dest = source_store_dir(category_code, subcategory_code, source_id)
    dest.mkdir(parents=True, exist_ok=True)

    (dest / "content.md").write_text(result.markdown, encoding="utf-8")
    if result.html is not None:
        (dest / "original.html").write_text(result.html, encoding="utf-8")
    if result.structured is not None:
        (dest / "structured.json").write_text(
            json.dumps(result.structured, indent=2),
            encoding="utf-8",
        )

    meta = {
        "source_id": source_id,
        "category_code": category_code,
        "subcategory_code": subcategory_code,
        "strategy_id": result.strategy_id,
        "stored_at": datetime.now(timezone.utc).isoformat(),
        **(result.meta or {}),
        **(extra_meta or {}),
    }
    (dest / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return dest
