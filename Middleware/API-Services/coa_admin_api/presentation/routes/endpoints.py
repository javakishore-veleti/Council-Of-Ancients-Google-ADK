from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException

from coa_admin_api.application.facade import AdminFacade
from coa_admin_api.domain.errors import NotFoundError
from coa_admin_api.presentation.schemas.admin import AppEndpointOut

router = APIRouter(prefix="/v1/app-endpoints", tags=["app-endpoints"])
facade = AdminFacade()


def _out(ep) -> AppEndpointOut:
    return AppEndpointOut(
        id=ep.id,
        name=ep.name,
        kind=ep.kind,
        provider=ep.provider,
        endpoint_url=ep.endpoint_url,
        resource=ep.resource,
        region=ep.region,
        status=ep.status,
        notes=ep.notes,
        created_on=ep.created_at,
        updated_on=ep.updated_at,
    )


@router.get("", response_model=list[AppEndpointOut], operation_id="list_app_endpoints")
def list_endpoints() -> list[AppEndpointOut]:
    return [_out(e) for e in facade.list_endpoints()]


@router.get("/{endpoint_id}", response_model=AppEndpointOut, operation_id="get_app_endpoint")
def get_endpoint(endpoint_id: UUID) -> AppEndpointOut:
    try:
        return _out(facade.get_endpoint(endpoint_id))
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
