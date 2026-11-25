# Knowledge schema (Liquibase)

Postgres schema **`knowledge`** for `coa_knowledge_api` (Knowledge Bank API).

| Table | Role |
|-------|------|
| `knowledge_category` | Top-nav topics (roots) and left-nav sections (children via `parent_id`) |
| `knowledge_source` | Allowlisted corpus rows; `name` is the business key; `citation_name` / `citation_desc` feed indexing + chamber cites |
| `app_endpoint` | Configurable dependency targets (Postgres, Chroma, S3, HTTP origins, …) |
| `knowledge_source_endpoint` | Source ↔ endpoint maps (`download_from` / `store_to` / `tech_stack`) |
| `wf_exec_log` | Download/ops execution history |

## Apply (local)

```bash
# Postgres up:
bash CICD/Local/docker-all-up.sh --postgres

# Schema + seeds (no Liquibase CLI required):
psql postgresql://postgres:postgres@localhost:5432/council \
  -f Middleware/API-Services/db/liquibase/knowledge/bootstrap.sql
psql postgresql://postgres:postgres@localhost:5432/council \
  -f Middleware/API-Services/db/liquibase/knowledge/bootstrap-admin-ops.sql
```

Or with Liquibase CLI against `changelog/db.changelog-master.xml`, then still run `bootstrap-admin-ops.sql` for fixed-UUID seeds.
