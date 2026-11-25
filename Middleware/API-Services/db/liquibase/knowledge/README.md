# Knowledge schema (Liquibase)

Postgres schema **`knowledge`** for Knowledge Bank / Admin ops.

Schema management is **Liquibase** under this tree (outside Python packages) — not Alembic inside apps. See Product_Ideas.

| Table | Role |
|-------|------|
| `knowledge_category` | Top-nav topics (roots) and left-nav sections (children via `parent_id`) |
| `knowledge_source` | Allowlisted corpus rows; `workflow_id` = Download workflow |
| `workflow` | Named ingest/ops workflows (`engine`: airflow, step_functions, emr, …) |
| `app_endpoint` | Configurable dependency targets |
| `knowledge_source_endpoint` | Source ↔ endpoint maps (`download_from` / `store_to` / `tech_stack`) |
| `wf_exec_log` | Ops history; `wf_id` → `workflow.id` |

## Apply (local — preferred)

```bash
npm run local:middleware:api:all:start
```

That starts Postgres and runs `CICD/Local/knowledge-db-apply.sh`, which executes
**Liquibase** (`liquibase/liquibase` Docker image) against
`changelog/db.changelog-master.xml` (001 → 006).

Manual:

```bash
npm run local:containers:all:start
bash CICD/Local/knowledge-db-apply.sh
```

## Changelog layout

```text
changelog/
  db.changelog-master.xml
  001-knowledge-schema.xml
  002-seed-topic-categories.xml
  003-admin-ops-schema.xml
  004-seed-admin-ops.xml          → sql/004-seed-admin-ops.sql
  005-workflow-registry.xml
  006-seed-workflows.xml          → sql/006-seed-workflows.sql
liquibase.properties
```

## Bootstrap `.sql` files

`bootstrap.sql`, `bootstrap-admin-ops.sql`, and `bootstrap-workflows.sql` remain as
**optional one-shot dumps** for emergency/offline use. Local start does **not** use them;
Liquibase is the source of truth.
