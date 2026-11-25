from __future__ import annotations

from typing import Any

from .extract import ExtractOptions, get_strategy, resolve_strategy_id
from .store import write_extract_artifacts


def run_extract(
    *,
    url: str,
    source_id: str,
    category_code: str,
    subcategory_code: str,
    strategy_id: str | None = None,
    render_js: bool = False,
) -> dict[str, Any]:
    """Core extract step — called by kb_extract DAG (or tests). Swappable via strategy_id."""
    resolved = resolve_strategy_id(url, override=strategy_id)
    strategy = get_strategy(resolved)
    result = strategy.extract(url, ExtractOptions(render_js=render_js))
    dest = write_extract_artifacts(
        category_code=category_code,
        subcategory_code=subcategory_code,
        source_id=source_id,
        result=result,
        extra_meta={"requested_strategy_id": strategy_id, "resolved_strategy_id": resolved},
    )
    return {
        "store_dir": str(dest),
        "strategy_id": result.strategy_id,
        "markdown_chars": len(result.markdown or ""),
        "has_html": result.html is not None,
        "meta": result.meta,
    }
