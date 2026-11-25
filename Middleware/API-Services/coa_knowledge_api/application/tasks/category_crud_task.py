"""Category CRUD task → CategorySubFacade."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from coa_knowledge_api.application.sub_facades.category_sub_facade import CategorySubFacade
from coa_knowledge_api.application.tasks.base import BaseKnowledgeTask
from coa_knowledge_api.domain.errors import ValidationError
from coa_knowledge_api.domain.models import KnowledgeCategory


class CategoryCrudTask(BaseKnowledgeTask):
    name = "category_crud"

    def __init__(self, sub_facade: CategorySubFacade | None = None) -> None:
        self._sub = sub_facade or CategorySubFacade()

    def list(
        self,
        *,
        parent_id: UUID | None = None,
        roots_only: bool = False,
        include_inactive: bool = False,
    ) -> list[KnowledgeCategory]:
        return self._sub.list(
            parent_id=parent_id,
            roots_only=roots_only,
            include_inactive=include_inactive,
        )

    def get(self, category_id: UUID) -> KnowledgeCategory:
        return self._sub.get(category_id)

    def get_by_code(self, code: str) -> KnowledgeCategory:
        return self._sub.get_by_code(code)

    def create(self, data: dict[str, Any]) -> KnowledgeCategory:
        code = (data.get("code") or "").strip()
        name = (data.get("name") or "").strip()
        if not code or not name:
            raise ValidationError("code and name are required")
        parent_id = data.get("parent_id")
        if parent_id:
            self._sub.get(parent_id)
        return self._sub.create(
            code=code,
            name=name,
            description=data.get("description"),
            parent_id=parent_id,
            sort_order=int(data.get("sort_order") or 0),
            is_active=bool(data.get("is_active", True)),
        )

    def update(self, category_id: UUID, data: dict[str, Any]) -> KnowledgeCategory:
        set_parent = "parent_id" in data
        if set_parent and data.get("parent_id"):
            self._sub.get(data["parent_id"])
        return self._sub.update(
            category_id,
            name=data.get("name"),
            description=data.get("description"),
            parent_id=data.get("parent_id"),
            sort_order=data.get("sort_order"),
            is_active=data.get("is_active"),
            set_parent=set_parent,
        )

    def delete(self, category_id: UUID) -> None:
        self._sub.delete(category_id)
