from __future__ import annotations

import json
import os
from typing import Any, Callable

from . import license_gate, robots
from .admin_callback import get_knowledge_source, get_wf_exec_log, patch_wf_exec_log
from .extract import ExtractOptions
from .extract_runner import run_extract

ExtractInvoker = Callable[..., dict[str, Any]]


def _default_extract_invoker(**kwargs: Any) -> dict[str, Any]:
    """In-process extract (local / tests). Airflow facade swaps this for TriggerDagRun."""
    return run_extract(**kwargs)


def run_ingest_facade(
    wf_exec_log_id: str,
    *,
    external_run_id: str | None = None,
    strategy_id: str | None = None,
    extract_invoker: ExtractInvoker | None = None,
    skip_admin_callbacks: bool = False,
) -> dict[str, Any]:
    """Facade orchestration: gate → invoke extract → finalize wf_exec_log.

    Extract is intentionally injected so Airflow can trigger kb_extract DAG
    instead of calling the strategy in-process — swap extractors without
    changing this facade contract.
    """
    invoker = extract_invoker or _default_extract_invoker
    run_id = external_run_id or os.environ.get("AIRFLOW_RUN_ID") or f"local-{wf_exec_log_id}"

    def _patch(**kwargs: Any) -> None:
        if skip_admin_callbacks:
            return
        patch_wf_exec_log(wf_exec_log_id, **kwargs)

    _patch(status="started", external_run_id=run_id, detail="facade started")

    try:
        if skip_admin_callbacks:
            raise RuntimeError(
                "skip_admin_callbacks requires caller to pass source via extract_invoker only"
            )

        log = get_wf_exec_log(wf_exec_log_id)
        source_id = str(log["source_id"])
        source = get_knowledge_source(source_id)
        url = (source.get("url") or "").strip()
        if not url:
            raise RuntimeError("source_has_no_url")

        license_id = source.get("license")
        if not license_gate.allowed(license_id):
            _patch(
                status="failed",
                error_message="denied_license",
                detail=json.dumps({"license": license_id}),
            )
            return {"status": "failed", "reason": "denied_license", "license": license_id}

        ua = ExtractOptions().user_agent
        if not robots.allowed_by_robots(url, ua):
            _patch(
                status="failed",
                error_message="denied_robots",
                detail=json.dumps({"url": url}),
            )
            return {"status": "failed", "reason": "denied_robots", "url": url}

        _patch(status="running", detail="invoking extract")

        extract_out = invoker(
            url=url,
            source_id=source_id,
            category_code=source["category_code"],
            subcategory_code=source["subcategory_code"],
            strategy_id=strategy_id or (source.get("meta") or {}).get("extract_strategy"),
        )

        detail = json.dumps(
            {
                "store_dir": extract_out.get("store_dir"),
                "strategy_id": extract_out.get("strategy_id"),
                "markdown_chars": extract_out.get("markdown_chars"),
            }
        )
        _patch(status="completed", detail=detail)
        return {
            "status": "completed",
            "wf_exec_log_id": wf_exec_log_id,
            "source_id": source_id,
            "extract": extract_out,
        }
    except Exception as exc:
        _patch(status="failed", error_message=str(exc)[:500], detail="facade_error")
        raise
