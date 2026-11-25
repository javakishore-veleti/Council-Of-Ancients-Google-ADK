"""OBS_TASK_EMIT_LLMOPS → LlmOpsSubFacade."""

from __future__ import annotations

from coa_observability_api.application.sub_facades.llmops_sub_facade import (
    LlmOpsSubFacade,
)
from coa_observability_api.application.tasks.base import BaseObsTask
from coa_observability_api.domain.models import ObsFeedEvent
from coa_observability_api.domain.toggles import TaskToggle


class EmitLlmOpsTask(BaseObsTask):
    toggle = TaskToggle.EMIT_LLMOPS
    name = "emit_llmops"

    def __init__(self, sub_facade: LlmOpsSubFacade | None = None) -> None:
        self._sub = sub_facade or LlmOpsSubFacade()

    def _run(self, event: ObsFeedEvent) -> None:
        self._sub.emit(event)
