# Product Ideas — Pluggable KB Packs & Customer Portal

Captured product and research directions. These are backlog ideas, not committed delivery dates.

## Core verdict

**Pluggable per-domain knowledge banks (KBs)** plus **domain-scoped portal chrome** — not one monolithic KB across all topics.

A single shared KB (entrepreneurship + SRE + fitness + architecture + …) confuses users and pollutes retrieval. Each **domain pack** is a plug: its own corpora, seats, prompts, and (later) RAG tools. The portal makes the active pack obvious so users always know which “brain” they are talking to.

```text
Top menu bar     → domain packs (product lines)
Left nav         → workflows within the active pack only
Main canvas      → chamber chat bound to that pack’s Facilitator + KB
```

Hard rules:

- No cross-pack retrieval.
- Empty packs show **coming soon / KB not loaded** — never silently answer from another pack.
- KB blobs never live in this **public** git repo (laptop or private S3 only).

---

## Portal top menu (build full chrome now)

Visible from the start so product focus is not lost as packs land:

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
3. Other packs next, same ingest pipeline.  
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

Subcats after download (examples): `architecture_styles`, `microservices`, `integration`, `data_modeling`, `enterprise_java`, `cloud_architectures`, `gof_style_patterns` (open explanations only).

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
Overview · Chamber · Sessions · Patterns · Architecture styles · Data & modeling · Knowledge · Seats (Patterns / Architecture / Data)

---

## Chamber chat & context engineering

Session chat: history panel + composer. Context for each turn:

```text
1. Pack system + Facilitator instructions
2. Selected seats’ instructions
3. Retrieved KB chunks (this pack + subcategory filters only)
4. Session summary + last N turns
5. User-selected domain options
6. Current user message (+ optional attach)
```

### Conversation kinds (by pack)

| Pack | Example intents |
|------|-----------------|
| Software Architecture & Design | Pattern fit; design review; monolith vs microservices; data modeling |
| Entrepreneurship | Idea validation; funding path; launch checklist; GTM vs build |
| Leadership | People decision; culture vs delivery; conflict coaching |
| SRE | SLO / error budget; incident review; capacity risk |
| Fitness | Training split; recovery vs intensity (**disclaimer always on**) |

Shared modes: Quick ask · Full council · Single seat · Compare seats.

### Chat options — domain-specific (not generic engineering toolbar)

Universal chrome only: **Send** · **New session** · **Cite sources** (if KB ready) · **Export**.  
All other chips come from **active top menu + left nav**. Switching pack/nav swaps the option set; options must not leak across packs.

#### Software Architecture & Design
| Left nav | Options |
|----------|---------|
| Patterns | Family (creational / structural / behavioral); fit constraint; compare 2 patterns |
| Architecture styles | Style (monolith / modular monolith / microservices / event-driven / serverless); trade-off (latency / team topology / consistency) |
| Data & modeling | Normalization vs access paths; consistency model; schema evolution |
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

**US-oriented authoritative sources first** for Entrepreneurship / Leadership / federal materials. Architecture pack may use major US-hosted open vendor docs (Microsoft Learn, AWS, etc.) under their ToS. Non-US gov portals later as locale packs.

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
  → fetch (robots.txt, rate limit, ETag)
  → license_gate (US gov PD, CC-*, explicit open; deny unknown/ARR)
  → blob store (local FS or S3 — same keys)
  → normalize (HTML/PDF → text)
  → subcategorize (rules / classifier)
  → chunk → embed → pack-scoped index (later)
```

### Storage (locked)

KB content lives in **exactly one** of:

1. **Laptop** — `KB_LOCAL_ROOT` (prefer **outside** the git clone)  
2. **Private AWS S3** — `KB_BLOB_BACKEND=s3`, `KB_S3_BUCKET`

```text
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
- Early target: **thousands of chunks** per pack after section split.  
- Program for scale; seed from authoritative allowlists; grow honestly.

### Subcategorize after download

Fetch into the domain first; label subcats offline (URL/title rules + optional classifier); re-tag without re-download; retrieve with `domain + subcategory` only.

---

## Suggested build order

1. Document (this file) — done as living product IA.  
2. Portal shell: five top menus + left-nav configs + coming-soon states.  
3. Ingest v0: local blob store + license gate + Architecture allowlist.  
4. Chamber options for Architecture left-nav sections.  
5. Wire RAG retrieval pack-scoped.  
6. Entrepreneurship (SBA) → Leadership → SRE → Fitness packs.  
7. Optional S3 backend with same keys.

---

## Notes

- Observability (`coa_observability_api`) should later label retrieval hits (corpus id, subcategory, latency) like LLM calls.  
- This file records **ideas and locked product decisions**, not a promise of implementation order beyond the suggested sequence above.
