# coa_knowledge_api — Knowledge Bank

Neal Ford FastAPI service for knowledge registry CRUD. Schema: Postgres `knowledge`.

```text
API (presentation/routes)
  → Facade (application/facade)
    → Tasks (application/tasks)
      → SubFacades (application/sub_facades)
        → DAO (infrastructure/dao)
```

| Table | Role |
|-------|------|
| `knowledge_category` | Top-nav topics (`parent_id` NULL) and left-nav sections (children) |
| `knowledge_source` | Corpus rows; **`name`** unique lookup key; **`citation_name` / `citation_desc`** for indexing + chamber cites |

Port **`:8093`**.

## Layout

```text
presentation/           routes + Pydantic schemas + app
application/
  facade/               KnowledgeFacade
  tasks/                CategoryCrudTask, SourceCrudTask
  sub_facades/          CategorySubFacade, SourceSubFacade
infrastructure/
  dao/                  CategoryDao, SourceDao, db
domain/                 models, errors
```

## Prerequisites

1. Postgres (`council` DB): `bash CICD/Local/docker-all-up.sh --postgres`
2. Apply schema: `psql … -f Middleware/API-Services/db/liquibase/knowledge/bootstrap.sql`
3. `uv sync` (includes `psycopg`)

## Run

```bash
export PYTHONPATH=Middleware/API-Services
export COA_KNOWLEDGE_DATABASE_URL=postgresql://postgres:postgres@localhost:5432/council
uv run uvicorn coa_knowledge_api.presentation.app:app --host 0.0.0.0 --port 8093
# docs: http://localhost:8093/docs
```

## Useful routes

- `GET /v1/knowledge/categories?roots_only=true` — top-nav topics  
- `GET /v1/knowledge/categories?parent_id=<uuid>` — left-nav under a topic  
- `GET /v1/knowledge/categories/by-code/styles`  
- `POST /v1/knowledge/sources` — `name`, `citation_name`, `citation_desc`, `category_id`  
- `GET /v1/knowledge/sources?category_code=styles`  
- `GET /v1/knowledge/sources/by-name/{name}`
