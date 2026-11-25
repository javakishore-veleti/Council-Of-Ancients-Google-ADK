# Council of Ancients — Admin Portal

Angular 19 ops console for Knowledge Bank ingest. Port **`:4201`**.

**Design:** warm ivory + ink + copper (same family as customer portal). Not gray, black, purple, or Creative-Tim-style dark dashboards.

**Stack:** Angular 19 · PrimeNG · Bootstrap Icons · Source Sans 3

## Architecture (locked)

```text
Admin UI (:4201)
  → coa_admin_api (:8094)     # only backend this UI calls
      → coa_knowledge_api     # async queue download / status
          → Airflow DAG
              → callbacks to knowledge_api (started / completed / failed)
```

Until `coa_admin_api` is up, Knowledge Sources uses local fixtures and simulates queueing.

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
| `/knowledge/sources` | List sources · Download queues async job via Admin API |
