"""
LLMOps helpers for Council agents.

Thin layer: cost estimation + emit into ObservabilityFacade.
Vendor fan-out lives under Middleware/API-Services/coa_observability_api
(tasks → sub-facades → plugins), gated by OBS_TASK_* env flags (default off).
"""

from __future__ import annotations

import logging
import os
import sys
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping

logger = logging.getLogger(__name__)

# Approximate list prices USD / 1M tokens (override via env). Update when Google publishes rates.
_DEFAULT_MODEL_RATES_USD_PER_1M: dict[str, tuple[float, float]] = {
    "gemini-4-hydrogen": (1.25, 10.0),
    "gemini-2.5-flash": (0.30, 2.50),
    "gemini-2.0-flash": (0.10, 0.40),
    "gemini-1.5-pro": (1.25, 5.00),
    "gemini-1.5-flash": (0.075, 0.30),
}


@dataclass
class LLMCallMetrics:
    """One completed (or failed) LLM generation."""

    agent: str
    model: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    duration_seconds: float = 0.0
    ttft_seconds: float | None = None
    started_at_unix: float = field(default_factory=time.time)
    first_token_at_unix: float | None = None
    ended_at_unix: float | None = None
    status: str = "ok"  # ok | error | blocked
    deliberation_wave: str | None = None  # framing | openings | rebuttals | synthesis
    session_id: str | None = None

    @property
    def total_tokens(self) -> int:
        return int(self.prompt_tokens) + int(self.completion_tokens)


def estimate_cost_usd(
    model: str,
    prompt_tokens: int,
    completion_tokens: int,
    rates: Mapping[str, tuple[float, float]] | None = None,
) -> float:
    """Estimate USD cost from token counts and per-1M rates."""
    table = dict(_DEFAULT_MODEL_RATES_USD_PER_1M)
    if rates:
        table.update(rates)

    env_key = model.upper().replace("-", "_").replace(".", "_")
    in_env = os.getenv(f"LLM_COST_{env_key}_INPUT_PER_1M")
    out_env = os.getenv(f"LLM_COST_{env_key}_OUTPUT_PER_1M")
    input_rate, output_rate = table.get(model, table.get("gemini-4-hydrogen", (1.25, 10.0)))
    if in_env:
        input_rate = float(in_env)
    if out_env:
        output_rate = float(out_env)

    return (prompt_tokens / 1_000_000.0) * input_rate + (
        completion_tokens / 1_000_000.0
    ) * output_rate


def _ensure_api_on_path() -> None:
    api_root = Path(__file__).resolve().parents[1] / "API-Services"
    path = str(api_root)
    if path not in sys.path:
        sys.path.insert(0, path)


def _get_facade():
    _ensure_api_on_path()
    from coa_observability_api.application.facade.observability_facade import (
        get_observability_facade,
    )

    return get_observability_facade()


def setup_observability(
    *,
    service_name: str = "council-of-ancients",
    otlp_endpoint: str | None = None,
    enable_prometheus_http: bool = True,
    prometheus_port: int | None = None,
) -> None:
    """
    Compatibility shim.

    Real fan-out is toggle-gated via ObservabilityFacade / coa_observability_api.
    Optional kwargs are retained for call-site compatibility and applied as env
    defaults when unset so local plugins can pick them up.
    """
    if otlp_endpoint and not os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"):
        os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = otlp_endpoint
    if prometheus_port is not None and not os.getenv("PROMETHEUS_METRICS_PORT"):
        os.environ["PROMETHEUS_METRICS_PORT"] = str(prometheus_port)
    if service_name and not os.getenv("OTEL_SERVICE_NAME"):
        os.environ["OTEL_SERVICE_NAME"] = service_name
    if not enable_prometheus_http:
        os.environ.setdefault("OBS_DISABLE_PROMETHEUS_HTTP", "true")
    logger.info(
        "setup_observability: facade ready; enable fan-out with OBS_TASK_EMIT_* "
        "(metrics/traces/logs/llmops). service=%s",
        service_name,
    )


def record_llm_call(metrics: LLMCallMetrics) -> float:
    """
    Normalize timings, estimate cost, emit into ObservabilityFacade (soft-fail).

    Returns estimated USD cost. Vendor plugins run only when matching OBS_TASK_*
    flags are true.
    """
    if metrics.ended_at_unix is None:
        metrics.ended_at_unix = time.time()
    if metrics.duration_seconds <= 0 and metrics.started_at_unix:
        metrics.duration_seconds = max(
            0.0, metrics.ended_at_unix - metrics.started_at_unix
        )
    if (
        metrics.ttft_seconds is None
        and metrics.first_token_at_unix is not None
        and metrics.started_at_unix
    ):
        metrics.ttft_seconds = max(
            0.0, metrics.first_token_at_unix - metrics.started_at_unix
        )

    cost = estimate_cost_usd(
        metrics.model, metrics.prompt_tokens, metrics.completion_tokens
    )
    wave = metrics.deliberation_wave or "unknown"
    session_id = metrics.session_id or "local"

    obs_data = {
        "event_type": "llm_call",
        "agent": metrics.agent,
        "model": metrics.model,
        "prompt_tokens": metrics.prompt_tokens,
        "completion_tokens": metrics.completion_tokens,
        "duration_seconds": metrics.duration_seconds,
        "ttft_seconds": metrics.ttft_seconds,
        "started_at_unix": metrics.started_at_unix,
        "first_token_at_unix": metrics.first_token_at_unix,
        "ended_at_unix": metrics.ended_at_unix,
        "status": metrics.status,
        "deliberation_wave": metrics.deliberation_wave,
        "cost_usd": cost,
    }

    # Prefer HTTP ingest into coa_observability_api container so plugins/metrics
    # live in one place. Fall back to in-process facade when URL unset/unreachable.
    obs_api = (os.getenv("COA_OBS_API_URL") or "http://localhost:8088").rstrip("/")
    posted = False
    try:
        import json
        import urllib.error
        import urllib.request

        body = json.dumps(
            {
                "session_id": session_id,
                "ctx_data": {
                    "service": os.getenv("OTEL_SERVICE_NAME", "coa_agents_api"),
                    "agent": metrics.agent,
                    "wave": wave,
                    "obs_data": obs_data,
                },
            }
        ).encode("utf-8")
        req = urllib.request.Request(
            f"{obs_api}/v1/obs/feed",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=2.0) as resp:
            posted = 200 <= getattr(resp, "status", 0) < 300
    except Exception:
        logger.debug(
            "record_llm_call HTTP ingest soft-fail; trying in-process facade",
            exc_info=True,
        )

    if not posted:
        try:
            facade = _get_facade()
            from coa_observability_api.domain.models import ObsFeedEvent

            event = ObsFeedEvent(
                ingest_id=str(uuid.uuid4()),
                session_id=session_id,
                ctx_data={"obs_data": obs_data},
                obs_data=obs_data,
            )
            facade.emit_sync(event)
        except Exception:
            logger.exception(
                "record_llm_call facade soft-fail agent=%s model=%s",
                metrics.agent,
                metrics.model,
            )

    logger.info(
        "llm_call agent=%s model=%s status=%s wave=%s prompt_tokens=%s "
        "completion_tokens=%s duration_s=%.3f ttft_s=%s cost_usd=%.6f",
        metrics.agent,
        metrics.model,
        metrics.status,
        wave,
        metrics.prompt_tokens,
        metrics.completion_tokens,
        metrics.duration_seconds,
        f"{metrics.ttft_seconds:.3f}" if metrics.ttft_seconds is not None else "n/a",
        cost,
    )
    return cost
