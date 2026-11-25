"""Local Prometheus metrics plugin (soft-imports prometheus_client)."""

from __future__ import annotations

import logging
import os
import threading
from typing import Any, ClassVar

from coa_observability_api.domain.models import ObsFeedEvent
from coa_observability_api.infrastructure.plugins.base import ObservabilityPlugin

logger = logging.getLogger(__name__)

_LOCK = threading.Lock()
_READY = False
_REQUESTS: Any = None
_TOKENS: Any = None
_COST: Any = None
_DURATION: Any = None
_TTFT: Any = None
_HTTP_STARTED = False


def _estimate_cost_usd(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    """Local cost estimate (ported from Observability/llmops; avoid circular import)."""
    rates = {
        "gemini-4-hydrogen": (1.25, 10.0),
        "gemini-2.5-flash": (0.30, 2.50),
        "gemini-2.0-flash": (0.10, 0.40),
        "gemini-1.5-pro": (1.25, 5.00),
        "gemini-1.5-flash": (0.075, 0.30),
    }
    env_key = model.upper().replace("-", "_").replace(".", "_")
    in_env = os.getenv(f"LLM_COST_{env_key}_INPUT_PER_1M")
    out_env = os.getenv(f"LLM_COST_{env_key}_OUTPUT_PER_1M")
    inp, out = rates.get(model, (1.25, 10.0))
    if in_env:
        inp = float(in_env)
    if out_env:
        out = float(out_env)
    return (prompt_tokens / 1_000_000.0) * inp + (completion_tokens / 1_000_000.0) * out


def _ensure_metrics(*, enable_http: bool = True) -> bool:
    global _READY, _REQUESTS, _TOKENS, _COST, _DURATION, _TTFT, _HTTP_STARTED
    if _READY:
        return _REQUESTS is not None

    with _LOCK:
        if _READY:
            return _REQUESTS is not None
        try:
            from prometheus_client import Counter, Histogram, start_http_server
        except ImportError:
            logger.warning(
                "prometheus_client not installed; local prometheus plugin disabled"
            )
            _READY = True
            return False

        _REQUESTS = Counter(
            "council_llm_requests_total",
            "LLM generations attempted",
            ["agent", "model", "status", "wave"],
        )
        _TOKENS = Counter(
            "council_llm_tokens_total",
            "LLM tokens consumed",
            ["agent", "model", "token_type"],
        )
        _COST = Counter(
            "council_llm_cost_usd_total",
            "Estimated LLM cost in USD",
            ["agent", "model"],
        )
        _DURATION = Histogram(
            "council_llm_duration_seconds",
            "LLM end-to-end generation latency",
            ["agent", "model"],
            buckets=(0.1, 0.25, 0.5, 1, 2, 5, 10, 20, 40, 80, 160),
        )
        _TTFT = Histogram(
            "council_llm_ttft_seconds",
            "LLM time to first token",
            ["agent", "model"],
            buckets=(0.05, 0.1, 0.25, 0.5, 1, 2, 5, 10, 20, 40),
        )
        disable_http = os.getenv("OBS_DISABLE_PROMETHEUS_HTTP", "").lower() in {
            "1",
            "true",
            "yes",
            "on",
        }
        if enable_http and not disable_http and not _HTTP_STARTED:
            port = int(os.getenv("PROMETHEUS_METRICS_PORT", "9108"))
            try:
                start_http_server(port)
                _HTTP_STARTED = True
                logger.info("Prometheus metrics listening on :%s/metrics", port)
            except OSError as exc:
                # Port already bound (another process) — scrape still works via that process.
                logger.warning(
                    "Prometheus HTTP server not started on :%s (%s)", port, exc
                )
                _HTTP_STARTED = True
        _READY = True
        return True


class PrometheusPlugin(ObservabilityPlugin):
    name: ClassVar[str] = "local.prometheus"
    domains: ClassVar[tuple[str, ...]] = ("metrics", "llmops")

    def _emit(self, event: ObsFeedEvent) -> None:
        if not _ensure_metrics():
            return
        call = event.llm_call
        if call is None:
            logger.debug(
                "prometheus skip: no llm_call in obs_data ingest_id=%s",
                event.ingest_id,
            )
            return

        wave = call.deliberation_wave or "unknown"
        cost = _estimate_cost_usd(call.model, call.prompt_tokens, call.completion_tokens)
        _REQUESTS.labels(call.agent, call.model, call.status, wave).inc()
        _TOKENS.labels(call.agent, call.model, "prompt").inc(call.prompt_tokens)
        _TOKENS.labels(call.agent, call.model, "completion").inc(call.completion_tokens)
        _COST.labels(call.agent, call.model).inc(cost)
        if call.duration_seconds > 0:
            _DURATION.labels(call.agent, call.model).observe(call.duration_seconds)
        if call.ttft_seconds is not None:
            _TTFT.labels(call.agent, call.model).observe(call.ttft_seconds)
        logger.debug(
            "prometheus recorded ingest_id=%s agent=%s model=%s",
            event.ingest_id,
            call.agent,
            call.model,
        )
