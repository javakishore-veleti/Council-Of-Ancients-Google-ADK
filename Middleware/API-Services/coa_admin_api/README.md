# coa_admin_api — Admin BFF

Neal Ford FastAPI BFF for the Admin portal. Port **`:8094`**.

```text
Admin UI (:4201) → coa_admin_api (:8094) → Postgres (knowledge schema)
```

| Concern | Tables |
|---------|--------|
| Sources (joined) | `knowledge_source` + `knowledge_category` + `knowledge_source_endpoint` |
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

1. Postgres: `npm run local:containers:all:start` (or `docker-all-up.sh --postgres`)
2. Schema + seeds:

```bash
psql postgresql://postgres:postgres@localhost:5432/council \
  -f Middleware/API-Services/db/liquibase/knowledge/bootstrap.sql
psql postgresql://postgres:postgres@localhost:5432/council \
  -f Middleware/API-Services/db/liquibase/knowledge/bootstrap-admin-ops.sql
```

3. `uv sync` (includes `psycopg`)

## Run

```bash
export PYTHONPATH=Middleware/API-Services
export COA_ADMIN_DATABASE_URL=postgresql://postgres:postgres@localhost:5432/council
uv run uvicorn coa_admin_api.presentation.app:app --host 0.0.0.0 --port 8094
# docs: http://127.0.0.1:8094/docs
```

Or: `npm run local:middleware:api:all:start` (starts agents + admin).

## Useful routes

- `GET /v1/knowledge/sources`
- `GET /v1/knowledge/sources/{id}`
- `POST /v1/knowledge/sources/{id}/download` — creates `wf_exec_log` (queued)
- `GET /v1/knowledge/sources/{id}/wf-exec-logs`
- `GET /v1/wf-exec-logs/{id}`
- `PATCH /v1/wf-exec-logs/{id}` — DAG callback stub
- `GET /v1/app-endpoints`
- `GET /v1/app-endpoints/{id}`
