# coa_agents_api

FastAPI entry for Council of Ancients agents (Facilitator + counselors).

## Architecture

```text
POST /v1/council/deliberate
  → InMemoryRunner(App council_of_ancients)  # process-wide; sessions persist
      → Facilitator → Plato / Descartes / Machiavelli
      → after_model_callback → record_llm_call
          → HTTP POST COA_OBS_API_URL/v1/obs/feed  (default :8088)
          → fallback: in-process ObservabilityFacade
              → OBS_TASK_* tasks → Prometheus / OTEL / … (default off)
```

## OpenAPI

| Field | Value |
|-------|--------|
| operationId | `deliberate` |
| Method / path | `POST /v1/council/deliberate` |
| Body | `{ "session_id", "message", "user_id?", "ctx_data?" }` |

## Run

```bash
npm run local:middleware:api:all:start
# → agents http://localhost:8090/docs · obs http://localhost:8088/docs
```

Sample:

```bash
curl -sS -X POST http://localhost:8090/v1/council/deliberate \
  -H 'Content-Type: application/json' \
  -d '{
    "session_id": "sess-1",
    "message": "Should we leave a stable job for an early-stage startup?",
    "ctx_data": { "wave": "openings" }
  }'
```

Requires repo-root `.env` with `GOOGLE_CLOUD_PROJECT`, Vertex flags, and Model Armor template paths.
