from __future__ import annotations

import json
from typing import Any
from uuid import UUID

from coa_knowledge_api.domain.errors import ConflictError, NotFoundError
from coa_knowledge_api.domain.models import KnowledgeSource
from coa_knowledge_api.infrastructure.dao.db import connection


def _row(r: dict[str, Any]) -> KnowledgeSource:
    meta = r.get("meta") or {}
    if isinstance(meta, str):
        meta = json.loads(meta)
    return KnowledgeSource(
        id=r["id"],
        category_id=r["category_id"],
        name=r["name"],
        description=r.get("description"),
        citation_name=r["citation_name"],
        citation_desc=r.get("citation_desc"),
        source_key=r["source_key"],
        url=r.get("url"),
        license=r.get("license"),
        status=r["status"],
        meta=meta,
        created_at=r.get("created_at"),
        updated_at=r.get("updated_at"),
    )


_SELECT = """
    SELECT id, category_id, name, description, citation_name, citation_desc,
           source_key, url, license, status, meta, created_at, updated_at
    FROM knowledge.knowledge_source
"""


class SourceDao:
    def list(
        self,
        *,
        category_id: UUID | None = None,
        status: str | None = None,
        q: str | None = None,
    ) -> list[KnowledgeSource]:
        clauses = ["TRUE"]
        params: list[Any] = []
        if category_id is not None:
            clauses.append("category_id = %s")
            params.append(category_id)
        if status:
            clauses.append("status = %s")
            params.append(status)
        if q:
            clauses.append(
                "(name ILIKE %s OR citation_name ILIKE %s OR source_key ILIKE %s)"
            )
            like = f"%{q}%"
            params.extend([like, like, like])
        sql = f"{_SELECT} WHERE {' AND '.join(clauses)} ORDER BY name"
        with connection() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [_row(r) for r in rows]

    def get(self, source_id: UUID) -> KnowledgeSource:
        with connection() as conn:
            row = conn.execute(
                f"{_SELECT} WHERE id = %s",
                (source_id,),
            ).fetchone()
        if not row:
            raise NotFoundError(f"source {source_id} not found")
        return _row(row)

    def get_by_name(self, name: str) -> KnowledgeSource:
        with connection() as conn:
            row = conn.execute(
                f"{_SELECT} WHERE name = %s",
                (name,),
            ).fetchone()
        if not row:
            raise NotFoundError(f"source name={name} not found")
        return _row(row)

    def create(
        self,
        *,
        category_id: UUID,
        name: str,
        description: str | None,
        citation_name: str,
        citation_desc: str | None,
        source_key: str,
        url: str | None,
        license: str | None,
        status: str,
        meta: dict[str, Any],
    ) -> KnowledgeSource:
        try:
            with connection() as conn:
                row = conn.execute(
                    """
                    INSERT INTO knowledge.knowledge_source
                      (category_id, name, description, citation_name, citation_desc,
                       source_key, url, license, status, meta)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb)
                    RETURNING id, category_id, name, description, citation_name, citation_desc,
                              source_key, url, license, status, meta, created_at, updated_at
                    """,
                    (
                        category_id,
                        name,
                        description,
                        citation_name,
                        citation_desc,
                        source_key,
                        url,
                        license,
                        status,
                        json.dumps(meta),
                    ),
                ).fetchone()
        except Exception as exc:
            msg = str(exc).lower()
            if "unique" in msg or "duplicate" in msg:
                raise ConflictError(
                    f"source_key or name conflict for source_key={source_key}"
                ) from exc
            raise
        return _row(row)

    def update(
        self,
        source_id: UUID,
        patch: dict[str, Any],
    ) -> KnowledgeSource:
        current = self.get(source_id)
        data = {
            "category_id": patch.get("category_id", current.category_id),
            "name": patch.get("name", current.name),
            "description": patch.get("description", current.description),
            "citation_name": patch.get("citation_name", current.citation_name),
            "citation_desc": patch.get("citation_desc", current.citation_desc),
            "url": patch.get("url", current.url),
            "license": patch.get("license", current.license),
            "status": patch.get("status", current.status),
            "meta": patch.get("meta", current.meta),
        }
        with connection() as conn:
            row = conn.execute(
                """
                UPDATE knowledge.knowledge_source
                SET category_id = %s,
                    name = %s,
                    description = %s,
                    citation_name = %s,
                    citation_desc = %s,
                    url = %s,
                    license = %s,
                    status = %s,
                    meta = %s::jsonb,
                    updated_at = NOW()
                WHERE id = %s
                RETURNING id, category_id, name, description, citation_name, citation_desc,
                          source_key, url, license, status, meta, created_at, updated_at
                """,
                (
                    data["category_id"],
                    data["name"],
                    data["description"],
                    data["citation_name"],
                    data["citation_desc"],
                    data["url"],
                    data["license"],
                    data["status"],
                    json.dumps(data["meta"]),
                    source_id,
                ),
            ).fetchone()
        return _row(row)

    def delete(self, source_id: UUID) -> None:
        self.get(source_id)
        with connection() as conn:
            conn.execute(
                "DELETE FROM knowledge.knowledge_source WHERE id = %s",
                (source_id,),
            )
