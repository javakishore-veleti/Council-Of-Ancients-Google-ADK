from __future__ import annotations

from typing import Any
from uuid import UUID

from coa_admin_api.domain.errors import NotFoundError
from coa_admin_api.domain.models import WfExecLog
from coa_admin_api.infrastructure.dao.db import connection

_SELECT = """
    SELECT id, source_id, engine, external_run_id, status,
           download_from_endpoint_id, store_to_endpoint_ids, tech_stack_endpoint_ids,
           started_at, finished_at, error_message, detail,
           created_at AS created_on, updated_at AS updated_on
    FROM knowledge.wf_exec_log
"""


def _uuids(v: Any) -> list[UUID]:
    if not v:
        return []
    return [x if isinstance(x, UUID) else UUID(str(x)) for x in v]


def _row(r: dict[str, Any]) -> WfExecLog:
    return WfExecLog(
        id=r["id"],
        source_id=r["source_id"],
        engine=r["engine"],
        external_run_id=r.get("external_run_id"),
        status=r["status"],
        download_from_endpoint_id=r.get("download_from_endpoint_id"),
        store_to_endpoint_ids=_uuids(r.get("store_to_endpoint_ids")),
        tech_stack_endpoint_ids=_uuids(r.get("tech_stack_endpoint_ids")),
        started_at=r.get("started_at"),
        finished_at=r.get("finished_at"),
        created_on=r["created_on"],
        updated_on=r["updated_on"],
        error_message=r.get("error_message"),
        detail=r.get("detail"),
    )


class WfExecDao:
    def list_for_source(self, source_id: UUID) -> list[WfExecLog]:
        with connection() as conn:
            rows = conn.execute(
                f"{_SELECT} WHERE source_id = %s ORDER BY created_at DESC",
                (source_id,),
            ).fetchall()
        return [_row(r) for r in rows]

    def get(self, exec_id: UUID) -> WfExecLog:
        with connection() as conn:
            row = conn.execute(f"{_SELECT} WHERE id = %s", (exec_id,)).fetchone()
        if not row:
            raise NotFoundError(f"wf_exec_log {exec_id} not found")
        return _row(row)

    def create_queued(
        self,
        *,
        source_id: UUID,
        download_from_endpoint_id: UUID | None,
        store_to_endpoint_ids: list[UUID],
        tech_stack_endpoint_ids: list[UUID],
        engine: str = "airflow",
        detail: str | None = None,
    ) -> WfExecLog:
        with connection() as conn:
            row = conn.execute(
                """
                INSERT INTO knowledge.wf_exec_log (
                  source_id, engine, status,
                  download_from_endpoint_id, store_to_endpoint_ids, tech_stack_endpoint_ids,
                  detail
                ) VALUES (%s, %s, 'queued', %s, %s, %s, %s)
                RETURNING id, source_id, engine, external_run_id, status,
                          download_from_endpoint_id, store_to_endpoint_ids, tech_stack_endpoint_ids,
                          started_at, finished_at, error_message, detail,
                          created_at AS created_on, updated_at AS updated_on
                """,
                (
                    source_id,
                    engine,
                    download_from_endpoint_id,
                    store_to_endpoint_ids,
                    tech_stack_endpoint_ids,
                    detail
                    or "Created by Admin UI Download; waiting for DAG pickup.",
                ),
            ).fetchone()
        return _row(row)

    def patch(
        self,
        exec_id: UUID,
        *,
        status: str | None = None,
        external_run_id: str | None = None,
        error_message: str | None = None,
        detail: str | None = None,
        mark_started: bool = False,
        mark_finished: bool = False,
    ) -> WfExecLog:
        sets = ["updated_at = NOW()"]
        params: list[Any] = []
        if status is not None:
            sets.append("status = %s")
            params.append(status)
        if external_run_id is not None:
            sets.append("external_run_id = %s")
            params.append(external_run_id)
        if error_message is not None:
            sets.append("error_message = %s")
            params.append(error_message)
        if detail is not None:
            sets.append("detail = %s")
            params.append(detail)
        if mark_started:
            sets.append("started_at = COALESCE(started_at, NOW())")
        if mark_finished:
            sets.append("finished_at = NOW()")
        params.append(exec_id)
        with connection() as conn:
            row = conn.execute(
                f"""
                UPDATE knowledge.wf_exec_log
                SET {', '.join(sets)}
                WHERE id = %s
                RETURNING id, source_id, engine, external_run_id, status,
                          download_from_endpoint_id, store_to_endpoint_ids, tech_stack_endpoint_ids,
                          started_at, finished_at, error_message, detail,
                          created_at AS created_on, updated_at AS updated_on
                """,
                params,
            ).fetchone()
        if not row:
            raise NotFoundError(f"wf_exec_log {exec_id} not found")
        return _row(row)
