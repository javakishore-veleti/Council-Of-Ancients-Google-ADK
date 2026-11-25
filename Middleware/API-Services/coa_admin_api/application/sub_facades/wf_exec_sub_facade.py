from __future__ import annotations

from typing import Any
from uuid import UUID

from coa_admin_api.domain.models import WfExecLog
from coa_admin_api.infrastructure.dao.wf_exec_dao import WfExecDao


class WfExecSubFacade:
    def __init__(self, dao: WfExecDao | None = None) -> None:
        self._dao = dao or WfExecDao()

    def list_for_source(self, source_id: UUID) -> list[WfExecLog]:
        return self._dao.list_for_source(source_id)

    def get(self, exec_id: UUID) -> WfExecLog:
        return self._dao.get(exec_id)

    def create_queued(
        self,
        *,
        source_id: UUID,
        wf_id: UUID,
        engine: str,
        download_from_endpoint_id: UUID | None,
        store_to_endpoint_ids: list[UUID],
        tech_stack_endpoint_ids: list[UUID],
        exec_config_json: dict[str, Any] | None = None,
    ) -> WfExecLog:
        return self._dao.create_queued(
            source_id=source_id,
            wf_id=wf_id,
            engine=engine,
            download_from_endpoint_id=download_from_endpoint_id,
            store_to_endpoint_ids=store_to_endpoint_ids,
            tech_stack_endpoint_ids=tech_stack_endpoint_ids,
            exec_config_json=exec_config_json,
        )

    def patch(self, exec_id: UUID, **kwargs) -> WfExecLog:
        return self._dao.patch(exec_id, **kwargs)
