from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException

from coa_admin_api.application.facade import AdminFacade
from coa_admin_api.domain.errors import NotFoundError, ValidationError
from coa_admin_api.presentation.schemas.admin import WorkflowCreate, WorkflowOut, WorkflowPatch

router = APIRouter(prefix="/v1/workflows", tags=["workflows"])
facade = AdminFacade()


@router.get("", response_model=list[WorkflowOut], operation_id="list_workflows")
def list_workflows() -> list[WorkflowOut]:
    return [WorkflowOut.model_validate(w, from_attributes=True) for w in facade.list_workflows()]


@router.get("/{workflow_id}", response_model=WorkflowOut, operation_id="get_workflow")
def get_workflow(workflow_id: UUID) -> WorkflowOut:
    try:
        return WorkflowOut.model_validate(facade.get_workflow(workflow_id), from_attributes=True)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.post("", response_model=WorkflowOut, operation_id="create_workflow", status_code=201)
def create_workflow(body: WorkflowCreate) -> WorkflowOut:
    try:
        row = facade.create_workflow(body.model_dump())
        return WorkflowOut.model_validate(row, from_attributes=True)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.patch("/{workflow_id}", response_model=WorkflowOut, operation_id="patch_workflow")
def patch_workflow(workflow_id: UUID, body: WorkflowPatch) -> WorkflowOut:
    try:
        row = facade.update_workflow(workflow_id, body.model_dump(exclude_unset=True))
        return WorkflowOut.model_validate(row, from_attributes=True)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
