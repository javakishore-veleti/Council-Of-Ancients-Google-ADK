from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any


def admin_api_base() -> str:
    return os.environ.get("COA_ADMIN_API_URL", "http://127.0.0.1:8094").rstrip("/")


def patch_wf_exec_log(
    exec_id: str,
    *,
    status: str | None = None,
    external_run_id: str | None = None,
    error_message: str | None = None,
    detail: str | None = None,
) -> dict[str, Any]:
    """PATCH /v1/wf-exec-logs/{id} — used by facade DAG callbacks."""
    body: dict[str, Any] = {}
    if status is not None:
        body["status"] = status
    if external_run_id is not None:
        body["external_run_id"] = external_run_id
    if error_message is not None:
        body["error_message"] = error_message
    if detail is not None:
        body["detail"] = detail
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        f"{admin_api_base()}/v1/wf-exec-logs/{exec_id}",
        data=data,
        method="PATCH",
        headers={"Content-Type": "application/json", "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"admin_patch_failed:{exc.code}:{exc.read().decode('utf-8', errors='replace')}") from exc


def get_wf_exec_log(exec_id: str) -> dict[str, Any]:
    req = urllib.request.Request(
        f"{admin_api_base()}/v1/wf-exec-logs/{exec_id}",
        headers={"Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def get_knowledge_source(source_id: str) -> dict[str, Any]:
    req = urllib.request.Request(
        f"{admin_api_base()}/v1/knowledge/sources/{source_id}",
        headers={"Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))
