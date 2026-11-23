# GitHub Actions workflows

Manual (`workflow_dispatch`) jobs for this repo. GCP auth uses Workload Identity Federation — see [`CICD/GCP/README.md`](../../CICD/GCP/README.md) for secrets and one-time Console setup.

Scripts live in [`CICD/GCP/scripts/`](../../CICD/GCP/scripts/).

## Table of contents

1. [What the three GCP setup workflows do](#what-the-three-gcp-setup-workflows-do)
2. [GCP-001-Setup-APIs](#1-gcp-001-setup-apis)
3. [GCP-002-Setup-ServiceAccount](#2-gcp-002-setup-serviceaccount)
4. [GCP-003-Setup-ModelArmor](#3-gcp-003-setup-modelarmor)
5. [Recommended run order](#recommended-run-order)
6. [Shared auth helper](#shared-auth-helper)

## What the three GCP setup workflows do

These prepare Google Cloud so the Council agents can call Gemini on Vertex AI and screen prompts/replies with Model Armor. They do **not** deploy the app or create local Docker containers.

| Workflow | What it does |
|----------|----------------|
| **[GCP-001-Setup-APIs](#1-gcp-001-setup-apis)** | Enables Vertex AI, Model Armor, Cloud Run, Cloud Build, and IAM APIs on your project. |
| **[GCP-002-Setup-ServiceAccount](#2-gcp-002-setup-serviceaccount)** | Creates runtime SA `council-of-ancients-sa` and grants it `aiplatform.user` + `modelarmor.user` (so the app can call Gemini and Model Armor). |
| **[GCP-003-Setup-ModelArmor](#3-gcp-003-setup-modelarmor)** | Creates the two screening templates `council-prompt-screening` and `council-response-screening` in `us-central1`. |

### 1. [`GCP-001-Setup-APIs`](GCP-001-Setup-APIs.yml)

**Purpose:** Turn on the Google Cloud APIs this project needs.

**What it does:**

- Authenticates as the deployer SA via WIF
- Enables:
  - `aiplatform.googleapis.com` — Vertex AI / Gemini
  - `modelarmor.googleapis.com` — Model Armor screening
  - `run.googleapis.com` — Cloud Run (for a later deploy)
  - `cloudbuild.googleapis.com` — Cloud Build (for source deploys)
  - `iam.googleapis.com` — IAM / service accounts

**Prerequisite (once, in Console):** Service Usage API must already be enabled on the project (chicken-and-egg; Actions cannot enable APIs until Service Usage itself is on).

**Destroy:** [`GCP-001-Destroy-APIs`](GCP-001-Destroy-APIs.yml) disables Model Armor, AI Platform, Cloud Run, and Cloud Build (keeps IAM). Requires confirmation input `disable-apis`.

### 2. [`GCP-002-Setup-ServiceAccount`](GCP-002-Setup-ServiceAccount.yml)

**Purpose:** Create the **runtime** service account the Council app will use (separate from the GitHub deployer SA).

**What it does:**

- Creates `council-of-ancients-sa@<GCP_PROJECT_ID>.iam.gserviceaccount.com` (if missing)
- Waits for GCP propagation, then grants:
  - `roles/aiplatform.user` — call Vertex AI / Gemini
  - `roles/modelarmor.user` — call Model Armor with the templates

This is the identity Cloud Run (or local ADC with impersonation) should use at runtime — **not** `github-actions-gcp-deployer`.

**Destroy:** [`GCP-002-Destroy-ServiceAccount`](GCP-002-Destroy-ServiceAccount.yml) removes those IAM roles and deletes the SA. Requires confirmation `delete-service-account`.

### 3. [`GCP-003-Setup-ModelArmor`](GCP-003-Setup-ModelArmor.yml)

**Purpose:** Create the two Model Armor **templates** that screen user prompts and model responses.

**What it does:**

- Creates (idempotent if already present):
  - `council-prompt-screening` — input filters (jailbreak/PI, SDP/PII, malicious URIs, RAI)
  - `council-response-screening` — output filters (calibrated for counselor replies)
- Region default: `us-central1` (both templates must share the same region)

**Full resource names for `.env`:**

```env
MODEL_ARMOR_PROMPT_TEMPLATE=projects/<GCP_PROJECT_ID>/locations/us-central1/templates/council-prompt-screening
MODEL_ARMOR_RESPONSE_TEMPLATE=projects/<GCP_PROJECT_ID>/locations/us-central1/templates/council-response-screening
```

Filter JSON schemas (for REST/IaC reference): [`CICD/GCP/templates/`](../../CICD/GCP/templates/).

**Destroy:** [`GCP-003-Destroy-ModelArmor`](GCP-003-Destroy-ModelArmor.yml) deletes both templates. Requires confirmation `delete-model-armor`.

## Recommended run order

| Step | Setup | Destroy (reverse) |
|------|--------|-------------------|
| 1 | [GCP-001-Setup-APIs](GCP-001-Setup-APIs.yml) | [GCP-001-Destroy-APIs](GCP-001-Destroy-APIs.yml) |
| 2 | [GCP-002-Setup-ServiceAccount](GCP-002-Setup-ServiceAccount.yml) | [GCP-002-Destroy-ServiceAccount](GCP-002-Destroy-ServiceAccount.yml) |
| 3 | [GCP-003-Setup-ModelArmor](GCP-003-Setup-ModelArmor.yml) | [GCP-003-Destroy-ModelArmor](GCP-003-Destroy-ModelArmor.yml) |

## Shared auth helper

[`.github/actions/gcp-auth`](../actions/gcp-auth/action.yml) — composite action that authenticates with `GCP_WORKLOAD_IDENTITY_PROVIDER` + `GCP_SERVICE_ACCOUNT` (no JSON keys).
