# coa_observability_api

Async observability ingest for Council of Ancients (Neal Ford layered layout).

## Architecture

```text
API (ingest_obs_feed)
  → ObservabilityFacade
    → Tasks (ONLY if OBS_TASK_* = true in .env; default OFF)
      → each Task invokes its SubFacade
        → SubFacade fans out to vendor plugins
```

HTTP returns **202 Accepted** quickly; fan-out runs on a background thread. Soft-fail per task/plugin — never raise to callers.

## OpenAPI

| Field | Value |
|-------|--------|
| operationId | `ingest_obs_feed` |
| Method / path | `POST /v1/obs/feed` |
| Body | `{ "session_id", "ctx_data": { ..., "obs_data": { ... } } }` |
| Response | `202` + `{ "ingest_id", "status": "accepted" }` |

`obs_data` is a **child of `ctx_data`**, not a top-level field.

## Run

### Docker (recommended with local stack)

```bash
npm run local:containers:all:start:observability
# builds + starts council-coa-observability-api with Prometheus/Grafana/Phoenix/Loki
```

API: http://localhost:8088 · OpenAPI: http://localhost:8088/docs · Health: `/healthz`

Task toggles for the container live in `CICD/Local/.env` (`OBS_TASK_EMIT_*`, default `false`).

### Host uvicorn (optional)

```bash
PYTHONPATH=Middleware/API-Services \
  uv run uvicorn coa_observability_api.presentation.app:app \
  --host 0.0.0.0 --port 8088
```

## Task toggles (default OFF)

Set in repo-root `.env` (from `.env.template`):

```bash
OBS_TASK_EMIT_METRICS=false
OBS_TASK_EMIT_TRACES=false
OBS_TASK_EMIT_LOGS=false
OBS_TASK_EMIT_LLMOPS=false
```

| Env | Task → SubFacade → typical local plugins |
|-----|------------------------------------------|
| `OBS_TASK_EMIT_METRICS` | Metrics → Prometheus (+ cloud stubs) |
| `OBS_TASK_EMIT_TRACES` | Traces → OTEL / Phoenix (+ stubs) |
| `OBS_TASK_EMIT_LOGS` | Logs → Loki / Phoenix (+ stubs) |
| `OBS_TASK_EMIT_LLMOPS` | LLMOps → Prometheus + OTEL + Phoenix (+ stubs) |

GCP / AWS / Azure / LangChain plugins are **stubs** (no-op + log once).

## Sample curl

All tasks off (accept only):

```bash
curl -sS -X POST http://localhost:8088/v1/obs/feed \
  -H 'Content-Type: application/json' \
  -d '{
    "session_id": "sess-smoke-1",
    "ctx_data": {
      "obs_data": {
        "event_type": "llm_call",
        "agent": "plato",
        "model": "gemini-2.5-flash",
        "prompt_tokens": 120,
        "completion_tokens": 80,
        "duration_seconds": 1.25,
        "ttft_seconds": 0.4,
        "status": "ok",
        "deliberation_wave": "openings"
      }
    }
  }'
```

Enable metrics then re-POST:

```bash
export OBS_TASK_EMIT_METRICS=true
# restart uvicorn so env is picked up
curl -sS http://localhost:9108/metrics | head
```

## Layout

```text
presentation/     FastAPI app, schemas, routes
application/      ObservabilityFacade, tasks, sub_facades
domain/           ObsFeedEvent, toggles
infrastructure/   vendor plugins (local + cloud stubs)
```

Thin agent-side helpers remain in [`Middleware/Observability/llmops.py`](../../Observability/llmops.py) (`estimate_cost_usd`, `record_llm_call` → facade).
