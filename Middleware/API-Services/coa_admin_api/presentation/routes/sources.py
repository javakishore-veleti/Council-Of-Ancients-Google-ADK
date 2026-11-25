from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException

from coa_admin_api.application.facade import AdminFacade
from coa_admin_api.domain.errors import NotFoundError, ValidationError
from coa_admin_api.domain.models import AdminKnowledgeSource, WfExecLog
from coa_admin_api.presentation.schemas.admin import (
    AdminSourceOut,
    DownloadJobOut,
    WfExecLogOut,
)

router = APIRouter(prefix="/v1/knowledge/sources", tags=["knowledge-sources"])
facade = AdminFacade()


def _source_out(s: AdminKnowledgeSource) -> AdminSourceOut:
    return AdminSourceOut.model_validate(s, from_attributes=True)


def _wf_out(w: WfExecLog) -> WfExecLogOut:
    return WfExecLogOut.model_validate(w, from_attributes=True)


@router.get("", response_model=list[AdminSourceOut], operation_id="admin_list_sources")
def list_sources() -> list[AdminSourceOut]:
    return [_source_out(s) for s in facade.list_sources()]


@router.get("/{source_id}", response_model=AdminSourceOut, operation_id="admin_get_source")
def get_source(source_id: UUID) -> AdminSourceOut:
    try:
        return _source_out(facade.get_source(source_id))
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.post(
    "/{source_id}/download",
    response_model=DownloadJobOut,
    operation_id="admin_queue_download",
)
def queue_download(source_id: UUID) -> DownloadJobOut:
    try:
        log, _src = facade.queue_download(source_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return DownloadJobOut(
        wf_exec_log_id=log.id,
        source_id=log.source_id,
        status="queued",
        download_from_endpoint_id=log.download_from_endpoint_id,
        store_to_endpoint_ids=list(log.store_to_endpoint_ids),
    )


@router.get(
    "/{source_id}/wf-exec-logs",
    response_model=list[WfExecLogOut],
    operation_id="admin_list_source_wf_logs",
)
def list_source_wf_logs(source_id: UUID) -> list[WfExecLogOut]:
    try:
        return [_wf_out(w) for w in facade.list_wf_logs(source_id)]
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
