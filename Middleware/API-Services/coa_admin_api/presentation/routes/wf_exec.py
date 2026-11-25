from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException

from coa_admin_api.application.facade import AdminFacade
from coa_admin_api.domain.errors import NotFoundError
from coa_admin_api.presentation.schemas.admin import WfExecLogOut, WfExecLogPatch

router = APIRouter(prefix="/v1/wf-exec-logs", tags=["wf-exec-logs"])
facade = AdminFacade()


@router.get("/{exec_id}", response_model=WfExecLogOut, operation_id="admin_get_wf_exec_log")
def get_wf_exec_log(exec_id: UUID) -> WfExecLogOut:
    try:
        return WfExecLogOut.model_validate(facade.get_wf_log(exec_id), from_attributes=True)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.patch("/{exec_id}", response_model=WfExecLogOut, operation_id="admin_patch_wf_exec_log")
def patch_wf_exec_log(exec_id: UUID, body: WfExecLogPatch) -> WfExecLogOut:
    try:
        row = facade.patch_wf_log(exec_id, body.model_dump(exclude_unset=True))
        return WfExecLogOut.model_validate(row, from_attributes=True)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
