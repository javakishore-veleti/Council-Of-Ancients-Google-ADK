# Product Ideas — Pluggable KB Topics & Customer Portal

Captured product and research directions. These are backlog ideas, not committed delivery dates.

## Core verdict

**Pluggable per-domain knowledge banks (KBs)** plus **domain-scoped portal chrome** — not one monolithic KB across all topics.

A single shared KB (entrepreneurship + SRE + fitness + architecture + …) confuses users and pollutes retrieval. Each **topic** is a plug: its own corpora, seats, prompts, and (later) RAG tools. The portal makes the active topic obvious so users always know which “brain” they are talking to.

```text
Top menu bar     → topics (product lines) + Account / Settings
Left nav         → workflows within the active topic only (+ Settings)
Main canvas      → chamber chat project / window bound to that topic’s Facilitator + KB
```

No permanent right-hand “context/debug” rail — it cramps the chamber and feels too technical for customers. Citations/sources surface inside the chamber thread when KB retrieval returns them.

Hard rules:

- No cross-topic retrieval.
- Empty topics show **coming soon / KB not loaded** — never silently answer from another topic.
- KB blobs never live in this **public** git repo (laptop or private S3 only).

---

## Portal UI shell (locked)

**Chat-first two-column app** (top bar + left nav + full canvas), not a dashboard/widget admin template.

```text
┌─────────────────────────────────────────────────────────────┐
│ Brand + council definition │ topics… │ Account               │
├──────────┬──────────────────────────────────────────────────┤
│ Left nav │  Chamber / overview — full width canvas          │
│ (topic)  │  history + chips + composer                      │
└──────────┴──────────────────────────────────────────────────┘
```

| Region | Role |
|--------|------|
| **Top bar** | Large **Council of Ancients** mark; professor-hat icon opens “what is a council?”; five topics; **Global Settings**; Sign in / Sign out |
| **Left nav** | Topic-specific list (below); **Settings** = defaults for the active top-menu topic |
| **Center** | Full-width chat **projects** / **windows** with history + domain chips + composer |

Two-column shell (top + left + canvas). Do **not** make a multi-widget analytics home or a floating AI bubble the primary surface.

Angular app lives under `Portals/`. v0: Architecture chamber live; other topics chrome + coming soon.

---

## Auth, customer, and settings (locked)

### Services (separate FastAPI apps)

| Service | Role | Local port (proposed) | Postgres schema |
|---------|------|----------------------|-----------------|
| `coa_auth_api` | Signup, signin, signout, tokens/sessions only | `:8091` | `auth` |
| `coa_customer_api` | Customer create/update, global + topic prefs, chat projects, chat overrides, history index | `:8092` | `customer` |
| `coa_agents_api` | Council `POST /v1/council/deliberate` | `:8090` | `agents` |
| `coa_observability_api` | LLMOps ingest | `:8088` | `observability` |
| `coa_knowledge_api` | Knowledge Bank: `knowledge_category` + `knowledge_source` CRUD (indexing registry) | `:8093` | `knowledge` |
| `coa_admin_api` | Admin BFF — only backend the Admin UI calls; proxies Knowledge + triggers ingest async | `:8094` | `admin` |

Existing agents/obs APIs stay; auth, customer, knowledge, and admin are **new** peers under `Middleware/API-Services/`. Preferences do **not** live inside `coa_agents_api`.

### Admin ingest path (locked)

```text
Admin UI "Queue download"
  → coa_admin_api creates wf_exec_log (status=queued, UUID pk)
  → triggers Airflow **facade** DAG today (AWS Step Functions later) with wf_exec_log.id
  → facade patches wf_exec_log (started / running / completed / failed)
```

Admin UI never talks to Airflow / Step Functions or Knowledge API directly.

**Workflows registry (locked):** `knowledge.workflow` rows (name, description, **engine**, external_ref, status). Engine is open-ended (`airflow`, `step_functions`, `emr`, `spring_batch`, `local`, …). Admin has **Workflows** list + detail (criteria + searchable columns).

- Each `knowledge_source.workflow_id` points at the workflow used on **Download**.
- Each `wf_exec_log.wf_id` stores that workflow’s primary key at queue time (plus denormalized `engine`).

**Facade vs extract (locked):** Admin only triggers the source’s registered **facade** workflow (seed: `kb_ingest_facade`). That workflow is **not** an extractor — it orchestrates one download run and **invokes** extract (`kb_extract`). Extract is swappable without changing Admin or `wf_exec_log`.

