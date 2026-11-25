# API Services

FastAPI / ADK runtime services that expose Council agents to portals and other clients.

| Service | Path | Role |
|---------|------|------|
| **coa_agents_api** | [`coa_agents_api/`](coa_agents_api/) | Council deliberate API (`POST /v1/council/deliberate`, operationId `deliberate`) |
| **coa_observability_api** | [`coa_observability_api/`](coa_observability_api/) | Async observability ingest (`POST /v1/obs/feed`, operationId `ingest_obs_feed`) |

## Local run

```bash
npm run local:middleware:api:all:start    # obs stack + coa_observability_api :8088 + coa_agents_api :8090
npm run local:middleware:api:all:status
npm run local:middleware:api:all:stop
```
