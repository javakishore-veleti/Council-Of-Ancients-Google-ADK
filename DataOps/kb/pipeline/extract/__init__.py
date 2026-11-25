"""URL extract strategies — invoked by kb_extract DAG, never by Admin directly."""

from .base import ExtractOptions, ExtractResult, ExtractStrategy
from .registry import get_strategy, list_strategies, register_strategy, resolve_strategy_id

# Register built-ins on import.
from . import generic_markdown as _generic_markdown  # noqa: F401

__all__ = [
    "ExtractOptions",
    "ExtractResult",
    "ExtractStrategy",
    "get_strategy",
    "list_strategies",
    "register_strategy",
    "resolve_strategy_id",
]
