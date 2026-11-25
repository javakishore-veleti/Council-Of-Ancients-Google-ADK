from __future__ import annotations

from typing import Any
from uuid import UUID

from coa_admin_api.application.sub_facades.workflow_sub_facade import WorkflowSubFacade
from coa_admin_api.application.tasks.base import BaseAdminTask
from coa_admin_api.domain.models import Workflow


class WorkflowCrudTask(BaseAdminTask):
    name = "workflow_crud"

    def __init__(self, sub: WorkflowSubFacade | None = None) -> None:
        self._sub = sub or WorkflowSubFacade()

    def list(self) -> list[Workflow]:
        return self._sub.list()

    def get(self, workflow_id: UUID) -> Workflow:
        return self._sub.get(workflow_id)

    def create(self, data: dict[str, Any]) -> Workflow:
        return self._sub.create(data)

    def update(self, workflow_id: UUID, data: dict[str, Any]) -> Workflow:
        return self._sub.update(workflow_id, data)
