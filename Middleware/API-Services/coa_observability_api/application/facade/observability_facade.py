"""
ObservabilityFacade — single entry for feed ingest / LLM call emit.

API → Facade → Tasks (only if OBS_TASK_* true) → SubFacades → Plugins
Never raises to callers; soft-fails per task/plugin.
"""

from __future__ import annotations

import logging
import threading
import uuid
from typing import Any, Mapping

from coa_observability_api.application.tasks.base import BaseObsTask
from coa_observability_api.application.tasks.emit_llmops_task import EmitLlmOpsTask
from coa_observability_api.application.tasks.emit_logs_task import EmitLogsTask
from coa_observability_api.application.tasks.emit_metrics_task import EmitMetricsTask
from coa_observability_api.application.tasks.emit_traces_task import EmitTracesTask
from coa_observability_api.domain.models import ObsFeedEvent

logger = logging.getLogger(__name__)

_FACADE: ObservabilityFacade | None = None
_FACADE_LOCK = threading.Lock()


class ObservabilityFacade:
    def __init__(self, tasks: list[BaseObsTask] | None = None) -> None:
        self._tasks: list[BaseObsTask] = tasks or [
            EmitMetricsTask(),
            EmitTracesTask(),
            EmitLogsTask(),
            EmitLlmOpsTask(),
        ]

    def ingest(
        self,
        *,
        session_id: str,
        ctx_data: Mapping[str, Any] | None = None,
        ingest_id: str | None = None,
    ) -> str:
        """
        Accept a feed payload and fan out asynchronously.

        Returns ingest_id immediately; background thread runs tasks.
        """
        iid = ingest_id or str(uuid.uuid4())
        ctx = dict(ctx_data or {})
        obs_raw = ctx.get("obs_data")
        obs_data = dict(obs_raw) if isinstance(obs_raw, Mapping) else {}
        event = ObsFeedEvent(
            ingest_id=iid,
            session_id=session_id,
            ctx_data=ctx,
            obs_data=obs_data,
        )
        thread = threading.Thread(
            target=self._dispatch,
            args=(event,),
            name=f"obs-fanout-{iid[:8]}",
            daemon=True,
        )
        thread.start()
        return iid

    def emit_sync(self, event: ObsFeedEvent) -> None:
        """Synchronous dispatch (used by thin helpers / tests). Soft-fail."""
        self._dispatch(event)

    def _dispatch(self, event: ObsFeedEvent) -> None:
        try:
            for task in self._tasks:
                try:
                    task.run(event)
                except Exception:
                    logger.exception(
                        "facade task soft-fail name=%s ingest_id=%s",
                        getattr(task, "name", "?"),
                        event.ingest_id,
                    )
        except Exception:
            logger.exception("facade dispatch soft-fail ingest_id=%s", event.ingest_id)


def get_observability_facade() -> ObservabilityFacade:
    global _FACADE
    if _FACADE is None:
        with _FACADE_LOCK:
            if _FACADE is None:
                _FACADE = ObservabilityFacade()
    return _FACADE