```text
Download → source.workflow_id → create wf_exec_log(wf_id=…)
kb_ingest_facade (wf_exec_log.id)
  → load source + license/robots gate
  → trigger kb_extract (url, store_dir, strategy)
  → finalize store under UUID leaf + PATCH wf_exec_log
```

**`wf_exec_log` (ops history):** one row per download/index run. Source detail → **Ops history** accordion. Fields include source_id, engine (`airflow` | `step_functions` | `local`), external_run_id, status, download_from / store_to / tech_stack endpoint ids, timestamps, error/detail.

### App Endpoints (locked)

Configurable dependency targets — **not** vector-DB-only. Examples: local Postgres, local Chroma, local Postgres+pgvector, AWS / Azure / GCP services, HTTP origins, object stores, search, queues, or any other 3rd party.

- Created/managed under **App Endpoints** in Admin.
- A **knowledge source** maps:
  - **download from** — one origin endpoint
  - **store to** — one or more endpoints (same content fans out)
  - **tech stack** — endpoints used after ingest (indexes / DBs / clouds)
- Listing has no Download; Download lives on the **source detail** page.

**Local download base (default store-to):**

```text
$HOME/runtime_data/apps/datasets/COA/KnowledgeBase/
  {category_code}/{subcategory_code}/{source_uuid}/   # no spaces; UUID leaf
```

Example: `…/KnowledgeBase/architecture/patterns/d85e1c09-8157-5565-82d3-f9f3cf209509/`.

**Identity:** primary key is a UUID stored as a string (`id`) — URLs, FKs, store-path leaves.

### Knowledge Bank tables (locked)

- **`knowledge_category`** — top-nav topics are roots (`parent_id` NULL); left-nav sections are children of a topic. Same table, parent/child. Stable `code` matches portal ids (`software_architecture`, `styles`, …).
- **`knowledge_source`** — allowlisted corpus row. **`name`** is the unique business / lookup key; **`citation_name`** and **`citation_desc`** are what indexing and the chamber use when citing a hit. FK → `knowledge_category`.

### Settings layers (later wins)

1. **Global (per user)** — defaults in customer-service (tone, cite-sources default, last topic, UI prefs, Fitness disclaimer ack, …).  
2. **Topic (top menu)** — overrides for that domain (default seats, preferred left-nav section, …).  
3. **Chat project / chat window** — overrides for that conversation only (domain chips, seat focus, cite on/off). History attaches here.

Left-nav selection drives domain option chips; when the user changes them, store as **chat-window overrides**.

### What the portal sends to the council API

Each Send → existing deliberate body:

```json
{
  "session_id": "<chat_window_id>",
  "user_id": "<customer_id>",
  "message": "<composer text>",
  "ctx_data": {
    "topic_id": "software_architecture",
    "left_nav": "patterns",
    "domain_options": {},
    "lenses": ["startup_cto", "developer"],
    "mode": "balanced",
    "settings": {},
    "chat_project_id": "...",
    "recent_turns": []
  }
}
```

`settings` is the **merged** global → topic → chat override map. Transcript index lives in customer-service; ADK session continuity uses `session_id`.

---

## Neal Ford API shape + Postgres / Liquibase (locked)

Every stateful API follows:

```text
presentation/     FastAPI routes + Pydantic (thin HTTP)
application/      Facade(s) — orchestration only; no SQL
infrastructure/   DAO(s) — SQL against this service’s schema only
domain/           models, errors, toggles
```

```text
API route → Facade → DAO → postgres.<service_schema>
```

(Observability: API → Facade → tasks → sub-facades → plugins. Knowledge Bank: API → Facade → tasks → sub-facades → DAO. Auth/customer follow the same Facade → tasks → DAO shape for CRUD.)

### Database

- Local container already in `CICD/Local` (`--postgres`): DB **`council`**, user/password **`postgres` / `postgres`**, port **`5432`**.  
- **One shared DB**, **one dedicated schema per API** (`auth`, `customer`, `agents`, `observability`, `knowledge`). No shared tables across services; cross-service refs are opaque IDs.

### Liquibase (outside Python packages)

Schema management is **not** Alembic inside each app. Dedicated tree, e.g. `Middleware/API-Services/db/liquibase/` with per-service changelogs. Migrate against `postgresql://postgres:postgres@localhost:5432/council` before middleware APIs start. App packages consume schemas; they do not own migration files.

---

## Portal top menu (build full chrome now)

Visible from the start so product focus is not lost as topics land:

