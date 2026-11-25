# API Services

FastAPI / ADK runtime services that expose Council agents to portals and other clients.

| Service | Path | Role |
|---------|------|------|
| **coa_agents_api** | [`coa_agents_api/`](coa_agents_api/) | Council deliberate API (`POST /v1/council/deliberate`, operationId `deliberate`) |
| **coa_observability_api** | [`coa_observability_api/`](coa_observability_api/) | Async observability ingest (`POST /v1/obs/feed`, operationId `ingest_obs_feed`) |
| **coa_knowledge_api** | [`coa_knowledge_api/`](coa_knowledge_api/) | Knowledge Bank CRUD (`knowledge_category`, `knowledge_source`) on `:8093` |

## Local run

```bash
npm run local:containers:all:start -- --postgres --observability   # durable DB / Redis / obs
npm run local:middleware:api:all:start    # Liquibase + agents :8090 + admin :8094 (host; bounce anytime)
npm run local:middleware:api:all:status
npm run local:middleware:api:all:stop     # APIs only — does not stop containers

```
