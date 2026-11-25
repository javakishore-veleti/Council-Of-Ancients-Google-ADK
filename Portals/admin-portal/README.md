# Council of Ancients — Admin Portal

Angular 19 ops console for Knowledge Bank ingest. Port **`:4201`**.

**Design:** ops console — cool ink rail, teal accents, IBM Plex. Deliberately *not* the customer chamber (copper/ivory), and not stock Berry/Breeze/MDB purple-gray templates.

**Stack:** Angular 19 · PrimeNG · Bootstrap Icons · IBM Plex Sans / Mono

## Architecture (locked)

```text
Admin UI (:4201)
  → coa_admin_api (:8094)     # only backend this UI calls
      → Postgres (sources, workflows, endpoints, wf_exec_log)
      → queue Download → wf_exec_log.wf_id = source.workflow_id
          → facade workflow (Airflow today) → extract → PATCH callbacks
```

Requires `coa_admin_api` on `:8094`. Start containers first (`npm run local:containers:all:start -- --postgres --observability`), then `npm run local:middleware:api:all:start` (Liquibase + admin). Middleware stop does not tear down Postgres.

## Run (from repo root — preferred)

```bash
npm run local:portals:all:start    # customer :4200 + admin :4201
npm run local:portals:all:status
npm run local:portals:all:stop
npm run local:portals:all:build
```

Admin: http://127.0.0.1:4201 · Customer: http://127.0.0.1:4200

## Pages

| Route | Purpose |
|-------|---------|
| `/dashboard` | Ops overview |
| `/knowledge/sources` | List sources (name, category, subcategory, ingest status, created on) |
| `/knowledge/sources/:uuid` | Source detail — download workflow, from/store-to, **Ops history**, tech-stack |
| `/workflows` | Workflow registry (criteria + searchable columns) |
| `/workflows/:uuid` | Workflow detail (engine, external ref, meta) |
| `/wf-exec-logs/:uuid` | Reusable execution detail — **Back** returns to owning source detail |
| `/app-endpoints` | Configure dependency targets (Postgres, Chroma, pgvector, AWS/Azure/GCP, …) |
| `/app-endpoints/:uuid` | Endpoint detail |

Primary key is a **UUID string** (`id`) — used in URLs, FKs, and store-path leaves.
