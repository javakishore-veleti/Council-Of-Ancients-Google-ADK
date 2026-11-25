"""AIOps / LLMOps / DataOps instrumentation for Council of Ancients."""

from __future__ import annotations

from .llmops import (
    LLMCallMetrics,
    estimate_cost_usd,
    record_llm_call,
    setup_observability,
)


def get_observability_facade():
    """Re-export facade entry (lazy import; adds API-Services to sys.path)."""
    from .llmops import _get_facade

    return _get_facade()


__all__ = [
    "LLMCallMetrics",
    "estimate_cost_usd",
    "record_llm_call",
    "setup_observability",
    "get_observability_facade",
]
