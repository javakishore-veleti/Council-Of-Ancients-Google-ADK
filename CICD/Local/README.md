# Local Docker infra

## Start containers

```bash
npm run local:containers:all:start
```

Postgres + Redis + Jaeger + OTEL + Prometheus + Grafana + Phoenix + Loki + `coa_observability_api` **:8088**.

| Service | URL / port |
|---------|------------|
| Redis | `localhost:6379` |
| Postgres | `localhost:5432` (`postgres`/`postgres`, db `council`) |
| Jaeger UI | http://localhost:16686 |
| OTEL Collector | `:4317` / `:4318` |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3000 (`admin`/`admin`) |
| Phoenix | http://localhost:6006 |
| Loki | http://localhost:3100 |
| Obs API | http://localhost:8088 |

### LLMOps metrics the app records

Ingest path: `POST http://localhost:8088/v1/obs/feed` → facade → toggle-gated tasks → plugins.  
Thin helpers: `Middleware/Observability/llmops.py` (`estimate_cost_usd`, `record_llm_call` → facade).

Fan-out is **off by default**. Enable in repo-root `.env`:

```bash
OBS_TASK_EMIT_METRICS=true   # Prometheus local plugin
OBS_TASK_EMIT_TRACES=true    # OTEL / Phoenix
OBS_TASK_EMIT_LOGS=true      # Loki
OBS_TASK_EMIT_LLMOPS=true    # combined LLMOps plugins
```

| Metric | Meaning |
|--------|---------|
| `council_llm_requests_total` | Generations by agent / model / status / wave |
| `council_llm_tokens_total` | Prompt vs completion tokens |
| `council_llm_cost_usd_total` | Estimated USD cost (rate table + env overrides) |
| `council_llm_duration_seconds` | End-to-end generation latency histogram |
| `council_llm_ttft_seconds` | Time-to-first-token histogram |
| OTEL spans `llm.<agent>` | Timestamps, tokens, cost, wave, session_id |

App Prometheus scrape target (host): http://localhost:9108/metrics  

API docs: [`Middleware/API-Services/coa_observability_api/README.md`](../../Middleware/API-Services/coa_observability_api/README.md)

## Middleware APIs (host only — agents + admin)

Containers and middleware are **independent**. Containers own durable storage (Postgres, Redis, obs). Middleware APIs are host processes that depend on that storage; restart them without touching Docker.

```bash
npm run local:containers:all:start
npm run local:middleware:api:all:start
npm run local:middleware:api:all:status
npm run local:middleware:api:all:stop
```

`local:containers:all:start` brings up Postgres + observability (durable volumes). Middleware is host APIs only — Liquibase then `coa_agents_api` **:8090** / `coa_admin_api` **:8094**. Bounce middleware without stopping containers.

Needs repo-root `.env` with GCP / Model Armor for deliberation.  
Obs feed: `COA_OBS_API_URL` (default `http://localhost:8088`) `/v1/obs/feed`.

Foreground agents-only (debug): `./agents-api-up.sh`

### Stop

```bash
npm run local:middleware:api:all:stop
npm run local:containers:all:stop
```
