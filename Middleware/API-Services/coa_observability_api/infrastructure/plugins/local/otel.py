"""Local OpenTelemetry traces plugin (soft-imports OTEL SDK)."""

from __future__ import annotations

import logging
import os
import threading
import time
from typing import Any, ClassVar

from coa_observability_api.domain.models import ObsFeedEvent
from coa_observability_api.infrastructure.plugins.base import ObservabilityPlugin

logger = logging.getLogger(__name__)

_LOCK = threading.Lock()
_TRACER: Any = None
_INIT_ATTEMPTED = False


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


def _ensure_tracer() -> Any:
    global _TRACER, _INIT_ATTEMPTED
    if _INIT_ATTEMPTED:
        return _TRACER
    with _LOCK:
        if _INIT_ATTEMPTED:
            return _TRACER
        _INIT_ATTEMPTED = True
        endpoint = (
            os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT") or "http://localhost:4317"
        )
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
            logger.warning("opentelemetry packages missing; local otel plugin disabled")
            return None

        service_name = os.getenv("OTEL_SERVICE_NAME", "coa-observability-api")
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
        phoenix_ep = os.getenv("PHOENIX_OTLP_ENDPOINT")
        if phoenix_ep:
            phoenix_ep = phoenix_ep.replace("http://", "").replace("https://", "")
            provider.add_span_processor(
                BatchSpanProcessor(
                    OTLPSpanExporter(endpoint=phoenix_ep, insecure=True)
                )
            )
        # Avoid clobbering an existing global provider if one is already set.
        try:
            existing = trace.get_tracer_provider()
            from opentelemetry.sdk.trace import TracerProvider as SDKProvider

            if not isinstance(existing, SDKProvider):
                trace.set_tracer_provider(provider)
        except Exception:
            trace.set_tracer_provider(provider)

        _TRACER = trace.get_tracer("council.llmops")
        logger.info("OTEL tracer ready (otlp=%s)", endpoint)
        return _TRACER


class OtelPlugin(ObservabilityPlugin):
    name: ClassVar[str] = "local.otel"
    domains: ClassVar[tuple[str, ...]] = ("traces", "llmops")

    def _emit(self, event: ObsFeedEvent) -> None:
        tracer = _ensure_tracer()
        if tracer is None:
            return
        call = event.llm_call
        if call is None:
            logger.debug("otel skip: no llm_call ingest_id=%s", event.ingest_id)
            return

        from opentelemetry.trace import Status, StatusCode

        wave = call.deliberation_wave or "unknown"
        started = call.started_at_unix or time.time()
        cost = _estimate_cost_usd(call.model, call.prompt_tokens, call.completion_tokens)
        with tracer.start_as_current_span(
            f"llm.{call.agent}",
            start_time=int(started * 1e9),
        ) as span:
            span.set_attribute("gen_ai.system", "vertex_ai")
            span.set_attribute("gen_ai.request.model", call.model)
            span.set_attribute("gen_ai.operation.name", "chat")
            span.set_attribute("council.agent", call.agent)
            span.set_attribute("council.wave", wave)
            span.set_attribute("gen_ai.usage.input_tokens", call.prompt_tokens)
            span.set_attribute("gen_ai.usage.output_tokens", call.completion_tokens)
            span.set_attribute("council.cost_usd", cost)
            span.set_attribute("council.duration_seconds", call.duration_seconds)
            span.set_attribute("council.ingest_id", event.ingest_id)
            span.set_attribute("council.session_id", event.session_id)
            if call.ttft_seconds is not None:
                span.set_attribute("council.ttft_seconds", call.ttft_seconds)
            if call.status != "ok":
                span.set_status(Status(StatusCode.ERROR, call.status))
        logger.debug("otel span emitted ingest_id=%s", event.ingest_id)
