from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass
class ExtractOptions:
    """Options passed into any extract strategy (DAG-agnostic)."""

    render_js: bool = False
    user_agent: str = "CouncilOfAncientsKB/0.1 (+kb-extract; allowlisted-ingest)"
    timeout_s: float = 45.0
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class ExtractResult:
    """Contract every extractor must satisfy — Markdown is required for RAG."""

    markdown: str
    html: str | None = None
    structured: dict[str, Any] | None = None
    meta: dict[str, Any] = field(default_factory=dict)
    strategy_id: str = "generic_markdown"


class ExtractStrategy(Protocol):
    """Pluggable extractor. Swap implementations without changing the facade DAG."""

    id: str

    def extract(self, url: str, options: ExtractOptions | None = None) -> ExtractResult:
        ...
