"""Category sub-facade → CategoryDao."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from coa_knowledge_api.domain.models import KnowledgeCategory
from coa_knowledge_api.infrastructure.dao.category_dao import CategoryDao


class CategorySubFacade:
    def __init__(self, dao: CategoryDao | None = None) -> None:
        self._dao = dao or CategoryDao()

    def list(
        self,
        *,
        parent_id: UUID | None = None,
        roots_only: bool = False,
        include_inactive: bool = False,
    ) -> list[KnowledgeCategory]:
        return self._dao.list(
            parent_id=parent_id,
            roots_only=roots_only,
            include_inactive=include_inactive,
        )

    def get(self, category_id: UUID) -> KnowledgeCategory:
        return self._dao.get(category_id)

    def get_by_code(self, code: str) -> KnowledgeCategory:
        return self._dao.get_by_code(code)

    def create(self, **kwargs: Any) -> KnowledgeCategory:
        return self._dao.create(**kwargs)

    def update(self, category_id: UUID, **kwargs: Any) -> KnowledgeCategory:
        return self._dao.update(category_id, **kwargs)

    def delete(self, category_id: UUID) -> None:
        self._dao.delete(category_id)
