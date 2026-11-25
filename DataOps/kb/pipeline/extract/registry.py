from __future__ import annotations

from typing import Callable
from urllib.parse import urlparse

from .base import ExtractStrategy

_REGISTRY: dict[str, ExtractStrategy] = {}
# host suffix → strategy id (optional host extractors; empty until registered)
_HOST_ROUTES: list[tuple[str, str]] = []


def register_strategy(strategy: ExtractStrategy) -> ExtractStrategy:
    _REGISTRY[strategy.id] = strategy
    return strategy


def register_host_route(host_suffix: str, strategy_id: str) -> None:
    """Map a host (e.g. wikipedia.org) to a strategy id for sparse host extractors."""
    suffix = host_suffix.lower().lstrip(".")
    _HOST_ROUTES.append((suffix, strategy_id))


def get_strategy(strategy_id: str) -> ExtractStrategy:
    try:
        return _REGISTRY[strategy_id]
    except KeyError as exc:
        known = ", ".join(sorted(_REGISTRY)) or "(none)"
        raise KeyError(f"unknown extract strategy {strategy_id!r}; known: {known}") from exc


def list_strategies() -> list[str]:
    return sorted(_REGISTRY)


def resolve_strategy_id(url: str, override: str | None = None) -> str:
    """Pick strategy for a URL. Override wins; else host route; else generic_markdown."""
    if override:
        return override
    host = (urlparse(url).hostname or "").lower()
    for suffix, strategy_id in _HOST_ROUTES:
        if host == suffix or host.endswith("." + suffix):
            if strategy_id in _REGISTRY:
                return strategy_id
    return "generic_markdown"


def strategy_factory(strategy_id: str) -> Callable[[], ExtractStrategy]:
    def _factory() -> ExtractStrategy:
        return get_strategy(strategy_id)

    return _factory
