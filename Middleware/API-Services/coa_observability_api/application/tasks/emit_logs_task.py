"""OBS_TASK_EMIT_LOGS → LogsSubFacade."""

from __future__ import annotations

from coa_observability_api.application.sub_facades.logs_sub_facade import LogsSubFacade
from coa_observability_api.application.tasks.base import BaseObsTask
from coa_observability_api.domain.models import ObsFeedEvent
from coa_observability_api.domain.toggles import TaskToggle


class EmitLogsTask(BaseObsTask):
    toggle = TaskToggle.EMIT_LOGS
    name = "emit_logs"

    def __init__(self, sub_facade: LogsSubFacade | None = None) -> None:
        self._sub = sub_facade or LogsSubFacade()

    def _run(self, event: ObsFeedEvent) -> None:
        self._sub.emit(event)
