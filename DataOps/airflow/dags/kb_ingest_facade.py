"""
kb_ingest_facade — Admin-facing facade DAG.

Triggered with conf: { "wf_exec_log_id": "<uuid>" }.
Orchestrates gate + invokes kb_extract (TriggerDagRun when enabled;
falls back to in-process extract for local runs).

Always PATCHes wf_exec_log on start and on any task failure.
"""

from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

try:
    from airflow import DAG
    from airflow.operators.python import PythonOperator
    from airflow.operators.trigger_dagrun import TriggerDagRunOperator
except ImportError:  # pragma: no cover
    DAG = None  # type: ignore
    PythonOperator = None  # type: ignore
    TriggerDagRunOperator = None  # type: ignore


def _conf(context) -> dict:
    conf = (context.get("dag_run") and context["dag_run"].conf) or {}
    return conf or {}


def _exec_id(context) -> str | None:
    return _conf(context).get("wf_exec_log_id")


def _run_id(context) -> str | None:
    rid = context.get("run_id")
    return str(rid) if rid else None


def _safe_patch(exec_id: str | None, **kwargs) -> None:
    """Never raise from status callbacks — ops must still update."""
    if not exec_id:
        return
    try:
        from DataOps.kb.pipeline.admin_callback import patch_wf_exec_log

        patch_wf_exec_log(exec_id, **kwargs)
    except Exception:
        pass


def _on_failure(context) -> None:
    """DAG/task failure → always mark wf_exec_log failed with Airflow run id."""
    exec_id = _exec_id(context)
    exc = context.get("exception")
    msg = (str(exc) if exc else "dag_failed")[:500]
    task = context.get("task_instance")
    task_id = getattr(task, "task_id", None) or "unknown"
    _safe_patch(
        exec_id,
        status="failed",
        external_run_id=_run_id(context),
        error_message=msg,
        detail=f"dag_task_failed:{task_id}",
    )


def _start(**context):
    from DataOps.kb.pipeline import license_gate, robots
    from DataOps.kb.pipeline.admin_callback import get_knowledge_source, get_wf_exec_log
    from DataOps.kb.pipeline.extract import ExtractOptions

    conf = _conf(context)
    exec_id = conf.get("wf_exec_log_id")
    if not exec_id:
        raise ValueError("wf_exec_log_id required in dag_run.conf")

    run_id = _run_id(context) or f"airflow-{exec_id}"
    _safe_patch(
        exec_id,
        status="started",
        external_run_id=str(run_id),
        detail="facade started",
    )

    log = get_wf_exec_log(exec_id)
    source_id = str(log["source_id"])
    source = get_knowledge_source(source_id)
    url = (source.get("url") or "").strip()
    if not url:
        _safe_patch(exec_id, status="failed", error_message="source_has_no_url")
        raise RuntimeError("source_has_no_url")

    if not license_gate.allowed(source.get("license")):
        _safe_patch(
            exec_id,
            status="failed",
            error_message="denied_license",
            detail=str(source.get("license")),
        )
        raise RuntimeError("denied_license")

    ua = ExtractOptions().user_agent
    if not robots.allowed_by_robots(url, ua):
        _safe_patch(exec_id, status="failed", error_message="denied_robots", detail=url)
        raise RuntimeError("denied_robots")

    _safe_patch(exec_id, status="running", detail="invoking kb_extract")
    payload = {
        "wf_exec_log_id": exec_id,
        "url": url,
        "source_id": source_id,
        "category_code": source["category_code"],
        "subcategory_code": source["subcategory_code"],
        "strategy_id": (source.get("meta") or {}).get("extract_strategy"),
        "wf_id": log.get("wf_id"),
    }
    context["ti"].xcom_push(key="extract_conf", value=payload)
    return payload


def _finalize(**context):
    import json

    conf = _conf(context)
    exec_id = conf.get("wf_exec_log_id")
    ti = context["ti"]
    extract = ti.xcom_pull(task_ids="extract_inline", key="return_value")
    if extract is None:
        extract = ti.xcom_pull(task_ids="trigger_kb_extract", key="return_value")
    if extract is None:
        extract = {"note": "kb_extract finished"}
    detail = json.dumps(extract if isinstance(extract, dict) else {"result": extract})
    _safe_patch(
        exec_id,
        status="completed",
        external_run_id=_run_id(context),
        detail=detail,
    )


def _extract_inline(**context):
    """Local / no-Trigger fallback: call extract runner in-process."""
    from DataOps.kb.pipeline.extract_runner import run_extract

    payload = context["ti"].xcom_pull(task_ids="start_facade", key="extract_conf") or {}
    return run_extract(
        url=payload["url"],
        source_id=str(payload["source_id"]),
        category_code=payload["category_code"],
        subcategory_code=payload["subcategory_code"],
        strategy_id=payload.get("strategy_id"),
    )


if DAG is not None:
    use_trigger = os.environ.get("COA_KB_EXTRACT_VIA_TRIGGER", "1") == "1"

    with DAG(
        dag_id="kb_ingest_facade",
        description="Facade ingest: gate → kb_extract → patch wf_exec_log",
        start_date=datetime(2026, 11, 1),
        schedule=None,
        catchup=False,
        tags=["coa", "knowledge", "facade"],
        params={"wf_exec_log_id": ""},
        default_args={"on_failure_callback": _on_failure},
        on_failure_callback=_on_failure,
    ) as dag:
        start = PythonOperator(task_id="start_facade", python_callable=_start)

        if use_trigger and TriggerDagRunOperator is not None:
            trigger = TriggerDagRunOperator(
                task_id="trigger_kb_extract",
                trigger_dag_id="kb_extract",
                conf="{{ ti.xcom_pull(task_ids='start_facade', key='extract_conf') }}",
                wait_for_completion=True,
                poke_interval=5,
                reset_dag_run=True,
            )
            finalize = PythonOperator(task_id="finalize", python_callable=_finalize)
            start >> trigger >> finalize
        else:
            inline = PythonOperator(task_id="extract_inline", python_callable=_extract_inline)
            finalize = PythonOperator(task_id="finalize", python_callable=_finalize)
            start >> inline >> finalize
