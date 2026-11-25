from __future__ import annotations

from uuid import UUID

from coa_admin_api.domain.models import AdminKnowledgeSource
from coa_admin_api.infrastructure.dao.source_dao import AdminSourceDao


class SourceSubFacade:
    def __init__(self, dao: AdminSourceDao | None = None) -> None:
        self._dao = dao or AdminSourceDao()

    def list(self) -> list[AdminKnowledgeSource]:
        return self._dao.list()

    def get(self, source_id: UUID) -> AdminKnowledgeSource:
        return self._dao.get(source_id)

    def set_status(self, source_id: UUID, status: str) -> None:
        self._dao.set_status(source_id, status)

    def require_store_targets(self, source_id: UUID) -> dict[str, list[UUID]]:
        return self._dao.require_store_targets(source_id)
