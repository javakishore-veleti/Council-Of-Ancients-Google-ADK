from __future__ import annotations

from abc import ABC


class BaseAdminTask(ABC):
    name: str = "admin_task"