1. **Entrepreneurship**
2. **Leadership**
3. **SRE**
4. **Fitness**
5. **Software Architecture & Design**

KB depth fills in behind each item over time. Nav discovery is complete early; content is progressive.

### Progressive content rollout

| Stage | Top menu | KB behind it |
|-------|----------|--------------|
| **v0** | All five menus visible | Only **Software Architecture & Design** loaded (laptop) |
| **v1+** | Same menus | Enable Entrepreneurship, Leadership, SRE, Fitness as each KB lands |

---

## What to build first

1. **Storage: laptop local first** (`KB_LOCAL_ROOT`), not S3.  
2. **First KB: Software Architecture & Design** — dense technical corpora; faster useful chamber than a full SBA crawl.  
3. Other topics next, same ingest pipeline.  
4. Portal shell with all five top menus + left-nav configs; wire chamber only where `kbReady`.

### Software Architecture & Design — source caution

Named classics (GoF, many J2EE / architecture pattern books) are **copyrighted**. Do **not** ingest full book PDFs without a license.

| Family | In KB as full text? | Approach |
|--------|---------------------|----------|
| Gang of Four *Design Patterns* | No | Cite / link; prompts may name patterns |
| Commercial architecture / J2EE pattern books | No | Reading list only |
| Microservices pattern books | Prefer not | Prefer open vendor docs |
| Codd / relational theory books | Partial | Prefer open DB docs + OA |
| **v0 open spines** | **Yes** | Microsoft Learn, Azure Architecture Center, AWS Architecture Center / Well-Architected (per ToS), PostgreSQL/MySQL/MariaDB docs, Jakarta EE docs (check license), OA architecture papers, relevant NIST/IT guidance |

Subcats after download (examples): `architecture_styles`, `microservices`, `integration`, `data_modeling`, `enterprise_java`, `cloud_architectures`, `databases_storage`, `event_systems`, `ai_agentic`, `gof_style_patterns` (open explanations only).

MCP for external agents is a **later** second interface on the same structured store — not a v0 dependency. GraphRAG / compatibility tools after topic-scoped retrieval works in the chamber.

---

## Starter left nav (per top menu)

Shared spine (learn once):

- Overview  
- Chamber  
- Sessions  
- Knowledge (disabled until KB ready)  
- Seats  
- Guides (optional)

### Entrepreneurship
Overview · Chamber · Sessions · Plan & launch · Fund & grow · Knowledge · Seats (Vision / Capital / Execution)

### Leadership
Overview · Chamber · Sessions · People & culture · Decisions · Knowledge · Seats (People / Culture / Judgment)

### SRE
Overview · Chamber · Sessions · Reliability · Incidents & postmortems · Knowledge · Seats (Reliability / Capacity / Response)

### Fitness
Overview · Chamber · Sessions · Training · Nutrition & recovery · Knowledge · Seats (Training / Nutrition / Recovery) · **Disclaimer** (not medical advice)

### Software Architecture & Design *(first KB)*

Workflow / domain pillars (not textbook chapters). **Role is never mandatory** — optional curated “start here” hubs later; primary spine is problem layers:

Overview · Chamber · Sessions · Patterns · Architecture styles · Data & modeling · **Cloud & infrastructure** · **Databases & storage** · **Event systems** · **AI & agentic systems** · Knowledge · Seats (Patterns / Architecture / Data) · Settings

Cross-link topics later with `pairs_with` / `conflicts_with` metadata (admin ingest). Customer portal only consumes structured entries.

---

## Chamber chat & context engineering

Session chat: history panel + composer. Context for each turn:

```text
1. Topic system + Facilitator instructions
2. Selected seats’ instructions
3. Retrieved KB chunks (this topic + subcategory filters only)
4. Session summary + last N turns
5. User-selected domain options (from left nav)
6. Optional chat lenses + mode (deep_think | balanced)
7. Current user message (+ optional attach)
```

### Chat lenses (optional, multi-select in composer — **per topic**)

Never force a job-title wall. Default = **no lenses**. Lenses swap with the **active top menu**; they must not leak Architecture personas into Entrepreneurship (etc.).

| Topic | Example lenses |
|------|----------------|
| Software Architecture & Design | Aspiring · Developer · Startup CTO · Enterprise · Coding agent |
| Entrepreneurship | Founder · Operator · Investor lens · First-time founder |
| Leadership | IC · Manager · Exec · People partner |
| SRE | On-call · SRE lead · Platform · Exec risk |
| Fitness | Beginner · Intermediate · Coach lens |

