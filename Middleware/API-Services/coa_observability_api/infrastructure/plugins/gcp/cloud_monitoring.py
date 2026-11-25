"""GCP Cloud Monitoring / Cloud Trace stub (no-op + log once)."""

from __future__ import annotations

import logging
from typing import ClassVar

from coa_observability_api.domain.models import ObsFeedEvent
from coa_observability_api.infrastructure.plugins.base import ObservabilityPlugin

logger = logging.getLogger(__name__)
_LOGGED = False


class GcpCloudMonitoringPlugin(ObservabilityPlugin):
    name: ClassVar[str] = "gcp.cloud_monitoring"
    domains: ClassVar[tuple[str, ...]] = ("metrics", "traces", "logs", "llmops")

    def _emit(self, event: ObsFeedEvent) -> None:
        global _LOGGED
        if not _LOGGED:
            logger.info(
                "gcp plugin stub active (no-op); ingest_id=%s — wire Cloud Monitoring later",
                event.ingest_id,
            )
            _LOGGED = True
