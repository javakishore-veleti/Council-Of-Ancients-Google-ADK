from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException, Query

from coa_knowledge_api.application.facade.knowledge_facade import KnowledgeFacade
from coa_knowledge_api.domain.errors import ConflictError, NotFoundError, ValidationError
from coa_knowledge_api.presentation.schemas.knowledge import (
    SourceCreate,
    SourceOut,
    SourceUpdate,
)

router = APIRouter(prefix="/v1/knowledge/sources", tags=["sources"])
facade = KnowledgeFacade()


def _map(exc: Exception) -> HTTPException:
    if isinstance(exc, NotFoundError):
        return HTTPException(status_code=404, detail=str(exc))
    if isinstance(exc, ConflictError):
        return HTTPException(status_code=409, detail=str(exc))
    if isinstance(exc, ValidationError):
        return HTTPException(status_code=400, detail=str(exc))
    raise exc


@router.get("", response_model=list[SourceOut], operation_id="list_knowledge_sources")
def list_sources(
    category_id: UUID | None = None,
    category_code: str | None = Query(
        None,
        description="Filter by category code (e.g. styles under Architecture)",
    ),
    status: str | None = None,
    q: str | None = Query(None, description="Search name, citation_name, or source_key"),
) -> list[SourceOut]:
    rows = facade.list_sources(
        category_id=category_id,
        category_code=category_code,
        status=status,
        q=q,
    )
    return [SourceOut.model_validate(r, from_attributes=True) for r in rows]


@router.get("/by-name/{name}", response_model=SourceOut, operation_id="get_knowledge_source_by_name")
def get_by_name(name: str) -> SourceOut:
    try:
        return SourceOut.model_validate(facade.get_source_by_name(name), from_attributes=True)
    except Exception as exc:
        raise _map(exc) from exc


@router.get("/{source_id}", response_model=SourceOut, operation_id="get_knowledge_source")
def get_source(source_id: UUID) -> SourceOut:
    try:
        return SourceOut.model_validate(facade.get_source(source_id), from_attributes=True)
    except Exception as exc:
        raise _map(exc) from exc


@router.post("", response_model=SourceOut, status_code=201, operation_id="create_knowledge_source")
def create_source(body: SourceCreate) -> SourceOut:
    try:
        return SourceOut.model_validate(
            facade.create_source(body.model_dump()),
            from_attributes=True,
        )
    except Exception as exc:
        raise _map(exc) from exc


@router.patch("/{source_id}", response_model=SourceOut, operation_id="update_knowledge_source")
def update_source(source_id: UUID, body: SourceUpdate) -> SourceOut:
    try:
        return SourceOut.model_validate(
            facade.update_source(source_id, body.model_dump(exclude_unset=True)),
            from_attributes=True,
        )
    except Exception as exc:
        raise _map(exc) from exc


@router.delete("/{source_id}", status_code=204, operation_id="delete_knowledge_source")
def delete_source(source_id: UUID) -> None:
    try:
        facade.delete_source(source_id)
    except Exception as exc:
        raise _map(exc) from exc
