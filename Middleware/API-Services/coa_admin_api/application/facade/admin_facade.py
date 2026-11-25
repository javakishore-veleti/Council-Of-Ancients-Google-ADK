from __future__ import annotations

from typing import Any
from uuid import UUID

from coa_admin_api.application.tasks.endpoint_crud_task import EndpointCrudTask
from coa_admin_api.application.tasks.source_ops_task import SourceOpsTask
from coa_admin_api.domain.models import AdminKnowledgeSource, AppEndpoint, WfExecLog


class AdminFacade:
    def __init__(
        self,
        endpoints: EndpointCrudTask | None = None,
        sources: SourceOpsTask | None = None,
    ) -> None:
        self._endpoints = endpoints or EndpointCrudTask()
        self._sources = sources or SourceOpsTask()

    def list_endpoints(self) -> list[AppEndpoint]:
        return self._endpoints.list()

    def get_endpoint(self, endpoint_id: UUID) -> AppEndpoint:
        return self._endpoints.get(endpoint_id)

    def list_sources(self) -> list[AdminKnowledgeSource]:
        return self._sources.list_sources()

    def get_source(self, source_id: UUID) -> AdminKnowledgeSource:
        return self._sources.get_source(source_id)

    def queue_download(self, source_id: UUID) -> tuple[WfExecLog, AdminKnowledgeSource]:
        return self._sources.queue_download(source_id)

    def list_wf_logs(self, source_id: UUID) -> list[WfExecLog]:
        return self._sources.list_wf_logs(source_id)

    def get_wf_log(self, exec_id: UUID) -> WfExecLog:
        return self._sources.get_wf_log(exec_id)

    def patch_wf_log(self, exec_id: UUID, data: dict[str, Any]) -> WfExecLog:
        return self._sources.patch_wf_log(exec_id, data)
