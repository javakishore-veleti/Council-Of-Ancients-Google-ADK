"""Azure Monitor / App Insights stub (no-op + log once)."""

from __future__ import annotations

import logging
from typing import ClassVar

from coa_observability_api.domain.models import ObsFeedEvent
from coa_observability_api.infrastructure.plugins.base import ObservabilityPlugin

logger = logging.getLogger(__name__)
_LOGGED = False


class AzureMonitorPlugin(ObservabilityPlugin):
    name: ClassVar[str] = "azure.monitor"
    domains: ClassVar[tuple[str, ...]] = ("metrics", "traces", "logs", "llmops")

    def _emit(self, event: ObsFeedEvent) -> None:
        global _LOGGED
        if not _LOGGED:
            logger.info(
                "azure plugin stub active (no-op); ingest_id=%s — wire Azure Monitor later",
                event.ingest_id,
            )
            _LOGGED = True
