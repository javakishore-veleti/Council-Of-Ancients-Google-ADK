# COA Knowledge Airflow DAGs

Admin never talks to Airflow. `coa_admin_api` queues a `wf_exec_log` with **`wf_id`** from the source’s `workflow_id`, then the engine picks up the **facade** workflow.

| DAG id | Role | Conf |
|--------|------|------|
| `kb_ingest_facade` | Facade — gate, invoke extract, PATCH `wf_exec_log` | `{ "wf_exec_log_id": "<uuid>" }` |
| `kb_extract` | Extract only — URL → Markdown under UUID leaf | url, source_id, category_code, subcategory_code, optional strategy_id |

Set `AIRFLOW_HOME` / `dags_folder` to this directory (or symlink). `PYTHONPATH` must include the repo root.

```bash
export PYTHONPATH=/path/to/Council-Of-Ancients-Google-ADK
export COA_ADMIN_API_URL=http://127.0.0.1:8094
# Optional: skip TriggerDagRun and run extract in-process inside the facade
export COA_KB_EXTRACT_VIA_TRIGGER=0
```

Local facade without Airflow:

```bash
PYTHONPATH=. uv run python -c "
from DataOps.kb.pipeline.facade_runner import run_ingest_facade
print(run_ingest_facade('<wf_exec_log_id>'))
"
```
