from __future__ import annotations

from typing import Any
from uuid import UUID

from coa_admin_api.domain.errors import NotFoundError
from coa_admin_api.domain.models import AppEndpoint
from coa_admin_api.infrastructure.dao.db import connection

_SELECT = """
    SELECT id, name, kind, provider, endpoint_url, resource, region, status, notes,
           created_at, updated_at
    FROM knowledge.app_endpoint
"""


def _row(r: dict[str, Any]) -> AppEndpoint:
    return AppEndpoint(
        id=r["id"],
        name=r["name"],
        kind=r["kind"],
        provider=r["provider"],
        endpoint_url=r["endpoint_url"],
        resource=r["resource"],
        region=r.get("region"),
        status=r["status"],
        notes=r.get("notes"),
        created_at=r.get("created_at"),
        updated_at=r.get("updated_at"),
    )


class EndpointDao:
    def list(self) -> list[AppEndpoint]:
        with connection() as conn:
            rows = conn.execute(f"{_SELECT} ORDER BY name").fetchall()
        return [_row(r) for r in rows]

    def get(self, endpoint_id: UUID) -> AppEndpoint:
        with connection() as conn:
            row = conn.execute(f"{_SELECT} WHERE id = %s", (endpoint_id,)).fetchone()
        if not row:
            raise NotFoundError(f"endpoint {endpoint_id} not found")
        return _row(row)
