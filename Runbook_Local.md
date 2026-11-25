# Local runbook — Knowledge Base ingest

Goal: run the local stack, use the **Admin UI** to queue **Download** on an allowlisted knowledge source, run the ingest facade, and land Markdown under your local Knowledge Base.

**First source to run:** the seeded **DigitalOcean GoF** hub (§4). After that, every other source uses the same Admin → Download → facade path (§5+).

---

## Table of contents

1. [What this does (one picture)](#1-what-this-does-one-picture)
2. [Prerequisites](#2-prerequisites)
3. [Start the local stack](#3-start-the-local-stack)
4. [First source — DigitalOcean GoF](#4-first-source--digitalocean-gof)
5. [Same path for every other source](#5-same-path-for-every-other-source)
6. [Queue Download](#6-queue-download)
7. [Run the ingest facade](#7-run-the-ingest-facade)
8. [Confirm files on disk](#8-confirm-files-on-disk)
9. [Optional — Airflow](#9-optional--airflow)
10. [Stop everything](#10-stop-everything)
11. [Quick troubleshooting](#11-quick-troubleshooting)

---

## 1. What this does (one picture)

```text
Admin UI  →  coa_admin_api  →  wf_exec_log (queued)
                                    ↓
                         kb_ingest_facade  (entry workflow in DB)
                                    ↓
                         kb_extract        (internal step / DAG)
                                    ↓
              $HOME/.../KnowledgeBase/{category}/{subcategory}/{source_uuid}/
                 content.md   meta.json   original.html
```

| Piece | Role |
|-------|------|
| **Source** | Allowlisted row: URL, license, category, **workflow_id**, endpoint maps |
| **Workflow** | Entry facades only in `knowledge.workflow` (seed: `kb_ingest_facade`) |
| **`wf_exec_log`** | One row per Download (`wf_id` = that facade) |
| **Extract** | Internal to the facade — not a Workflows-table row |

You grow the KB by adding more **sources** (same facade). You do not invent a new runbook per URL.

---

## 2. Prerequisites

| Need | Notes |
|------|--------|
| Docker Desktop | Running |
| `uv` | `uv sync` from repo root |
| `psql` | On PATH (middleware start waits on Postgres / Liquibase) |
| Node / npm | Portals |
| Repo clone | Run all commands from repo root |

---

## 3. Start the local stack

```bash
uv sync
npm run local:containers:all:start
npm run local:middleware:api:all:start
npm run local:portals:all:start
```

Containers hold DB/Redis (leave up). Middleware/portals are host processes — restart anytime without stopping containers.

| URL | What |
|-----|------|
| http://127.0.0.1:4201 | Admin portal |
| http://127.0.0.1:8094/docs | Admin API |

```bash
npm run local:containers:all:status
npm run local:middleware:api:all:status
npm run local:portals:all:status
curl -sf http://127.0.0.1:8094/healthz
```

---

## 4. First source — DigitalOcean GoF

This is the **first real ingest**, not a toy demo. Liquibase seeds this row; you drive it from the **Admin UI**.

| Field | Value |
|-------|--------|
| Name | DigitalOcean GoF hub |
| Id | `d85e1c09-8157-5565-82d3-f9f3cf209509` |
| URL | https://www.digitalocean.com/community/tutorials/gangs-of-four-gof-design-patterns |
| Workflow | `kb_ingest_facade` |
| Path leaf | `…/software_architecture/patterns/d85e1c09-8157-5565-82d3-f9f3cf209509/` |

1. Open http://127.0.0.1:4201 → **Knowledge sources**.  
2. Open **DigitalOcean GoF hub**.  
3. On the detail page, confirm:

| UI field | Expected |
|----------|----------|
| **URL** | `https://www.digitalocean.com/community/tutorials/gangs-of-four-gof-design-patterns` |
| **Download workflow** | `kb_ingest_facade` |
| **Downloaded from** | **DigitalOcean community (origin)** |
| **Stored as** | Must include **COA KnowledgeBase (local datasets)** (required for local ingest). Seed may also list AWS S3 / Azure Blob — those are optional for this run. |

4. Continue at [§6 Queue Download](#6-queue-download) (use the **Download** button on that page).

---

## 5. Same path for every other source

After GoF lands, Wikipedia, NIST, or any source you add later follows the **same Admin UI path**:

1. Source exists in Admin (seed or create) with URL, allowlisted **license**, **workflow** = `kb_ingest_facade`, and **store_to** (and usually **download_from**) endpoint maps.  
2. **Knowledge sources** → open that source → **Download**.  
3. Run the facade with the new `wf_exec_log_id` ([§7](#7-run-the-ingest-facade)).  
4. Files appear under `{category_code}/{subcategory_code}/{source_uuid}/` ([§8](#8-confirm-files-on-disk)).

---

## 6. Queue Download

**Primary: Admin UI**

On the source detail page: **Download — from / store to** → **Download**.

Creates a **`wf_exec_log`** (`queued`) with `wf_id` = the source’s entry workflow. It does **not** fetch the page yet.

Copy `wf_exec_log_id` from **Ops history** on that page (needed for §7).

---

## 7. Run the ingest facade

Same command for every source — only the exec id changes.

```bash
export PYTHONPATH=.
export COA_ADMIN_API_URL=http://127.0.0.1:8094

uv run python -c "
from DataOps.kb.pipeline.facade_runner import run_ingest_facade
print(run_ingest_facade('PASTE_WF_EXEC_LOG_ID_HERE'))
"
```

Steps: license/robots gate → URL → Markdown → write UUID leaf → PATCH `wf_exec_log` (`completed` / `failed`).

Refresh source → **Ops history** → **completed**.

---

## 8. Confirm files on disk

```text
$HOME/runtime_data/apps/datasets/COA/KnowledgeBase/
  {category_code}/{subcategory_code}/{source_uuid}/
    content.md
    meta.json
    original.html
```

GoF leaf (first source):

```bash
SRC=d85e1c09-8157-5565-82d3-f9f3cf209509
DIR="$HOME/runtime_data/apps/datasets/COA/KnowledgeBase/software_architecture/patterns/$SRC"
ls -la "$DIR"
head -40 "$DIR/content.md"
```

Override root with `KB_LOCAL_ROOT` if needed. **Never commit** KB files (public repo).

---

## 9. Optional — Airflow

| DAG id | In Workflows table? | Job |
|--------|---------------------|-----|
| `kb_ingest_facade` | Yes | Gate → extract → PATCH log |
| `kb_extract` | No | URL → Markdown |

```bash
export PYTHONPATH=/absolute/path/to/this/repo
export COA_ADMIN_API_URL=http://127.0.0.1:8094
# dags_folder → DataOps/airflow/dags
```

Trigger conf: `{ "wf_exec_log_id": "<uuid>" }`. See [`DataOps/airflow/README.md`](DataOps/airflow/README.md).

---

## 10. Stop everything

```bash
npm run local:portals:all:stop
npm run local:middleware:api:all:stop
npm run local:containers:all:stop
```

Omit `containers:all:stop` if you only want to bounce APIs (DB stays).

---

## 11. Quick troubleshooting

| Symptom | Check |
|---------|--------|
| Admin / API down | `curl :8094/healthz`; middleware status |
| No sources / workflows | Re-run `bash CICD/Local/knowledge-db-apply.sh` |
| Download 400 `no_store_targets` | Map at least one **store_to** endpoint |
| `denied_license` | License in `DataOps/kb/pipeline/license_gate.py` |
| SSL verify failed on extract | In **that** shell only: `export COA_KB_SSL_INSECURE=1` then re-run §7 (not needed for `npm run`) |
| Ops history stuck `queued` | Facade not run — §7 |
| Empty / bad `content.md` | Origin / robots / network; read exec error on detail |

---

## Related docs

| Doc | When |
|-----|------|
| [`CICD/Local/README.md`](CICD/Local/README.md) | Containers / middleware |
| [`Portals/admin-portal/README.md`](Portals/admin-portal/README.md) | Admin UI |
| [`DataOps/airflow/README.md`](DataOps/airflow/README.md) | Facade + extract DAGs |
| [`Middleware/API-Services/db/liquibase/knowledge/README.md`](Middleware/API-Services/db/liquibase/knowledge/README.md) | Schema / Liquibase |
| [`Product_Ideas.md`](Product_Ideas.md) | Locked product rules |
