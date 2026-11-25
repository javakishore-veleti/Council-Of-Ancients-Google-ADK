"""Base class for observability vendor plugins."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import ClassVar

from coa_observability_api.domain.models import ObsFeedEvent

logger = logging.getLogger(__name__)


class ObservabilityPlugin(ABC):
    """One vendor sink. Soft-fail: never raise out of emit()."""

    name: ClassVar[str] = "unnamed"
    domains: ClassVar[tuple[str, ...]] = ()  # metrics | traces | logs | llmops

    def emit(self, event: ObsFeedEvent) -> None:
        try:
            self._emit(event)
        except Exception:
            logger.exception(
                "observability plugin soft-fail name=%s ingest_id=%s",
                self.name,
                event.ingest_id,
            )

    @abstractmethod
    def _emit(self, event: ObsFeedEvent) -> None:
        """Vendor-specific emit; may raise (caught by emit)."""
