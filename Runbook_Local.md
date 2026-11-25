# Local runbook — download a page into the Knowledge Base

Goal: take the seeded DigitalOcean GoF tutorial URL, queue a download in Admin, run the ingest facade, and see Markdown on disk under your local Knowledge Base.

---

## Table of contents

1. [What this does (one picture)](#1-what-this-does-one-picture)
2. [Prerequisites](#2-prerequisites)
3. [Start the local stack](#3-start-the-local-stack)
4. [Open the seeded GoF source](#4-open-the-seeded-gof-source)
5. [Queue Download](#5-queue-download)
6. [Run the ingest facade (DAG path)](#6-run-the-ingest-facade-dag-path)
7. [Confirm files on disk](#7-confirm-files-on-disk)
8. [Optional — Airflow instead of the local runner](#8-optional--airflow-instead-of-the-local-runner)
9. [Stop everything](#9-stop-everything)
10. [Quick troubleshooting](#10-quick-troubleshooting)

---

## 1. What this does (one picture)

```text
Admin UI  →  coa_admin_api  →  wf_exec_log (queued)
                                    ↓
                         kb_ingest_facade  (entry workflow)
                                    ↓
                         kb_extract        (internal DAG / step)
                                    ↓
              $HOME/.../KnowledgeBase/{category}/{subcategory}/{source_uuid}/
                 content.md   meta.json   original.html
```

| Piece | Role |
|-------|------|
| **Source** | Allowlisted row (URL + license + workflow) |
| **Workflow** | Only entry facades in DB — seed: `kb_ingest_facade` |
| **`wf_exec_log`** | One row per Download click (`wf_id` = facade) |
| **Extract** | Internal to the facade — not a Workflows-table row |

Example URL (already seeded):

https://www.digitalocean.com/community/tutorials/gangs-of-four-gof-design-patterns

---

## 2. Prerequisites

| Need | Notes |
|------|--------|
| Docker Desktop | Running |
| `uv` | Python deps (`uv sync` from repo root) |
| `psql` | Client on PATH (Liquibase apply waits on Postgres) |
| Node / npm | Portals |
| Repo clone | Work from repo root for all commands below |

Optional for HTTPS extract on some Macs:

```bash
export COA_KB_SSL_INSECURE=1
```

---

## 3. Start the local stack

From repo root:

```bash
uv sync
npm run local:middleware:api:all:start
npm run local:portals:all:start
```

What middleware start does for you:

1. Postgres + observability containers  
2. **Liquibase** on the knowledge changelog  
3. `coa_agents_api` **:8090** and `coa_admin_api` **:8094**

| URL | What |
|-----|------|
| http://127.0.0.1:4201 | Admin portal |
| http://127.0.0.1:8094/docs | Admin API |
| http://127.0.0.1:4200 | Customer portal (not needed for this runbook) |

Check:

```bash
npm run local:middleware:api:all:status
npm run local:portals:all:status
curl -sf http://127.0.0.1:8094/healthz
```

---

## 4. Open the seeded GoF source

1. Open http://127.0.0.1:4201  
2. **Knowledge sources**  
3. Open **DigitalOcean GoF hub**

| Field | Seeded value |
|-------|----------------|
| Name | DigitalOcean GoF hub |
| Id | `d85e1c09-8157-5565-82d3-f9f3cf209509` |
| URL | DigitalOcean GoF tutorial (link above) |
| Download workflow | `kb_ingest_facade` |
| Category / sub | Architecture → Patterns (`software_architecture` / `patterns`) |

Or via API:

```bash
curl -sf http://127.0.0.1:8094/v1/knowledge/sources/d85e1c09-8157-5565-82d3-f9f3cf209509 | python3 -m json.tool
```

---

## 5. Queue Download

On the source detail page:

1. Open **Download — from / store to**  
2. Click **Download**

That only creates a **`wf_exec_log`** (`status=queued`) with `wf_id` = `kb_ingest_facade`. It does **not** fetch the page yet.

Copy the new exec id from **Ops history** (or from the API response):

```bash
curl -sf -X POST \
  http://127.0.0.1:8094/v1/knowledge/sources/d85e1c09-8157-5565-82d3-f9f3cf209509/download \
  | python3 -m json.tool
```

Note `wf_exec_log_id` from the JSON.

---

## 6. Run the ingest facade (DAG path)

Preferred for a new laptop: run the same facade code **without** installing Airflow.

```bash
export PYTHONPATH=.
export COA_ADMIN_API_URL=http://127.0.0.1:8094
# export COA_KB_SSL_INSECURE=1   # if SSL verify fails

uv run python -c "
from DataOps.kb.pipeline.facade_runner import run_ingest_facade
print(run_ingest_facade('PASTE_WF_EXEC_LOG_ID_HERE'))
"
```

What runs:

1. Load source + license / robots gate  
2. Extract URL → clean Markdown (`generic_markdown`)  
3. Write under the Knowledge Base UUID leaf  
4. PATCH `wf_exec_log` → `completed` (or `failed`)

Refresh source detail → **Ops history** should show **completed**.

---

## 7. Confirm files on disk

Default store path:

```text
$HOME/runtime_data/apps/datasets/COA/KnowledgeBase/
  software_architecture/patterns/d85e1c09-8157-5565-82d3-f9f3cf209509/
    content.md
    meta.json
    original.html
```

```bash
ls -la "$HOME/runtime_data/apps/datasets/COA/KnowledgeBase/software_architecture/patterns/d85e1c09-8157-5565-82d3-f9f3cf209509/"
head -40 "$HOME/runtime_data/apps/datasets/COA/KnowledgeBase/software_architecture/patterns/d85e1c09-8157-5565-82d3-f9f3cf209509/content.md"
```

Override root with `KB_LOCAL_ROOT` if needed.

**Do not commit** these files — the repo is public; KB blobs stay outside git.

---

## 8. Optional — Airflow instead of the local runner

If you already run Airflow locally:

| DAG id | In Workflows table? | Job |
|--------|---------------------|-----|
| `kb_ingest_facade` | Yes (entry) | Gate → trigger extract → PATCH log |
| `kb_extract` | No (internal) | URL → Markdown on disk |

```bash
export PYTHONPATH=/absolute/path/to/this/repo
export COA_ADMIN_API_URL=http://127.0.0.1:8094
# Point Airflow dags_folder at DataOps/airflow/dags (or symlink)
```

Trigger facade with conf:

```json
{ "wf_exec_log_id": "<uuid from Download>" }
```

Details: [`DataOps/airflow/README.md`](DataOps/airflow/README.md).

---

## 9. Stop everything

```bash
npm run local:portals:all:stop
npm run local:middleware:api:all:stop
```

Stop scripts wipe Docker volumes by default — next start re-runs Liquibase on a fresh DB.

---

## 10. Quick troubleshooting

| Symptom | Check |
|---------|--------|
| Admin blank / API errors | `curl :8094/healthz`; `npm run local:middleware:api:all:status` |
| No workflows / sources | Middleware start should have run Liquibase; re-run `bash CICD/Local/knowledge-db-apply.sh` |
| Download 400 `no_store_targets` | Source must map at least one **store_to** endpoint (seeded for GoF) |
| `denied_license` | License must be allowlisted (`DataOps/kb/pipeline/license_gate.py`) |
| SSL errors on extract | `export COA_KB_SSL_INSECURE=1` and re-run facade |
| Ops history stuck `queued` | Facade was never run — step 6 |
| Empty `content.md` | Origin blocked / robots / network; read `wf_exec_log` error on detail page |

---

## Related docs

| Doc | When |
|-----|------|
| [`CICD/Local/README.md`](CICD/Local/README.md) | Containers / middleware scripts |
| [`Portals/admin-portal/README.md`](Portals/admin-portal/README.md) | Admin UI |
| [`DataOps/airflow/README.md`](DataOps/airflow/README.md) | Facade + extract DAGs |
| [`Middleware/API-Services/db/liquibase/knowledge/README.md`](Middleware/API-Services/db/liquibase/knowledge/README.md) | Schema / Liquibase |
| [`Product_Ideas.md`](Product_Ideas.md) | Locked product rules |
