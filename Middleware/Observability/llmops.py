"""
LLMOps metrics for Council agents.

Captures what operators usually want for multi-agent Gemini runs:
- timestamps (start / first token / end)
- time-to-first-token (TTFT)
- end-to-end duration
- prompt / completion / total tokens
- estimated USD cost by model
- agent + model labels for Prometheus / OTEL

Wire `setup_observability()` once at API/process start, then call
`record_llm_call(...)` around each model generation (or from ADK callbacks).
"""

from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass, field
from typing import Mapping

logger = logging.getLogger(__name__)

# Approximate list prices USD / 1M tokens (override via env). Update when Google publishes rates.
# Keys: (input_per_1m, output_per_1m)
_DEFAULT_MODEL_RATES_USD_PER_1M: dict[str, tuple[float, float]] = {
    "gemini-4-hydrogen": (1.25, 10.0),
    "gemini-2.5-flash": (0.30, 2.50),
    "gemini-2.0-flash": (0.10, 0.40),
    "gemini-1.5-pro": (1.25, 5.00),
    "gemini-1.5-flash": (0.075, 0.30),
}

_METRICS_READY = False
_REQUESTS = None
_TOKENS = None
_COST = None
_DURATION = None
_TTFT = None
_TRACER = None


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

    # Allow env overrides: LLM_COST_<MODEL>_INPUT_PER_1M / _OUTPUT_PER_1M
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


def setup_observability(
    *,
    service_name: str = "council-of-ancients",
    otlp_endpoint: str | None = None,
    enable_prometheus_http: bool = True,
    prometheus_port: int | None = None,
) -> None:
    """
    Initialize OpenTelemetry (traces → collector/Jaeger/Phoenix) and Prometheus metrics.

    Safe to call multiple times. Soft-fails if optional deps are missing so local
    coding without the observability profile still imports cleanly.
    """
    global _METRICS_READY, _REQUESTS, _TOKENS, _COST, _DURATION, _TTFT, _TRACER

    if _METRICS_READY:
        return

    endpoint = (
        otlp_endpoint
        or os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
        or "http://localhost:4317"
    )
    # OTEL SDK expects host:port without scheme for some exporters; normalize.
    endpoint_for_exporter = endpoint.replace("http://", "").replace("https://", "")

    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
            OTLPSpanExporter,
        )
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
    except ImportError:
        logger.warning(
            "opentelemetry packages not installed; traces disabled. "
            "uv add opentelemetry-api opentelemetry-sdk "
            "opentelemetry-exporter-otlp-proto-grpc"
        )
        trace_provider = None
    else:
        resource = Resource.create(
            {
                "service.name": service_name,
                "service.namespace": "council-of-ancients",
                "deployment.environment": os.getenv("DEPLOY_ENV", "local"),
            }
        )
        provider = TracerProvider(resource=resource)
        provider.add_span_processor(
            BatchSpanProcessor(
                OTLPSpanExporter(endpoint=endpoint_for_exporter, insecure=True)
            )
        )
        # Optional second exporter: Phoenix OTLP (host maps 4319 → phoenix:4317)
        phoenix_ep = os.getenv("PHOENIX_OTLP_ENDPOINT")
        if phoenix_ep:
            phoenix_ep = phoenix_ep.replace("http://", "").replace("https://", "")
            provider.add_span_processor(
                BatchSpanProcessor(
                    OTLPSpanExporter(endpoint=phoenix_ep, insecure=True)
                )
            )
        trace.set_tracer_provider(provider)
        _TRACER = trace.get_tracer("council.llmops")
        trace_provider = provider

    try:
        from prometheus_client import (
            Counter,
            Histogram,
            start_http_server,
        )
    except ImportError:
        logger.warning(
            "prometheus_client not installed; /metrics scrape target disabled. "
            "uv add prometheus-client"
        )
    else:
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
        if enable_prometheus_http:
            port = int(
                prometheus_port
                or os.getenv("PROMETHEUS_METRICS_PORT", "9108")
            )
            start_http_server(port)
            logger.info("Prometheus metrics listening on :%s/metrics", port)

    _METRICS_READY = True
    logger.info(
        "Observability ready (otlp=%s, tracer=%s)",
        endpoint,
        bool(trace_provider),
    )


def record_llm_call(metrics: LLMCallMetrics) -> float:
    """
    Record one LLM call into Prometheus + an OTEL span.

    Returns estimated USD cost.
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

    if _REQUESTS is not None:
        _REQUESTS.labels(
            metrics.agent, metrics.model, metrics.status, wave
        ).inc()
        _TOKENS.labels(metrics.agent, metrics.model, "prompt").inc(
            metrics.prompt_tokens
        )
        _TOKENS.labels(metrics.agent, metrics.model, "completion").inc(
            metrics.completion_tokens
        )
        _COST.labels(metrics.agent, metrics.model).inc(cost)
        _DURATION.labels(metrics.agent, metrics.model).observe(
            metrics.duration_seconds
        )
        if metrics.ttft_seconds is not None:
            _TTFT.labels(metrics.agent, metrics.model).observe(
                metrics.ttft_seconds
            )

    if _TRACER is not None:
        from opentelemetry import trace
        from opentelemetry.trace import Status, StatusCode

        with _TRACER.start_as_current_span(
            f"llm.{metrics.agent}",
            start_time=int(metrics.started_at_unix * 1e9),
        ) as span:
            span.set_attribute("gen_ai.system", "vertex_ai")
            span.set_attribute("gen_ai.request.model", metrics.model)
            span.set_attribute("gen_ai.operation.name", "chat")
            span.set_attribute("council.agent", metrics.agent)
            span.set_attribute("council.wave", wave)
            span.set_attribute("gen_ai.usage.input_tokens", metrics.prompt_tokens)
            span.set_attribute(
                "gen_ai.usage.output_tokens", metrics.completion_tokens
            )
            span.set_attribute("council.cost_usd", cost)
            span.set_attribute("council.duration_seconds", metrics.duration_seconds)
            if metrics.ttft_seconds is not None:
                span.set_attribute("council.ttft_seconds", metrics.ttft_seconds)
            if metrics.session_id:
                span.set_attribute("council.session_id", metrics.session_id)
            if metrics.status != "ok":
                span.set_status(Status(StatusCode.ERROR, metrics.status))
            # End time is approximate when using context manager; attributes carry truth.

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
