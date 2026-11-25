# Local Docker infra

## Default stack

```bash
./docker-all-up.sh
# or: npm run local:containers:all:start
```

| Service | URL / port | Role |
|---------|------------|------|
| Redis | `localhost:6379` | Cache / sessions |
| Jaeger UI | http://localhost:16686 | Distributed traces |
| OTEL Collector | `localhost:4317` (gRPC), `:4318` (HTTP) | OTLP front door → Jaeger + Prometheus |

## Optional Postgres

```bash
./docker-all-up.sh --postgres
```

## AIOps / LLMOps / DataOps (`--observability`)

```bash
./docker-all-up.sh --observability
# or: npm run local:containers:all:start:observability
```

| Domain | Service | URL | What you get |
|--------|---------|-----|----------------|
| **AIOps** | Prometheus | http://localhost:9090 | Time-series scrape of LLM + collector metrics |
| **AIOps** | Grafana | http://localhost:3000 (`admin`/`admin`) | Dashboard **Council LLMOps Overview** |
| **LLMOps** | Phoenix | http://localhost:6006 | Generations, spans, latency inspection |
| **DataOps** | Loki | http://localhost:3100 | Log aggregation (wire app logs later) |

### LLMOps metrics the app records

`--observability` also builds and starts the **`coa_observability_api` container** (`council-coa-observability-api` on port **8088**).

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
# once per session — data lives in volumes
npm run local:containers:all:start -- --postgres --observability

# bounce as often as you like
npm run local:middleware:api:all:start
npm run local:middleware:api:all:status
npm run local:middleware:api:all:stop
```

Middleware start: requires `council-postgres` already up → runs **Liquibase**
(`knowledge-db-apply.sh` → `db.changelog-master.xml` via Docker image) → host
`coa_agents_api` **:8090** and `coa_admin_api` **:8094**. No manual `psql`.

Needs repo-root `.env` with GCP / Model Armor for deliberation.  
Each model turn POSTs into `COA_OBS_API_URL` (default `http://localhost:8088`) `/v1/obs/feed`.

Foreground agents-only (debug): `./agents-api-up.sh`

### Combine flags (containers)

```bash
./docker-all-up.sh --postgres --observability
```

### Stop

```bash
npm run local:middleware:api:all:stop   # APIs only; DB stays
./docker-all-down.sh --volumes          # or: npm run local:containers:all:stop
# keep data: ./docker-all-down.sh --keep-volumes
```