Plus **Deep think** toggle → `mode: deep_think`. Domain option chips still come from **left nav** for that topic only.

Admin KB entries should eventually support facet blocks filtered by lenses; v0 UI sends topic-scoped `lenses` in `ctx_data` even before facets land.

### Conversation kinds (by topic)

| Topic | Example intents |
|------|-----------------|
| Software Architecture & Design | Pattern fit; design review; monolith vs microservices; data modeling |
| Entrepreneurship | Idea validation; funding path; launch checklist; GTM vs build |
| Leadership | People decision; culture vs delivery; conflict coaching |
| SRE | SLO / error budget; incident review; capacity risk |
| Fitness | Training split; recovery vs intensity (**disclaimer always on**) |

Shared modes: Quick ask · Full council · Single seat · Compare seats.

### Chat options — domain-specific (not generic engineering toolbar)

Universal chrome only: **Send** · **New session** · **Cite sources** (if KB ready) · **Export**.  
All other chips come from **active top menu + left nav**. Switching topic/nav swaps the option set; options must not leak across topics.

#### Software Architecture & Design
| Left nav | Options |
|----------|---------|
| Patterns | Family (creational / structural / behavioral / resilience); compare 2 patterns |
| Architecture styles | Style (monolith / modular monolith / microservices / event-driven / serverless) |
| Data & modeling | Normalization vs access; consistency; schema evolution |
| Cloud & infrastructure | K8s vs serverless; multi-region; IaC |
| Databases & storage | OLTP vs OLAP; sharding; CAP trade-offs |
| Event systems | Pub/sub vs queue; streaming; idempotency / DLQ |
| AI & agentic systems | Orchestration; hybrid RAG; evals / guardrails |
| Chamber / Overview | Full council vs single seat (Patterns / Architecture / Data) |
| Knowledge | Subcategory browse filter only |

#### Entrepreneurship
| Left nav | Options |
|----------|---------|
| Plan & launch | Stage (idea / validate / launch); setup focus; risk lens |
| Fund & grow | Capital path (bootstrapped / debt / equity); use-of-funds; milestone |
| Chamber | Seats: Vision / Capital / Execution |

#### Leadership
| Left nav | Options |
|----------|---------|
| People & culture | Stakeholder (IC / manager / skip / exec); conflict type |
| Decisions | Time horizon; reversible vs one-way door |
| Chamber | Seats: People / Culture / Judgment |

#### SRE
| Left nav | Options |
|----------|---------|
| Reliability | SLO class; error-budget policy; customer impact |
| Incidents & postmortems | Severity; phase (detect / mitigate / review) |
| Chamber | Seats: Reliability / Capacity / Response |

#### Fitness
| Left nav | Options |
|----------|---------|
| Training | Goal (strength / endurance / mobility); experience level |
| Nutrition & recovery | Time / equipment constraints — **no medical diagnosis** |
| Chamber | Seats + mandatory disclaimer |

History panel: rename/archive session, pin/copy/export, show sources, regenerate with different seat focus (later).

---

## Geographic scope

**US-oriented authoritative sources first** for Entrepreneurship / Leadership / federal materials. Architecture topic may use major US-hosted open vendor docs (Microsoft Learn, AWS, etc.) under their ToS. Non-US gov portals later as locale topics.

---

## Authoritative sources only (no self-authored KB lore)

The KB must be grounded in **authentic, citable sources**. Operator-written dilemma cards / playbooks are **not** KB corpus (UI scenarios can exist later without pretending to be the bank).

### Entrepreneurship (US) — where to look

