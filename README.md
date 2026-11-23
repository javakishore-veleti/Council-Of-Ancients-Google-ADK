# Council-Of-Ancients-Google-ADK

Multi-agent Council of Ancients on Google ADK, inspired by Daniela Petruzalek’s [AI Agents from Scratch with Google ADK](https://danicat.dev/posts/ai-agents-from-scratch-with-google-adk/) (companion reference: [danicat/council](https://github.com/danicat/council)).

## Table of contents

1. [Layout](#layout)
2. [Local infrastructure](#local-infrastructure)
3. [GitHub Actions secrets to configure](#github-actions-secrets-to-configure)
4. [What the three GCP setup workflows do](#what-the-three-gcp-setup-workflows-do)
   - [GCP-001 / GCP-002 / GCP-003 summary table](#what-the-three-gcp-setup-workflows-do)
   - [Workflow files (setup & destroy)](#workflow-files-setup--destroy)
5. [GCP setup from zero (developer guide)](#gcp-setup-from-zero-developer-guide)
6. [After GCP setup — local `.env`](#after-gcp-setup--local-env)
7. [More detail](#more-detail)
8. [Workflows deep dive](.github/workflows/README.md#github-actions-secrets-to-configure)

## Layout

| Path | Role |
|------|------|
| `Middleware/Agents/` | ADK agents (Facilitator + counselors) |
| `Middleware/API-Services/` | FastAPI / ADK runtime APIs |
| `Portals/` | Angular portals |
| `CICD/Local/` | Local Docker infra (Redis, Jaeger, optional Postgres) |
| `CICD/GCP/` | Scripts + templates used by the GCP GitHub Actions |
| `.github/workflows/` | Manual GCP setup / destroy workflows |

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

## More detail

| Doc | Contents |
|-----|----------|
| [`.github/workflows/README.md`](.github/workflows/README.md) | What each workflow enables / creates / destroys |
| [`CICD/GCP/README.md`](CICD/GCP/README.md) | WIF secrets, Console notes, template JSON |
