"""
KnowledgeFacade — single entry for Knowledge Bank CRUD.

API → Facade → Tasks → SubFacades → DAO
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from coa_knowledge_api.application.tasks.category_crud_task import CategoryCrudTask
from coa_knowledge_api.application.tasks.source_crud_task import SourceCrudTask
from coa_knowledge_api.domain.models import KnowledgeCategory, KnowledgeSource


class KnowledgeFacade:
    def __init__(
        self,
        category_task: CategoryCrudTask | None = None,
        source_task: SourceCrudTask | None = None,
    ) -> None:
        self._categories = category_task or CategoryCrudTask()
        self._sources = source_task or SourceCrudTask()

    # --- categories ---

    def list_categories(
        self,
        *,
        parent_id: UUID | None = None,
        roots_only: bool = False,
        include_inactive: bool = False,
    ) -> list[KnowledgeCategory]:
        return self._categories.list(
            parent_id=parent_id,
            roots_only=roots_only,
            include_inactive=include_inactive,
        )

    def get_category(self, category_id: UUID) -> KnowledgeCategory:
        return self._categories.get(category_id)

    def get_category_by_code(self, code: str) -> KnowledgeCategory:
        return self._categories.get_by_code(code)

    def create_category(self, data: dict[str, Any]) -> KnowledgeCategory:
        return self._categories.create(data)

    def update_category(self, category_id: UUID, data: dict[str, Any]) -> KnowledgeCategory:
        return self._categories.update(category_id, data)

    def delete_category(self, category_id: UUID) -> None:
        self._categories.delete(category_id)

    # --- sources ---

    def list_sources(
        self,
        *,
        category_id: UUID | None = None,
        category_code: str | None = None,
        status: str | None = None,
        q: str | None = None,
    ) -> list[KnowledgeSource]:
        return self._sources.list(
            category_id=category_id,
            category_code=category_code,
            status=status,
            q=q,
        )

    def get_source(self, source_id: UUID) -> KnowledgeSource:
        return self._sources.get(source_id)

    def get_source_by_name(self, name: str) -> KnowledgeSource:
        return self._sources.get_by_name(name)

    def create_source(self, data: dict[str, Any]) -> KnowledgeSource:
        return self._sources.create(data)

    def update_source(self, source_id: UUID, data: dict[str, Any]) -> KnowledgeSource:
        return self._sources.update(source_id, data)

    def delete_source(self, source_id: UUID) -> None:
        self._sources.delete(source_id)
