# Council of Ancients — Admin Portal

Angular 19 ops console for Knowledge Bank ingest. Port **`:4201`**.

**Design:** ops console — cool ink rail, teal accents, IBM Plex. Deliberately *not* the customer chamber (copper/ivory), and not stock Berry/Breeze/MDB purple-gray templates.

**Stack:** Angular 19 · PrimeNG · Bootstrap Icons · IBM Plex Sans / Mono

## Architecture (locked)

```text
Admin UI (:4201)
  → coa_admin_api (:8094)     # only backend this UI calls
      → coa_knowledge_api     # async queue download / status
          → Airflow DAG
              → callbacks to knowledge_api (started / completed / failed)
```

Requires `coa_admin_api` on `:8094` (Postgres-backed). Apply knowledge bootstrap + `bootstrap-admin-ops.sql`, then `npm run local:middleware:api:all:start`.

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
| `/knowledge/sources/:uuid` | Source detail — download from/store-to, **Ops history (`wf_exec_log`)**, tech-stack |
| `/wf-exec-logs/:uuid` | Reusable execution detail — **Back** returns to owning source detail |
| `/app-endpoints` | Configure dependency targets (Postgres, Chroma, pgvector, AWS/Azure/GCP, …) |
| `/app-endpoints/:uuid` | Endpoint detail |

Primary key is a **UUID string** (`id`) — used in URLs, FKs, and store-path leaves.
