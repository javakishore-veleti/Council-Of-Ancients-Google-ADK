"""Base observability task (toggle-gated, soft-fail)."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod

from coa_observability_api.domain.models import ObsFeedEvent
from coa_observability_api.domain.toggles import TaskToggle, is_task_enabled

logger = logging.getLogger(__name__)


class BaseObsTask(ABC):
    toggle: TaskToggle
    name: str = "obs_task"

    def run(self, event: ObsFeedEvent) -> None:
        if not is_task_enabled(self.toggle):
            logger.debug(
                "task skipped (toggle off) name=%s env=%s ingest_id=%s",
                self.name,
                self.toggle.value,
                event.ingest_id,
            )
            return
        try:
            self._run(event)
        except Exception:
            logger.exception(
                "task soft-fail name=%s ingest_id=%s",
                self.name,
                event.ingest_id,
            )

    @abstractmethod
    def _run(self, event: ObsFeedEvent) -> None:
        ...
