from __future__ import annotations

from typing import Any
from uuid import UUID

from coa_admin_api.domain.models import Workflow
from coa_admin_api.infrastructure.dao.workflow_dao import WorkflowDao


class WorkflowSubFacade:
    def __init__(self, dao: WorkflowDao | None = None) -> None:
        self._dao = dao or WorkflowDao()

    def list(self) -> list[Workflow]:
        return self._dao.list()

    def get(self, workflow_id: UUID) -> Workflow:
        return self._dao.get(workflow_id)

    def get_by_name(self, name: str) -> Workflow:
        return self._dao.get_by_name(name)

    def create(self, data: dict[str, Any]) -> Workflow:
        return self._dao.create(
            name=data["name"],
            engine=data["engine"],
            description=data.get("description"),
            external_ref=data.get("external_ref"),
            status=data.get("status") or "active",
            meta=data.get("meta"),
        )

    def update(self, workflow_id: UUID, data: dict[str, Any]) -> Workflow:
        return self._dao.update(workflow_id, data)
