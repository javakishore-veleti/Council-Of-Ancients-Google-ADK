"""LLMOps sub-facade → LLMOps-capable plugins (metrics + traces + cost)."""

from __future__ import annotations

import logging

from coa_observability_api.domain.models import ObsFeedEvent
from coa_observability_api.infrastructure.plugins.aws import AwsCloudWatchPlugin
from coa_observability_api.infrastructure.plugins.azure import AzureMonitorPlugin
from coa_observability_api.infrastructure.plugins.base import ObservabilityPlugin
from coa_observability_api.infrastructure.plugins.gcp import GcpCloudMonitoringPlugin
from coa_observability_api.infrastructure.plugins.langchain import LangSmithPlugin
from coa_observability_api.infrastructure.plugins.local import (
    OtelPlugin,
    PhoenixPlugin,
    PrometheusPlugin,
)

logger = logging.getLogger(__name__)


class LlmOpsSubFacade:
    def __init__(self, plugins: list[ObservabilityPlugin] | None = None) -> None:
        self._plugins = plugins or [
            PrometheusPlugin(),
            OtelPlugin(),
            PhoenixPlugin(),
            GcpCloudMonitoringPlugin(),
            AwsCloudWatchPlugin(),
            AzureMonitorPlugin(),
            LangSmithPlugin(),
        ]

    def emit(self, event: ObsFeedEvent) -> None:
        for plugin in self._plugins:
            try:
                plugin.emit(event)
            except Exception:
                logger.exception(
                    "llmops sub-facade soft-fail plugin=%s ingest_id=%s",
                    getattr(plugin, "name", "?"),
                    event.ingest_id,
                )
