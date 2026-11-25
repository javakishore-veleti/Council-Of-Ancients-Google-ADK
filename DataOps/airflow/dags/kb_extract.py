"""
kb_extract — extract DAG (NOT the Admin-facing facade).

Invoked by kb_ingest_facade (TriggerDagRun) or run alone for tests.
Swappable: change strategy_id / replace this DAG without touching Admin UI.
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
except ImportError:  # pragma: no cover — DAG file only loads under Airflow
    DAG = None  # type: ignore
    PythonOperator = None  # type: ignore


def _run_extract(**context):
    from DataOps.kb.pipeline.extract_runner import run_extract

    conf = (context.get("dag_run") and context["dag_run"].conf) or {}
    conf = conf or context.get("params") or {}
    required = ("url", "source_id", "category_code", "subcategory_code")
    missing = [k for k in required if not conf.get(k)]
    if missing:
        raise ValueError(f"kb_extract missing conf keys: {missing}")
    result = run_extract(
        url=conf["url"],
        source_id=str(conf["source_id"]),
        category_code=conf["category_code"],
        subcategory_code=conf["subcategory_code"],
        strategy_id=conf.get("strategy_id"),
        render_js=bool(conf.get("render_js", False)),
    )
    context["ti"].xcom_push(key="extract_result", value=result)
    return result


if DAG is not None:
    with DAG(
        dag_id="kb_extract",
        description="URL-agnostic extract → Markdown under KnowledgeBase UUID leaf",
        start_date=datetime(2026, 11, 1),
        schedule=None,
        catchup=False,
        tags=["coa", "knowledge", "extract"],
        params={
            "url": "",
            "source_id": "",
            "category_code": "",
            "subcategory_code": "",
            "strategy_id": None,
            "render_js": False,
        },
    ) as dag:
        PythonOperator(
            task_id="extract",
            python_callable=_run_extract,
        )
