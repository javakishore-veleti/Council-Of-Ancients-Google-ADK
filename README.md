# Council-Of-Ancients-Google-ADK

Multi-agent Council of Ancients on Google ADK, inspired by Daniela Petruzalek’s [AI Agents from Scratch with Google ADK](https://danicat.dev/posts/ai-agents-from-scratch-with-google-adk/) (companion reference: [danicat/council](https://github.com/danicat/council)).

## Layout

| Path | Role |
|------|------|
| `Middleware/Agents/` | ADK agents (Facilitator + counselors) |
| `Middleware/API-Services/` | FastAPI / ADK runtime APIs |
| `Portals/` | Angular portals |
| `CICD/Local/` | Local Docker infra (Redis, Jaeger, optional Postgres) |

## Local infrastructure

App persistence defaults to **SQLite**. Docker Postgres is optional.

```bash
# Redis + Jaeger (default)
npm run local:containers:all:start
# or: ./CICD/Local/docker-all-up.sh

# Also start Postgres and point the app at it (user/password: postgres/postgres)
npm run local:containers:all:start -- --postgres

npm run local:containers:all:status
npm run local:containers:all:stop
```

Copy `.env.template` → `.env` for app config. Compose defaults live under `CICD/Local/.env.example`.
