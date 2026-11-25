from __future__ import annotations

from typing import Any
from uuid import UUID

from coa_knowledge_api.domain.errors import ConflictError, NotFoundError
from coa_knowledge_api.domain.models import KnowledgeCategory
from coa_knowledge_api.infrastructure.dao.db import connection


def _row(r: dict[str, Any]) -> KnowledgeCategory:
    return KnowledgeCategory(**r)


class CategoryDao:
    def list(
        self,
        *,
        parent_id: UUID | None = None,
        roots_only: bool = False,
        include_inactive: bool = False,
    ) -> list[KnowledgeCategory]:
        clauses = ["TRUE"]
        params: list[Any] = []
        if roots_only:
            clauses.append("parent_id IS NULL")
        elif parent_id is not None:
            clauses.append("parent_id = %s")
            params.append(parent_id)
        if not include_inactive:
            clauses.append("is_active = TRUE")
        sql = f"""
            SELECT id, code, name, description, parent_id, sort_order, is_active,
                   created_at, updated_at
            FROM knowledge.knowledge_category
            WHERE {' AND '.join(clauses)}
            ORDER BY sort_order, name
        """
        with connection() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [_row(r) for r in rows]

    def get(self, category_id: UUID) -> KnowledgeCategory:
        with connection() as conn:
            row = conn.execute(
                """
                SELECT id, code, name, description, parent_id, sort_order, is_active,
                       created_at, updated_at
                FROM knowledge.knowledge_category WHERE id = %s
                """,
                (category_id,),
            ).fetchone()
        if not row:
            raise NotFoundError(f"category {category_id} not found")
        return _row(row)

    def get_by_code(self, code: str) -> KnowledgeCategory:
        with connection() as conn:
            row = conn.execute(
                """
                SELECT id, code, name, description, parent_id, sort_order, is_active,
                       created_at, updated_at
                FROM knowledge.knowledge_category WHERE code = %s
                """,
                (code,),
            ).fetchone()
        if not row:
            raise NotFoundError(f"category code={code} not found")
        return _row(row)

    def create(
        self,
        *,
        code: str,
        name: str,
        description: str | None,
        parent_id: UUID | None,
        sort_order: int,
        is_active: bool,
    ) -> KnowledgeCategory:
        try:
            with connection() as conn:
                row = conn.execute(
                    """
                    INSERT INTO knowledge.knowledge_category
                      (code, name, description, parent_id, sort_order, is_active)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id, code, name, description, parent_id, sort_order, is_active,
                              created_at, updated_at
                    """,
                    (code, name, description, parent_id, sort_order, is_active),
                ).fetchone()
        except Exception as exc:
            if "unique" in str(exc).lower() or "duplicate" in str(exc).lower():
                raise ConflictError(f"category code={code} already exists") from exc
            raise
        return _row(row)

    def update(
        self,
        category_id: UUID,
        *,
        name: str | None = None,
        description: str | None = None,
        parent_id: UUID | None = None,
        sort_order: int | None = None,
        is_active: bool | None = None,
        set_parent: bool = False,
    ) -> KnowledgeCategory:
        current = self.get(category_id)
        next_name = name if name is not None else current.name
        next_desc = description if description is not None else current.description
        next_parent = parent_id if set_parent else current.parent_id
        next_sort = sort_order if sort_order is not None else current.sort_order
        next_active = is_active if is_active is not None else current.is_active
        with connection() as conn:
            row = conn.execute(
                """
                UPDATE knowledge.knowledge_category
                SET name = %s,
                    description = %s,
                    parent_id = %s,
                    sort_order = %s,
                    is_active = %s,
                    updated_at = NOW()
                WHERE id = %s
                RETURNING id, code, name, description, parent_id, sort_order, is_active,
                          created_at, updated_at
                """,
                (next_name, next_desc, next_parent, next_sort, next_active, category_id),
            ).fetchone()
        return _row(row)

    def delete(self, category_id: UUID) -> None:
        self.get(category_id)
        with connection() as conn:
            conn.execute(
                "DELETE FROM knowledge.knowledge_category WHERE id = %s",
                (category_id,),
            )
