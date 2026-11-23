# Council-Of-Ancients-Google-ADK

Multi-agent Council of Ancients built with Google Agent Development Kit (ADK), Vertex AI, and Model Armor — with Middleware agents, API services, Angular portals, and GitHub Actions for GCP setup.

**Council** means a small board that deliberates together instead of one assistant hedging alone: a neutral Facilitator chairs the room and specialists argue in parallel before a shared verdict. **Ancients** points at classic intellectual lineages—voices that still shape how people argue about ethics, certainty, and power—not literal undead advisors.

The three counselors are standing roles in that debate. **Plato** (classical Athens) pushes virtue, justice, and the good of the wider community. **René Descartes** (early modern Europe) applies methodical doubt and asks what can be established from first principles. **Niccolò Machiavelli** (Renaissance Florence) focuses on incentives, power, and what holds up in practice. Together they give opposing lenses on the same dilemma so the Facilitator can synthesize a clearer recommendation.

| | |
|--|--|
| **Useful for** | Hard decisions where a single chatbot would hedge—“on one hand / on the other.” (*Hedge* here means staying non-committal and avoiding a clear recommendation.) The Council forces structured disagreement (ethics vs proof vs power), then a Facilitator synthesis with a recommended action. |
| **Who uses it** | Founders and operators on strategy/ethics trade-offs; product and eng leads on ship-vs-risk calls; policy, trust & safety, or compliance reviewers stress-testing a stance; coaches/advisors rehearsing a dilemma; developers learning multi-agent ADK patterns. |
| **How they interact** | Ask the Facilitator in natural language (portal, ADK web, or API). Casual greetings get a short reply; real dilemmas run parallel openings, rebuttals, and a council verdict. |

| Counselor | Lens | Benefit to the user |
|-----------|------|---------------------|
| **Plato** | Virtue, justice, wider community | Surfaces who else is affected and whether the “winning” option still looks fair when stakeholders are included. |
| **René Descartes** | Doubt, first principles, what is proven | Challenges shaky assumptions, missing evidence, and leaps of faith before you commit. |
| **Niccolò Machiavelli** | Power, incentives, what works in practice | Stress-tests politics, leverage, and second-order consequences so the plan survives contact with reality. |
| **Facilitator** (chair) | Neutral synthesis | Turns three sharp angles into one readable verdict: convergence, tensions, and a concrete recommended action. |

## Table of contents

