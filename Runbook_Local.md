# Local runbook — Knowledge Base ingest

Goal: run the local stack, queue a **Download** for any allowlisted knowledge source, run the ingest facade, and land Markdown under your local Knowledge Base.

The same path is used as you add more sources over time. Section 4 uses the seeded **DigitalOcean GoF** row as the first walkthrough only.

---

## Table of contents

1. [What this does (one picture)](#1-what-this-does-one-picture)
2. [Prerequisites](#2-prerequisites)
3. [Start the local stack](#3-start-the-local-stack)
4. [Worked example — DigitalOcean GoF](#4-worked-example--digitalocean-gof)
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
npm run local:middleware:api:all:start
npm run local:portals:all:start
```

Middleware start: Postgres + observability → **Liquibase** knowledge changelog → `coa_agents_api` **:8090** + `coa_admin_api` **:8094**.

| URL | What |
|-----|------|
| http://127.0.0.1:4201 | Admin portal |
| http://127.0.0.1:8094/docs | Admin API |
| http://127.0.0.1:4200 | Customer portal (not required here) |

```bash
npm run local:middleware:api:all:status
npm run local:portals:all:status
curl -sf http://127.0.0.1:8094/healthz
```

---

## 4. Worked example — DigitalOcean GoF

First seed used to prove the path end-to-end.

| Field | Value |
|-------|--------|
| Name | DigitalOcean GoF hub |
| Id | `d85e1c09-8157-5565-82d3-f9f3cf209509` |
| URL | https://www.digitalocean.com/community/tutorials/gangs-of-four-gof-design-patterns |
| Workflow | `kb_ingest_facade` |
| Path leaf | `…/software_architecture/patterns/d85e1c09-8157-5565-82d3-f9f3cf209509/` |

In Admin: **Knowledge sources** → **DigitalOcean GoF hub**.

```bash
curl -sf http://127.0.0.1:8094/v1/knowledge/sources/d85e1c09-8157-5565-82d3-f9f3cf209509 | python3 -m json.tool
```

Then continue at [§6 Queue Download](#6-queue-download) with this source id.

---

## 5. Same path for every other source

For Wikipedia, NIST, or any source you add later:

1. Source exists in Admin (seed or create) with URL, allowlisted **license**, **workflow** = `kb_ingest_facade`, and **store_to** (and usually **download_from**) endpoint maps.  
2. Open that source → **Download**.  
3. Run the facade with the new `wf_exec_log_id` ([§7](#7-run-the-ingest-facade)).  
4. Files appear under `{category_code}/{subcategory_code}/{source_uuid}/` ([§8](#8-confirm-files-on-disk)).

List sources:

```bash
curl -sf http://127.0.0.1:8094/v1/knowledge/sources | python3 -m json.tool
```

---

## 6. Queue Download

On the source detail page: **Download — from / store to** → **Download**.

Creates a **`wf_exec_log`** (`queued`) with `wf_id` = the source’s entry workflow. It does **not** fetch the page yet.

```bash
# Example: GoF. Replace SOURCE_UUID for other sources.
curl -sf -X POST \
  http://127.0.0.1:8094/v1/knowledge/sources/SOURCE_UUID/download \
  | python3 -m json.tool
```

Copy `wf_exec_log_id` from the JSON (or from **Ops history**).

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

GoF example:

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
```

Volumes are wiped by default; next start re-applies Liquibase.

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
