"""OBS_TASK_EMIT_METRICS → MetricsSubFacade."""

from __future__ import annotations

from coa_observability_api.application.sub_facades.metrics_sub_facade import (
    MetricsSubFacade,
)
from coa_observability_api.application.tasks.base import BaseObsTask
from coa_observability_api.domain.models import ObsFeedEvent
from coa_observability_api.domain.toggles import TaskToggle


class EmitMetricsTask(BaseObsTask):
    toggle = TaskToggle.EMIT_METRICS
    name = "emit_metrics"

    def __init__(self, sub_facade: MetricsSubFacade | None = None) -> None:
        self._sub = sub_facade or MetricsSubFacade()

    def _run(self, event: ObsFeedEvent) -> None:
        self._sub.emit(event)
