from __future__ import annotations

import json
from typing import Any
from uuid import UUID

from coa_admin_api.domain.errors import NotFoundError, ValidationError
from coa_admin_api.domain.models import AdminKnowledgeSource
from coa_admin_api.infrastructure.dao.db import connection

_SOURCE_SQL = """
    SELECT
      s.id,
      s.name,
      s.description,
      s.citation_name,
      s.citation_desc,
      s.url,
      s.license,
      s.status AS ingest_status,
      s.workflow_id,
      s.meta,
      s.created_at AS created_on,
      s.updated_at AS updated_on,
      sub.code AS subcategory_code,
      sub.name AS subcategory_name,
      COALESCE(parent.code, sub.code) AS category_code,
      COALESCE(parent.name, sub.name) AS category_name
    FROM knowledge.knowledge_source s
    JOIN knowledge.knowledge_category sub ON sub.id = s.category_id
    LEFT JOIN knowledge.knowledge_category parent ON parent.id = sub.parent_id
"""


def _uuid_list(values: list[Any] | None) -> list[UUID]:
    if not values:
        return []
    out: list[UUID] = []
    for v in values:
        if v is None:
            continue
        out.append(v if isinstance(v, UUID) else UUID(str(v)))
    return out


def _row(r: dict[str, Any], maps: dict[str, list[UUID]]) -> AdminKnowledgeSource:
    meta = r.get("meta") or {}
    if isinstance(meta, str):
        meta = json.loads(meta)
    return AdminKnowledgeSource(
        id=r["id"],
        name=r["name"],
        description=r.get("description"),
        citation_name=r["citation_name"],
        citation_desc=r.get("citation_desc"),
        category_name=r["category_name"],
        category_code=r["category_code"],
        subcategory_name=r["subcategory_name"],
        subcategory_code=r["subcategory_code"],
        url=r.get("url"),
        license=r.get("license"),
        ingest_status=r["ingest_status"],
        created_on=r.get("created_on"),
        updated_on=r.get("updated_on"),
        download_from_endpoint_id=(maps.get("download_from") or [None])[0],
        store_to_endpoint_ids=maps.get("store_to") or [],
        tech_stack_endpoint_ids=maps.get("tech_stack") or [],
        workflow_id=r.get("workflow_id"),
        meta=meta,
    )


class AdminSourceDao:
    def _maps_for(self, conn: Any, source_ids: list[UUID]) -> dict[UUID, dict[str, list[UUID]]]:
        if not source_ids:
            return {}
        rows = conn.execute(
            """
            SELECT source_id, endpoint_id, role
            FROM knowledge.knowledge_source_endpoint
            WHERE source_id = ANY(%s)
            ORDER BY created_at
            """,
            (source_ids,),
        ).fetchall()
        out: dict[UUID, dict[str, list[UUID]]] = {}
        for r in rows:
            sid = r["source_id"]
            bucket = out.setdefault(sid, {"download_from": [], "store_to": [], "tech_stack": []})
            role = r["role"]
            if role in bucket:
                bucket[role].append(r["endpoint_id"])
        return out

    def list(self) -> list[AdminKnowledgeSource]:
        with connection() as conn:
            rows = conn.execute(f"{_SOURCE_SQL} ORDER BY s.name").fetchall()
            maps = self._maps_for(conn, [r["id"] for r in rows])
        return [_row(r, maps.get(r["id"], {})) for r in rows]

    def get(self, source_id: UUID) -> AdminKnowledgeSource:
        with connection() as conn:
            row = conn.execute(f"{_SOURCE_SQL} WHERE s.id = %s", (source_id,)).fetchone()
            if not row:
                raise NotFoundError(f"source {source_id} not found")
            maps = self._maps_for(conn, [source_id])
        return _row(row, maps.get(source_id, {}))

    def set_status(self, source_id: UUID, status: str) -> None:
        with connection() as conn:
            cur = conn.execute(
                """
                UPDATE knowledge.knowledge_source
                SET status = %s, updated_at = NOW()
                WHERE id = %s
                """,
                (status, source_id),
            )
            if cur.rowcount == 0:
                raise NotFoundError(f"source {source_id} not found")

    def endpoint_ids_by_role(self, source_id: UUID) -> dict[str, list[UUID]]:
        with connection() as conn:
            maps = self._maps_for(conn, [source_id])
        return maps.get(source_id, {"download_from": [], "store_to": [], "tech_stack": []})

    def require_store_targets(self, source_id: UUID) -> dict[str, list[UUID]]:
        maps = self.endpoint_ids_by_role(source_id)
        if not maps.get("store_to"):
            raise ValidationError("no_store_targets")
        return maps
