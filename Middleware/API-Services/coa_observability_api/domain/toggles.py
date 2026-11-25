"""Feature toggles for observability fan-out tasks (default OFF)."""

from __future__ import annotations

import os
from enum import Enum


def _env_truthy(value: str | None) -> bool:
    if value is None:
        return False
    return value.strip().lower() in {"1", "true", "yes", "on"}


class TaskToggle(str, Enum):
    EMIT_METRICS = "OBS_TASK_EMIT_METRICS"
    EMIT_TRACES = "OBS_TASK_EMIT_TRACES"
    EMIT_LOGS = "OBS_TASK_EMIT_LOGS"
    EMIT_LLMOPS = "OBS_TASK_EMIT_LLMOPS"


def is_task_enabled(toggle: TaskToggle | str) -> bool:
    """Return True only when the corresponding .env flag is explicitly true."""
    key = toggle.value if isinstance(toggle, TaskToggle) else str(toggle)
    return _env_truthy(os.getenv(key, "false"))
