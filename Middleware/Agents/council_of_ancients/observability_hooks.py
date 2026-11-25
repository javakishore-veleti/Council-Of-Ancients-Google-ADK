"""ADK after_model callbacks → ObservabilityFacade (soft-fail)."""

from __future__ import annotations

import logging
import time
from contextvars import ContextVar
from typing import Any

logger = logging.getLogger(__name__)

obs_session_id: ContextVar[str] = ContextVar("obs_session_id", default="local")
obs_wave: ContextVar[str | None] = ContextVar("obs_wave", default=None)


def after_model_obs(ctx: Any, llm_response: Any) -> None:
    """Record one model generation into the observability facade."""
    try:
        import sys
        from pathlib import Path

        repo_root = Path(__file__).resolve().parents[3]
        for p in (str(repo_root), str(repo_root / "Middleware")):
            if p not in sys.path:
                sys.path.insert(0, p)
        from Middleware.Observability.llmops import LLMCallMetrics, record_llm_call
    except Exception:
        logger.debug("observability helpers unavailable; skip emit", exc_info=True)
        return

    agent_name = "unknown"
    model_name = ""
    try:
        agent_name = getattr(ctx, "agent_name", None) or agent_name
        node = getattr(ctx, "node", None)
        if node is not None:
            agent_name = getattr(node, "name", None) or agent_name
            model_name = str(getattr(node, "model", "") or "")
        if not model_name:
            inv = getattr(ctx, "_invocation_context", None)
            agent = getattr(inv, "agent", None) if inv is not None else None
            if agent is not None:
                agent_name = getattr(agent, "name", None) or agent_name
                model_name = str(getattr(agent, "model", "") or "")
    except Exception:
        pass

    prompt_tokens = 0
    completion_tokens = 0
    status = "ok"
    try:
        usage = getattr(llm_response, "usage_metadata", None)
        if usage is not None:
            prompt_tokens = int(
                getattr(usage, "prompt_token_count", None)
                or getattr(usage, "input_tokens", None)
                or 0
            )
            completion_tokens = int(
                getattr(usage, "candidates_token_count", None)
                or getattr(usage, "output_tokens", None)
                or 0
            )
        if getattr(llm_response, "error_code", None) or getattr(
            llm_response, "error_message", None
        ):
            status = "error"
    except Exception:
        logger.debug("usage_metadata parse soft-fail", exc_info=True)

    if not model_name:
        model_name = str(getattr(llm_response, "model_version", None) or "unknown")

    try:
        record_llm_call(
            LLMCallMetrics(
                agent=agent_name,
                model=model_name,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                started_at_unix=time.time(),
                ended_at_unix=time.time(),
                status=status,
                deliberation_wave=obs_wave.get(),
                session_id=obs_session_id.get(),
            )
        )
    except Exception:
        logger.exception("after_model_obs soft-fail agent=%s", agent_name)
    return None
