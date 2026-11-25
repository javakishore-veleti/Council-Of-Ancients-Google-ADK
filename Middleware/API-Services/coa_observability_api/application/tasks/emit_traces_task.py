"""OBS_TASK_EMIT_TRACES → TracesSubFacade."""

from __future__ import annotations

from coa_observability_api.application.sub_facades.traces_sub_facade import (
    TracesSubFacade,
)
from coa_observability_api.application.tasks.base import BaseObsTask
from coa_observability_api.domain.models import ObsFeedEvent
from coa_observability_api.domain.toggles import TaskToggle


class EmitTracesTask(BaseObsTask):
    toggle = TaskToggle.EMIT_TRACES
    name = "emit_traces"

    def __init__(self, sub_facade: TracesSubFacade | None = None) -> None:
        self._sub = sub_facade or TracesSubFacade()

    def _run(self, event: ObsFeedEvent) -> None:
        self._sub.emit(event)
