from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException, Query

from coa_knowledge_api.application.facade.knowledge_facade import KnowledgeFacade
from coa_knowledge_api.domain.errors import ConflictError, NotFoundError, ValidationError
from coa_knowledge_api.presentation.schemas.knowledge import (
    CategoryCreate,
    CategoryOut,
    CategoryUpdate,
)

router = APIRouter(prefix="/v1/knowledge/categories", tags=["categories"])
facade = KnowledgeFacade()


def _map(exc: Exception) -> HTTPException:
    if isinstance(exc, NotFoundError):
        return HTTPException(status_code=404, detail=str(exc))
    if isinstance(exc, ConflictError):
        return HTTPException(status_code=409, detail=str(exc))
    if isinstance(exc, ValidationError):
        return HTTPException(status_code=400, detail=str(exc))
    raise exc


@router.get("", response_model=list[CategoryOut], operation_id="list_knowledge_categories")
def list_categories(
    parent_id: UUID | None = None,
    roots_only: bool = Query(False, description="Top-nav topics only (parent_id IS NULL)"),
    include_inactive: bool = False,
) -> list[CategoryOut]:
    rows = facade.list_categories(
        parent_id=parent_id,
        roots_only=roots_only,
        include_inactive=include_inactive,
    )
    return [CategoryOut.model_validate(r, from_attributes=True) for r in rows]


@router.get("/by-code/{code}", response_model=CategoryOut, operation_id="get_knowledge_category_by_code")
def get_by_code(code: str) -> CategoryOut:
    try:
        return CategoryOut.model_validate(facade.get_category_by_code(code), from_attributes=True)
    except Exception as exc:
        raise _map(exc) from exc


@router.get("/{category_id}", response_model=CategoryOut, operation_id="get_knowledge_category")
def get_category(category_id: UUID) -> CategoryOut:
    try:
        return CategoryOut.model_validate(facade.get_category(category_id), from_attributes=True)
    except Exception as exc:
        raise _map(exc) from exc


@router.post("", response_model=CategoryOut, status_code=201, operation_id="create_knowledge_category")
def create_category(body: CategoryCreate) -> CategoryOut:
    try:
        return CategoryOut.model_validate(
            facade.create_category(body.model_dump()),
            from_attributes=True,
        )
    except Exception as exc:
        raise _map(exc) from exc


@router.patch("/{category_id}", response_model=CategoryOut, operation_id="update_knowledge_category")
def update_category(category_id: UUID, body: CategoryUpdate) -> CategoryOut:
    try:
        return CategoryOut.model_validate(
            facade.update_category(category_id, body.model_dump(exclude_unset=True)),
            from_attributes=True,
        )
    except Exception as exc:
        raise _map(exc) from exc


@router.delete("/{category_id}", status_code=204, operation_id="delete_knowledge_category")
def delete_category(category_id: UUID) -> None:
    try:
        facade.delete_category(category_id)
    except Exception as exc:
        raise _map(exc) from exc
