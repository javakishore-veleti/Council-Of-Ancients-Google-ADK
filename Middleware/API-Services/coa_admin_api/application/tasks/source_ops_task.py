from __future__ import annotations

from typing import Any
from uuid import UUID

from coa_admin_api.application.sub_facades.endpoint_sub_facade import EndpointSubFacade
from coa_admin_api.application.sub_facades.source_sub_facade import SourceSubFacade
from coa_admin_api.application.sub_facades.wf_exec_sub_facade import WfExecSubFacade
from coa_admin_api.application.sub_facades.workflow_sub_facade import WorkflowSubFacade
from coa_admin_api.application.tasks.base import BaseAdminTask
from coa_admin_api.domain.errors import ValidationError
from coa_admin_api.domain.models import AdminKnowledgeSource, AppEndpoint, WfExecLog

DEFAULT_FACADE_WORKFLOW = "kb_ingest_facade"


def _endpoint_snapshot(ep: AppEndpoint) -> dict[str, Any]:
    return {
        "id": str(ep.id),
        "name": ep.name,
        "kind": ep.kind,
        "provider": ep.provider,
        "endpoint_url": ep.endpoint_url,
        "resource": ep.resource,
        "region": ep.region,
        "status": ep.status,
        "notes": ep.notes,
    }


class SourceOpsTask(BaseAdminTask):
    name = "source_ops"

    def __init__(
        self,
        sources: SourceSubFacade | None = None,
        wf: WfExecSubFacade | None = None,
        workflows: WorkflowSubFacade | None = None,
        endpoints: EndpointSubFacade | None = None,
    ) -> None:
        self._sources = sources or SourceSubFacade()
        self._wf = wf or WfExecSubFacade()
        self._workflows = workflows or WorkflowSubFacade()
        self._endpoints = endpoints or EndpointSubFacade()

    def list_sources(self) -> list[AdminKnowledgeSource]:
        return self._sources.list()

    def get_source(self, source_id: UUID) -> AdminKnowledgeSource:
        return self._sources.get(source_id)

    def queue_download(self, source_id: UUID) -> tuple[WfExecLog, AdminKnowledgeSource]:
        src = self._sources.get(source_id)
        maps = self._sources.require_store_targets(source_id)
        download_from = (maps.get("download_from") or [None])[0]

        if src.workflow_id:
            workflow = self._workflows.get(src.workflow_id)
        else:
            workflow = self._workflows.get_by_name(DEFAULT_FACADE_WORKFLOW)

        if workflow.status != "active":
            raise ValidationError(f"workflow_not_active:{workflow.name}")

        # Exec log records only endpoints this ingest run actually uses:
        # active object_store targets. Indexing (tech_stack) is a later step.
        by_id = {e.id: e for e in self._endpoints.list()}
        store_to = [
            eid
            for eid in (maps.get("store_to") or [])
            if (ep := by_id.get(eid)) is not None
            and ep.status == "active"
            and ep.kind == "object_store"
        ]
        if not store_to:
            raise ValidationError("no_active_store_targets")

        from_eps = []
        if download_from and download_from in by_id:
            from_eps.append(_endpoint_snapshot(by_id[download_from]))
        to_eps = [_endpoint_snapshot(by_id[eid]) for eid in store_to if eid in by_id]

        exec_config_json: dict[str, Any] = {
            "inputs": [
                {"key": "source_id", "value": str(source_id)},
                {"key": "source_name", "value": src.name},
                {"key": "url", "value": src.url or ""},
                {"key": "license", "value": src.license or ""},
                {"key": "workflow_id", "value": str(workflow.id)},
                {"key": "workflow_name", "value": workflow.name},
                {"key": "engine", "value": workflow.engine},
            ],
            "from_endpoints": from_eps,
            "to_endpoints": to_eps,
        }

        log = self._wf.create_queued(
            source_id=source_id,
            wf_id=workflow.id,
            engine=workflow.engine,
            download_from_endpoint_id=download_from,
            store_to_endpoint_ids=store_to,
            tech_stack_endpoint_ids=[],
            exec_config_json=exec_config_json,
        )
        self._sources.set_status(source_id, "queued")
        return log, self._sources.get(source_id)

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
