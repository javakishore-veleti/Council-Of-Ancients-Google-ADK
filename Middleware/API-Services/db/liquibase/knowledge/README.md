# Knowledge schema (Liquibase)

Postgres schema **`knowledge`** for `coa_knowledge_api` (Knowledge Bank API).

| Table | Role |
|-------|------|
| `knowledge_category` | Top-nav topics (roots) and left-nav sections (children via `parent_id`) |
| `knowledge_source` | Allowlisted corpus rows; `name` is the business key; `citation_name` / `citation_desc` feed indexing + chamber cites |

## Apply (local)

```bash
# Postgres up:
npm run local:containers:all:start -- --postgres   # or: bash CICD/Local/docker-all-up.sh --postgres

# From this directory (example with liquibase CLI):
liquibase \
  --changelog-file=changelog/db.changelog-master.xml \
  --url=jdbc:postgresql://localhost:5432/council \
  --username=postgres \
  --password=postgres \
  --default-schema-name=knowledge \
  update
```

Or run the SQL in `changelog/*.xml` via `psql` when Liquibase is not installed yet.
