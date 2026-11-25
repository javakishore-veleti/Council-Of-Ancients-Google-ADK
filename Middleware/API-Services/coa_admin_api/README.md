# coa_admin_api — Admin BFF

Neal Ford FastAPI BFF for the Admin portal. Port **`:8094`**.

```text
Admin UI (:4201) → coa_admin_api (:8094) → Postgres (knowledge schema)
```

| Concern | Tables |
|---------|--------|
| Sources (joined) | `knowledge_source` + `knowledge_category` + `knowledge_source_endpoint` |
| Workflows | `workflow` (`knowledge_source.workflow_id`, `wf_exec_log.wf_id`) |
| App Endpoints | `app_endpoint` |
| Ops history | `wf_exec_log` |

## Layout

```text
presentation/           routes + schemas + app
application/
  facade/               AdminFacade
  tasks/                EndpointCrudTask, SourceOpsTask
  sub_facades/          Endpoint / Source / WfExec
infrastructure/dao/     EndpointDao, AdminSourceDao, WfExecDao, db
domain/                 models, errors
```

## Prerequisites

`uv sync` (includes `psycopg`). Postgres client (`psql`) on PATH for schema apply.

## Run (preferred)

```bash
npm run local:middleware:api:all:start
```

That starts Postgres + observability, runs **Liquibase** on the knowledge changelog
(`CICD/Local/knowledge-db-apply.sh` → `db.changelog-master.xml`), then
`coa_agents_api` + `coa_admin_api`.

Manual uvicorn only (schema already applied):

```bash
export PYTHONPATH=Middleware/API-Services
export COA_ADMIN_DATABASE_URL=postgresql://postgres:postgres@localhost:5432/council
uv run uvicorn coa_admin_api.presentation.app:app --host 0.0.0.0 --port 8094
# docs: http://127.0.0.1:8094/docs
```

## Useful routes

- `GET /v1/workflows` / `GET|POST /v1/workflows` / `PATCH /v1/workflows/{id}`
- `GET /v1/knowledge/sources`
- `GET /v1/knowledge/sources/{id}`
- `POST /v1/knowledge/sources/{id}/download` — creates `wf_exec_log` with `wf_id` from source
- `GET /v1/knowledge/sources/{id}/wf-exec-logs`
- `GET /v1/wf-exec-logs/{id}`
- `PATCH /v1/wf-exec-logs/{id}` — facade callback
- `GET /v1/app-endpoints`
- `GET /v1/app-endpoints/{id}`
