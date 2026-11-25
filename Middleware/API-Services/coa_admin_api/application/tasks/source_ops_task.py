from __future__ import annotations

from uuid import UUID

from coa_admin_api.application.sub_facades.source_sub_facade import SourceSubFacade
from coa_admin_api.application.sub_facades.wf_exec_sub_facade import WfExecSubFacade
from coa_admin_api.application.tasks.base import BaseAdminTask
from coa_admin_api.domain.models import AdminKnowledgeSource, WfExecLog


class SourceOpsTask(BaseAdminTask):
    name = "source_ops"

    def __init__(
        self,
        sources: SourceSubFacade | None = None,
        wf: WfExecSubFacade | None = None,
    ) -> None:
        self._sources = sources or SourceSubFacade()
        self._wf = wf or WfExecSubFacade()

    def list_sources(self) -> list[AdminKnowledgeSource]:
        return self._sources.list()

    def get_source(self, source_id: UUID) -> AdminKnowledgeSource:
        return self._sources.get(source_id)

    def queue_download(self, source_id: UUID) -> tuple[WfExecLog, AdminKnowledgeSource]:
        # Ensure source exists
        self._sources.get(source_id)
        maps = self._sources.require_store_targets(source_id)
        download_from = (maps.get("download_from") or [None])[0]
        log = self._wf.create_queued(
            source_id=source_id,
            download_from_endpoint_id=download_from,
            store_to_endpoint_ids=list(maps.get("store_to") or []),
            tech_stack_endpoint_ids=list(maps.get("tech_stack") or []),
        )
        self._sources.set_status(source_id, "queued")
        # DAG / Step Functions trigger is stubbed — callbacks PATCH /v1/wf-exec-logs/{id}
        src = self._sources.get(source_id)
        return log, src

    def list_wf_logs(self, source_id: UUID) -> list[WfExecLog]:
        self._sources.get(source_id)
        return self._wf.list_for_source(source_id)

    def get_wf_log(self, exec_id: UUID) -> WfExecLog:
        return self._wf.get(exec_id)

    def patch_wf_log(self, exec_id: UUID, data: dict) -> WfExecLog:
        status = data.get("status")
        mark_started = status in {"started", "running"}
        mark_finished = status in {"completed", "failed", "cancelled"}
        return self._wf.patch(
            exec_id,
            status=status,
            external_run_id=data.get("external_run_id"),
            error_message=data.get("error_message"),
            detail=data.get("detail"),
            mark_started=mark_started,
            mark_finished=mark_finished,
        )