1. [Layout](#layout)
2. [How the Council agents work](#how-the-council-agents-work)
3. [Local infrastructure](#local-infrastructure)
4. [GitHub Actions secrets to configure](#github-actions-secrets-to-configure)
5. [What the three GCP setup workflows do](#what-the-three-gcp-setup-workflows-do)
   - [GCP-001 / GCP-002 / GCP-003 summary table](#what-the-three-gcp-setup-workflows-do)
   - [Workflow files (setup & destroy)](#workflow-files-setup--destroy)
6. [GCP setup from zero (developer guide)](#gcp-setup-from-zero-developer-guide)
7. [After GCP setup — local `.env`](#after-gcp-setup--local-env)
8. [Hands-on coding](#hands-on-coding)
9. [Future work (GitHub issues)](#future-work-github-issues)
10. [More detail](#more-detail)
11. [Workflows deep dive](.github/workflows/README.md#github-actions-secrets-to-configure)
12. [References](#references)

## Layout

| Path | Role |
|------|------|
| `Middleware/Agents/` | ADK agents (Facilitator + counselors) |
| `Middleware/API-Services/` | FastAPI / ADK runtime APIs |
| `Portals/` | Angular portals |
| `CICD/Local/` | Local Docker infra (Redis, Jaeger, optional Postgres) |
| `CICD/GCP/` | Scripts + templates used by the GCP GitHub Actions |
| `.github/workflows/` | Manual GCP setup / destroy workflows |
| [`HandsOn_GCP_Agents.md`](HandsOn_GCP_Agents.md) | Step-by-step coding lab (type the snippets yourself) |

## How the Council agents work

### What users type

Users talk to the **Facilitator**, not to Plato / Descartes / Machiavelli directly.

| Example prompt | Expected behavior |
|----------------|-------------------|
| `hello` / `who is on the council?` | Facilitator answers alone (no sub-agents) |
| `Should I leave my job for a risky startup?` | Full debate: opening → rebuttal → synthesis |
| `Should we prioritize growth or profitability?` | Same debate protocol |
| `Is it ethical to use customer data to train a model?` | Same debate protocol |

Users usually do **not** say “ask Plato.” The Facilitator decides when to call sub-agents.

### Knowledge base vs model prompts

| Piece | What it uses today (blog / MVP design) |
|-------|----------------------------------------|
| Facilitator | `static_instruction` = triage + debate rules |
| Plato / Descartes / Machiavelli | `static_instruction` = persona + how to argue + **Gemini pretrained knowledge** |
| Tools / DB / RAG | **None** unless you add them later |
| Model Armor | Screens prompts and replies (not a knowledge source) |

So the MVP is **structured multi-agent prompting** on Gemini — not random free-chat, and **not** a curated corpus of The Republic / Discourse / The Prince until a RAG epic lands.

```text
User dilemma
    → Facilitator (orchestrator prompt)
        → Plato (ethics prompt)      ─┐
        → Descartes (doubt prompt)   ├─ parallel single_turn calls
        → Machiavelli (power prompt) ─┘
    → Facilitator synthesis
```

Same idea as the ADK tool loop: the model requests work; your app runs sub-agents like tools; the model answers with those results.

### Making it “meatier” later

Tracked as GitHub **epics/features** below: RAG over texts or company docs, real tools (CRM/metrics), eval sets, Angular portal, durable Cloud Run sessions.

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

## GitHub Actions secrets to configure

Before any `GCP-00x-*` workflow can run, add these **repository** (or organization) secrets:

**GitHub path:** repo → **Settings → Secrets and variables → Actions → New repository secret**

| Secret name | What to put | Example shape (not real values) |
|-------------|-------------|-------------------------------|
| `GCP_PROJECT_ID` | Your Google Cloud **project ID** | `my-council-project` |
| `GCP_SERVICE_ACCOUNT` | Email of the **deployer** SA used by Actions (WIF impersonation target) | `github-actions-gcp-deployer@my-council-project.iam.gserviceaccount.com` |
| `GCP_WORKLOAD_IDENTITY_PROVIDER` | Full WIF **provider resource name** | `projects/123456789012/locations/global/workloadIdentityPools/github-actions/providers/github` |

| Secret | Used by | Notes |
|--------|---------|--------|
| `GCP_PROJECT_ID` | All `GCP-00x-*` workflows | Same value as `GOOGLE_CLOUD_PROJECT` in local `.env` |
| `GCP_SERVICE_ACCOUNT` | Auth step (`.github/actions/gcp-auth`) | **Not** the runtime `council-of-ancients-sa` |
| `GCP_WORKLOAD_IDENTITY_PROVIDER` | Auth step (OIDC / WIF) | No JSON key file; create pool/provider in Console first |

How to create the deployer SA + WIF pool: [Step 3–6 in the developer guide](#step-3--create-the-github-actions-deployer-service-account).  
Same table in [`.github/workflows/README.md`](.github/workflows/README.md#github-actions-secrets-to-configure).

## What the three GCP setup workflows do

| Workflow | What it does |
|----------|----------------|
| **[GCP-001-Setup-APIs](.github/workflows/GCP-001-Setup-APIs.yml)** | Enables Vertex AI, Model Armor, Cloud Run, Cloud Build, and IAM APIs on your project. |
| **[GCP-002-Setup-ServiceAccount](.github/workflows/GCP-002-Setup-ServiceAccount.yml)** | Creates runtime SA `council-of-ancients-sa` and grants it `aiplatform.user` + `modelarmor.user` (so the app can call Gemini and Model Armor). |
| **[GCP-003-Setup-ModelArmor](.github/workflows/GCP-003-Setup-ModelArmor.yml)** | Creates the two screening templates `council-prompt-screening` and `council-response-screening` in `us-central1`. |

These workflows do **not** deploy the app or start local Docker. Full notes: [`.github/workflows/README.md`](.github/workflows/README.md#what-the-three-gcp-setup-workflows-do).

### Workflow files (setup & destroy)

| Step | Setup | Destroy |
|------|--------|---------|
| 1 | [GCP-001-Setup-APIs](.github/workflows/GCP-001-Setup-APIs.yml) | [GCP-001-Destroy-APIs](.github/workflows/GCP-001-Destroy-APIs.yml) |
| 2 | [GCP-002-Setup-ServiceAccount](.github/workflows/GCP-002-Setup-ServiceAccount.yml) | [GCP-002-Destroy-ServiceAccount](.github/workflows/GCP-002-Destroy-ServiceAccount.yml) |
| 3 | [GCP-003-Setup-ModelArmor](.github/workflows/GCP-003-Setup-ModelArmor.yml) | [GCP-003-Destroy-ModelArmor](.github/workflows/GCP-003-Destroy-ModelArmor.yml) |

## GCP setup from zero (developer guide)

Do this once per Google Cloud project. Use the **Google Cloud Console** in a browser. No laptop `gcloud` and no JSON service-account keys.

Replace placeholders with your own values:

| Placeholder | Meaning | Example shape (not real values) |
|-------------|---------|----------------------------------|
| `YOUR_GCP_PROJECT_ID` | Project ID from GCP | `my-council-project` |
| `YOUR_GCP_PROJECT_NUMBER` | Numeric project number | `123456789012` |
| `YOUR_GITHUB_ORG_OR_USER` | GitHub owner of this repo | `your-github-org` |
| `YOUR_GITHUB_REPO` | Repo name | `Council-Of-Ancients-Google-ADK` |

Example project **name** you can use when creating the project: **Council of Ancients**.

---

### Step 1 — Create or select a GCP project

1. Open [Google Cloud Console](https://console.cloud.google.com/).
2. Project picker (top bar) → **New project**.
3. **Project name:** `Council of Ancients` (or any clear name).
4. Note the generated **Project ID** → this is `YOUR_GCP_PROJECT_ID`.
5. Open **IAM & Admin → Settings** and note **Project number** → this is `YOUR_GCP_PROJECT_NUMBER`.
6. Keep this project selected for every step below.

---

### Step 2 — Enable Service Usage API (one-time Console click)

GitHub Actions cannot enable other APIs until this one is on.

1. Go to **APIs & Services → Library**.
2. Search **Service Usage API**.
3. Open it → **Enable**.
4. Wait about one minute.

---

### Step 3 — Create the GitHub Actions deployer service account

This SA is only for CI. It is **not** the runtime app SA.

1. **IAM & Admin → Service Accounts → Create service account**.
2. **Name / ID:** `github-actions-gcp-deployer`.
3. Email will look like:  
   `github-actions-gcp-deployer@YOUR_GCP_PROJECT_ID.iam.gserviceaccount.com`
4. Grant these roles on the project:
   - Service Usage Admin
   - Service Account Admin
   - Project IAM Admin
   - Model Armor Admin (add later if the role is not listed yet)
5. Finish create. **Do not** create a JSON key.

---

### Step 4 — Create Workload Identity Federation (GitHub → GCP)

1. **IAM & Admin → Workload Identity Federation → Create pool**.
2. Pool name / ID: `github-actions`.
3. **Add provider** → OpenID Connect (OIDC).
4. Provider name / ID: `github`.
5. **Issuer (URL):** `https://token.actions.githubusercontent.com`
6. Audience: **Default audience**.
7. **Attribute mapping:**

| Google | OIDC |
|--------|------|
| `google.subject` | `assertion.sub` |
| `attribute.actor` | `assertion.actor` |
| `attribute.repository` | `assertion.repository` |
| `attribute.repository_owner` | `assertion.repository_owner` |

8. **Attribute condition** (lock to this repo):

```text
assertion.repository == "YOUR_GITHUB_ORG_OR_USER/YOUR_GITHUB_REPO"
```

9. Save. Copy the **provider resource name**:

```text
projects/YOUR_GCP_PROJECT_NUMBER/locations/global/workloadIdentityPools/github-actions/providers/github
```

That string is GitHub secret `GCP_WORKLOAD_IDENTITY_PROVIDER`.

---

### Step 5 — Allow GitHub to impersonate the deployer SA

1. Open service account `github-actions-gcp-deployer`.
2. **Permissions → VIEW PRINCIPALS BY ACCESS → GRANT ACCESS**.
3. **New principals** (paste exactly, with your numbers/names):

```text
principalSet://iam.googleapis.com/projects/YOUR_GCP_PROJECT_NUMBER/locations/global/workloadIdentityPools/github-actions/attribute.repository/YOUR_GITHUB_ORG_OR_USER/YOUR_GITHUB_REPO
```

4. **Role:** Workload Identity User (only this role).
5. Save. Wait 1–2 minutes.

---

### Step 6 — Add GitHub Actions secrets

Repo (or org) → **Settings → Secrets and variables → Actions → New repository secret**.

| Secret name | Value |
|-------------|--------|
| `GCP_PROJECT_ID` | `YOUR_GCP_PROJECT_ID` |
| `GCP_SERVICE_ACCOUNT` | `github-actions-gcp-deployer@YOUR_GCP_PROJECT_ID.iam.gserviceaccount.com` |
| `GCP_WORKLOAD_IDENTITY_PROVIDER` | `projects/YOUR_GCP_PROJECT_NUMBER/locations/global/workloadIdentityPools/github-actions/providers/github` |

---

### Step 7 — Run the three setup workflows (in order)

GitHub → **Actions** → select workflow → **Run workflow** (region `us-central1`).

1. **GCP-001-Setup-APIs**
2. **GCP-002-Setup-ServiceAccount** (default SA id: `council-of-ancients-sa`)
3. **GCP-003-Setup-ModelArmor**

If GCP-001 fails saying Service Usage API is disabled, repeat Step 2 and re-run.

Destroy order (only if tearing down): GCP-003 → GCP-002 → GCP-001 (each asks for a confirmation string).

## After GCP setup — local `.env`

```bash
cp .env.template .env
```

Set at least:

```env
GOOGLE_CLOUD_PROJECT=YOUR_GCP_PROJECT_ID
GOOGLE_CLOUD_LOCATION=global
GOOGLE_GENAI_USE_VERTEXAI=true
GOOGLE_GENAI_USE_ENTERPRISE=true

MODEL_ARMOR_PROMPT_TEMPLATE=projects/YOUR_GCP_PROJECT_ID/locations/us-central1/templates/council-prompt-screening
MODEL_ARMOR_RESPONSE_TEMPLATE=projects/YOUR_GCP_PROJECT_ID/locations/us-central1/templates/council-response-screening
```

## Hands-on coding

Follow [`HandsOn_GCP_Agents.md`](HandsOn_GCP_Agents.md) in order (config → counselors → facilitator → Model Armor App → local run → API → Angular → guardrail tests).

## Future work (GitHub issues)

Deferred product work is tracked as **Epics** and **Features** (labels: `epic`, `feature`, `future`, plus `agents` / `rag` / `tools` / `api` / `portal` / `eval` / `security` / `cloud-run`).

Browse: [all `future`](https://github.com/javakishore-veleti/Council-Of-Ancients-Google-ADK/issues?q=is%3Aissue+label%3Afuture) · [epics](https://github.com/javakishore-veleti/Council-Of-Ancients-Google-ADK/issues?q=is%3Aissue+label%3Aepic) · [features](https://github.com/javakishore-veleti/Council-Of-Ancients-Google-ADK/issues?q=is%3Aissue+label%3Afeature)

Each issue includes: description, objective, outcomes, acceptance criteria, and definition of done.

### Epics

| Epic | Issue |
|------|-------|
| Core Council agents MVP | [#2](https://github.com/javakishore-veleti/Council-Of-Ancients-Google-ADK/issues/2) |
| Knowledge grounding (RAG) | [#3](https://github.com/javakishore-veleti/Council-Of-Ancients-Google-ADK/issues/3) |
| Agent tools beyond debate | [#4](https://github.com/javakishore-veleti/Council-Of-Ancients-Google-ADK/issues/4) |
| API services (FastAPI / SSE) | [#5](https://github.com/javakishore-veleti/Council-Of-Ancients-Google-ADK/issues/5) |
| Angular council portal | [#6](https://github.com/javakishore-veleti/Council-Of-Ancients-Google-ADK/issues/6) |
| Evals & guardrail regression | [#7](https://github.com/javakishore-veleti/Council-Of-Ancients-Google-ADK/issues/7) |
| Production Cloud Run hardening | [#8](https://github.com/javakishore-veleti/Council-Of-Ancients-Google-ADK/issues/8) |

### Features (by epic)

| Epic | Features |
|------|----------|
| #2 Core agents | [#9](https://github.com/javakishore-veleti/Council-Of-Ancients-Google-ADK/issues/9) counselors · [#10](https://github.com/javakishore-veleti/Council-Of-Ancients-Google-ADK/issues/10) facilitator protocol · [#11](https://github.com/javakishore-veleti/Council-Of-Ancients-Google-ADK/issues/11) Model Armor App |
| #3 RAG | [#12](https://github.com/javakishore-veleti/Council-Of-Ancients-Google-ADK/issues/12) corpus ingest · [#13](https://github.com/javakishore-veleti/Council-Of-Ancients-Google-ADK/issues/13) retrieval tool |
| #4 Tools | [#14](https://github.com/javakishore-veleti/Council-Of-Ancients-Google-ADK/issues/14) sample domain tools |
| #5 API | [#15](https://github.com/javakishore-veleti/Council-Of-Ancients-Google-ADK/issues/15) FastAPI entry · [#16](https://github.com/javakishore-veleti/Council-Of-Ancients-Google-ADK/issues/16) SSE/API contract |
| #6 Portal | [#17](https://github.com/javakishore-veleti/Council-Of-Ancients-Google-ADK/issues/17) Angular chat shell · [#18](https://github.com/javakishore-veleti/Council-Of-Ancients-Google-ADK/issues/18) event stream UI |
| #7 Evals | [#19](https://github.com/javakishore-veleti/Council-Of-Ancients-Google-ADK/issues/19) dilemma eval set · [#20](https://github.com/javakishore-veleti/Council-Of-Ancients-Google-ADK/issues/20) injection regression |
| #8 Cloud Run | [#21](https://github.com/javakishore-veleti/Council-Of-Ancients-Google-ADK/issues/21) private deploy · [#22](https://github.com/javakishore-veleti/Council-Of-Ancients-Google-ADK/issues/22) durable sessions |

## More detail

| Doc | Contents |
|-----|----------|
| [`HandsOn_GCP_Agents.md`](HandsOn_GCP_Agents.md) | Coding lab with per-step snippets |
| [`.github/workflows/README.md`](.github/workflows/README.md) | What each workflow enables / creates / destroys |
| [`CICD/GCP/README.md`](CICD/GCP/README.md) | WIF secrets, Console notes, template JSON |

## References

- Daniela Petruzalek — [AI Agents from Scratch with Google ADK](https://danicat.dev/posts/ai-agents-from-scratch-with-google-adk/)
- Companion example repo — [danicat/council](https://github.com/danicat/council)
- Google ADK docs — [adk.dev](https://adk.dev)
