"""Source CRUD task → SourceSubFacade (+ category lookup via CategorySubFacade)."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from coa_knowledge_api.application.sub_facades.category_sub_facade import CategorySubFacade
from coa_knowledge_api.application.sub_facades.source_sub_facade import SourceSubFacade
from coa_knowledge_api.application.tasks.base import BaseKnowledgeTask
from coa_knowledge_api.domain.errors import ValidationError
from coa_knowledge_api.domain.models import KnowledgeSource


class SourceCrudTask(BaseKnowledgeTask):
    name = "source_crud"

    def __init__(
        self,
        sub_facade: SourceSubFacade | None = None,
        categories: CategorySubFacade | None = None,
    ) -> None:
        self._sub = sub_facade or SourceSubFacade()
        self._categories = categories or CategorySubFacade()

    def list(
        self,
        *,
        category_id: UUID | None = None,
        category_code: str | None = None,
        status: str | None = None,
        q: str | None = None,
    ) -> list[KnowledgeSource]:
        resolved = category_id
        if category_code and not resolved:
            resolved = self._categories.get_by_code(category_code).id
        return self._sub.list(category_id=resolved, status=status, q=q)

    def get(self, source_id: UUID) -> KnowledgeSource:
        return self._sub.get(source_id)

    def get_by_name(self, name: str) -> KnowledgeSource:
        return self._sub.get_by_name(name)

    def create(self, data: dict[str, Any]) -> KnowledgeSource:
        name = (data.get("name") or "").strip()
        source_key = (data.get("source_key") or "").strip()
        citation_name = (data.get("citation_name") or name).strip()
        category_id = data.get("category_id")
        if not name or not source_key or not category_id:
            raise ValidationError("name, source_key, and category_id are required")
        self._categories.get(category_id)
        status = (data.get("status") or "active").strip()
        if status not in {"active", "paused", "denied", "archived"}:
            raise ValidationError(f"invalid status={status}")
        return self._sub.create(
            category_id=category_id,
            name=name,
            description=data.get("description"),
            citation_name=citation_name,
            citation_desc=data.get("citation_desc"),
            source_key=source_key,
            url=data.get("url"),
            license=data.get("license"),
            status=status,
            meta=data.get("meta") or {},
        )

    def update(self, source_id: UUID, data: dict[str, Any]) -> KnowledgeSource:
        if "category_id" in data and data["category_id"]:
            self._categories.get(data["category_id"])
        if "status" in data and data["status"] not in {
            "active",
            "paused",
            "denied",
            "archived",
            None,
        }:
            raise ValidationError(f"invalid status={data['status']}")
        return self._sub.update(source_id, data)

    def delete(self, source_id: UUID) -> None:
        self._sub.delete(source_id)