| Source type | Where | Notes |
|-------------|-------|--------|
| Federal small-business guides | [SBA.gov](https://www.sba.gov) | Primary spine |
| Federal innovation / R&D | NIST MEP, USPTO, NSF SBIR/STTR public pages | |
| Commerce / labor stats | Census, BEA, BLS | Structured facts |
| US open textbooks / OCW | OpenStax, Open Textbook Library, MIT OCW (open/CC only) | |
| OA research | PMC, DOAJ, arXiv, SSRN when allowed | |
| VC blogs | YC / a16z / First Round | **Not primary KB** unless license allows |

**Priority:** SBA → NIST/USPTO/SBIR → Census/BLS/BEA → OpenStax/OCW → OA.

#### How SBA provides content (not by year)

SBA is a **living site by business lifecycle**, not yearly editions (2024/2025/2027 kits):

1. Plan your business  
2. Launch your business  
3. Manage your business  
4. Grow your business  

Sitemap `post-sitemap*.xml` files are CMS URL batches, **not** year curricula. Ingest the Business Guide trees; store `fetched_at` / etag; subcategorize after download.

### Leadership (US) — where to look

| Source type | Where | Notes |
|-------------|-------|--------|
| Federal civilian leadership | OPM competencies / HR University public materials | |
| Federal labor / management | DOL public guides | Not legal advice |
| Public-release military doctrine | Army/DoD pubs stamped public release | Verify distribution |
| Open textbooks / OCW / OA | OpenStax OB, MIT OCW open parts, PMC/DOAJ | |
| HBS / HBR full text | Out of KB | Links only |

**Priority:** OPM → DOL → public-release DoD/Army → OpenStax/OCW → OA.

### Excluded from KB corpus

- Self-authored playbooks / dilemma cards as “sources”  
- Commercial bestsellers; HBR/WSJ/NYT full text  
- Pirate “free PDF” sites  
- Scraped Medium/Substack/VC blogs without explicit license  

---

## Ingest pipeline (local laptop → private S3)

```text
sources registry (url, license, domain, status)
  → kb_ingest_facade (Airflow)
       → license_gate + robots
       → kb_extract (swappable strategy: default generic_markdown)
       → store content.md + meta.json (+ original.html when cheap)
  → subcategorize (rules / classifier) — later
  → chunk → embed → topic-scoped index (later)
```

### Extract strategies (locked)

- Extract is **URL-agnostic**: any allowlisted `knowledge_source.url` — not a DigitalOcean-only parser.
- Default strategy: **`generic_markdown`** — HTTP fetch → strip chrome → clean Markdown for RAG.
- Optional **host extractors** (sparse, later): registry by host/path when structured fields matter; always still emit Markdown.
- Facade triggers extract by strategy id / extract DAG id so vendors or local libs can be swapped without rewriting the facade.
- No multi-page Crawl/Map on single-source Download (v1). No hard dependency on a third-party scrape SaaS.

### Storage (locked)

KB content lives in **exactly one** of:

1. **Laptop** — `KB_LOCAL_ROOT` (prefer **outside** the git clone); default App Endpoint leaf is UUID under KnowledgeBase  
2. **Private AWS S3** — `KB_BLOB_BACKEND=s3`, `KB_S3_BUCKET`

```text
# Preferred (Admin App Endpoint / source UUID leaf)
KnowledgeBase/{category_code}/{subcategory_code}/{source_uuid}/
  content.md
  meta.json
  original.html   # optional

# Legacy topic layout (still supported by pipeline helpers)
kb/
  raw/{domain}/{source_id}/original.*
  raw/{domain}/{source_id}/meta.json
  text/{domain}/{source_id}/content.md
  derived/{domain}/{source_id}/subcats.json
```

### Public repo rule (locked)

This repository is **public**. Never commit downloaded KB files. Commit only ingest code, allowlists, license-gate logic, and docs. Gitignore any accidental `data/kb/`.

### Scale expectations

- SBA/OPM-class feeds alone → **hundreds** of pages, not 10k URLs each.  
- **Thousands–10k+** needs broad OA harvest under license gates.  
- Early target: **thousands of chunks** per topic after section split.  
- Program for scale; seed from authoritative allowlists; grow honestly.

### Subcategorize after download

Fetch into the domain first; label subcats offline (URL/title rules + optional classifier); re-tag without re-download; retrieve with `domain + subcategory` only.

---

## Suggested build order

1. Document (this file) — living product IA (including UI / auth / DB notes below).  
2. Liquibase schemas + local Postgres migrate; scaffold `coa_auth_api` + `coa_customer_api` (Neal Ford + DAO).  
3. Angular portal: signup/signin, five top menus, left-nav, Architecture chamber, settings merge → deliberate.  
4. Ingest v0: local blob store + license gate + Architecture allowlist.  
5. Chamber options for Architecture left-nav sections.  
6. Wire RAG retrieval topic-scoped.  
7. Entrepreneurship (SBA) → Leadership → SRE → Fitness topics.  
8. Optional S3 backend with same keys.

---

## Notes

- Observability (`coa_observability_api`) should later label retrieval hits (corpus id, subcategory, latency) like LLM calls.  
- v0 auth is email+password tokens; OAuth/SSO later. Agents may trust portal-supplied `user_id` first; JWT validation on agents later.  
- This file records **ideas and locked product decisions**, not a promise of implementation order beyond the suggested sequence above.
