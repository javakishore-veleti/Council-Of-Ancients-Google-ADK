from __future__ import annotations

import json
from typing import Any
from uuid import UUID

from coa_admin_api.domain.errors import NotFoundError, ValidationError
from coa_admin_api.domain.models import Workflow
from coa_admin_api.infrastructure.dao.db import connection

_SELECT = """
    SELECT id, name, description, engine, external_ref, status, meta,
           created_at AS created_on, updated_at AS updated_on
    FROM knowledge.workflow
"""


def _row(r: dict[str, Any]) -> Workflow:
    meta = r.get("meta") or {}
    if isinstance(meta, str):
        meta = json.loads(meta)
    return Workflow(
        id=r["id"],
        name=r["name"],
        description=r.get("description"),
        engine=r["engine"],
        external_ref=r.get("external_ref"),
        status=r["status"],
        meta=meta,
        created_on=r.get("created_on"),
        updated_on=r.get("updated_on"),
    )


class WorkflowDao:
    def list(self) -> list[Workflow]:
        with connection() as conn:
            rows = conn.execute(f"{_SELECT} ORDER BY name").fetchall()
        return [_row(r) for r in rows]

    def get(self, workflow_id: UUID) -> Workflow:
        with connection() as conn:
            row = conn.execute(f"{_SELECT} WHERE id = %s", (workflow_id,)).fetchone()
        if not row:
            raise NotFoundError(f"workflow {workflow_id} not found")
        return _row(row)

    def get_by_name(self, name: str) -> Workflow:
        with connection() as conn:
            row = conn.execute(f"{_SELECT} WHERE name = %s", (name,)).fetchone()
        if not row:
            raise NotFoundError(f"workflow {name!r} not found")
        return _row(row)

    def create(
        self,
        *,
        name: str,
        engine: str,
        description: str | None = None,
        external_ref: str | None = None,
        status: str = "active",
        meta: dict[str, Any] | None = None,
    ) -> Workflow:
        name = name.strip()
        engine = engine.strip()
        if not name:
            raise ValidationError("name_required")
        if not engine:
            raise ValidationError("engine_required")
        with connection() as conn:
            row = conn.execute(
                """
                INSERT INTO knowledge.workflow (
                  name, description, engine, external_ref, status, meta
                ) VALUES (%s, %s, %s, %s, %s, %s::jsonb)
                RETURNING id, name, description, engine, external_ref, status, meta,
                          created_at AS created_on, updated_at AS updated_on
                """,
                (
                    name,
                    description,
                    engine,
                    external_ref,
                    status,
                    json.dumps(meta or {}),
                ),
            ).fetchone()
        return _row(row)

    def update(self, workflow_id: UUID, data: dict[str, Any]) -> Workflow:
        allowed = ("name", "description", "engine", "external_ref", "status", "meta")
        sets: list[str] = ["updated_at = NOW()"]
        params: list[Any] = []
        for key in allowed:
            if key not in data:
                continue
            if key == "meta":
                sets.append("meta = %s::jsonb")
                params.append(json.dumps(data["meta"] or {}))
            else:
                sets.append(f"{key} = %s")
                params.append(data[key])
        params.append(workflow_id)
        with connection() as conn:
            row = conn.execute(
                f"""
                UPDATE knowledge.workflow
                SET {', '.join(sets)}
                WHERE id = %s
                RETURNING id, name, description, engine, external_ref, status, meta,
                          created_at AS created_on, updated_at AS updated_on
                """,
                params,
            ).fetchone()
        if not row:
            raise NotFoundError(f"workflow {workflow_id} not found")
        return _row(row)
