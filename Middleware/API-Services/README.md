# API Services

FastAPI / ADK runtime services that expose Council agents to portals and other clients.

| Service | Path | Role |
|---------|------|------|
| **coa_observability_api** | [`coa_observability_api/`](coa_observability_api/) | Async observability ingest (`POST /v1/obs/feed`, operationId `ingest_obs_feed`) |

See [`coa_observability_api/README.md`](coa_observability_api/README.md) for run instructions, task toggles (`OBS_TASK_EMIT_*`), and sample curl.
