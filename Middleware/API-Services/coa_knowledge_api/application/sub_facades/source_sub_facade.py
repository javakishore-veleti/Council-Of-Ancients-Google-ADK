"""Source sub-facade → SourceDao."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from coa_knowledge_api.domain.models import KnowledgeSource
from coa_knowledge_api.infrastructure.dao.source_dao import SourceDao


class SourceSubFacade:
    def __init__(self, dao: SourceDao | None = None) -> None:
        self._dao = dao or SourceDao()

    def list(
        self,
        *,
        category_id: UUID | None = None,
        status: str | None = None,
        q: str | None = None,
    ) -> list[KnowledgeSource]:
        return self._dao.list(category_id=category_id, status=status, q=q)

    def get(self, source_id: UUID) -> KnowledgeSource:
        return self._dao.get(source_id)

    def get_by_name(self, name: str) -> KnowledgeSource:
        return self._dao.get_by_name(name)

    def create(self, **kwargs: Any) -> KnowledgeSource:
        return self._dao.create(**kwargs)

    def update(self, source_id: UUID, patch: dict[str, Any]) -> KnowledgeSource:
        return self._dao.update(source_id, patch)

    def delete(self, source_id: UUID) -> None:
        self._dao.delete(source_id)
