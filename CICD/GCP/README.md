# GCP-001 — GitHub Actions setup / destroy

Manually triggered workflows under `.github/workflows/` that run the scripts in `CICD/GCP/scripts/`.

**No laptop `gcloud` and no JSON service-account keys.** Auth uses [Workload Identity Federation (WIF)](https://github.com/google-github-actions/auth#workload-identity-federation-through-a-service-account) so the org can share this repo safely.

## Recommended order

1. **GCP-001-Setup-APIs**
2. **GCP-001-Setup-ServiceAccount**
3. **GCP-001-Setup-ModelArmor**

Destroy in reverse: ModelArmor → ServiceAccount → APIs.

## GitHub secrets (org-shared)

Prefer **GitHub Organization secrets** (or Environment secrets) so every engineer reuses the same values—nobody downloads keys.

| Secret name | What to put |
|-------------|-------------|
| `GCP_PROJECT_ID` | GCP project id (e.g. `gen-lang-client-0604720781`) |
| `GCP_SERVICE_ACCOUNT` | Deployer SA email, e.g. `github-actions-gcp-deployer@PROJECT_ID.iam.gserviceaccount.com` |
| `GCP_WORKLOAD_IDENTITY_PROVIDER` | Full provider resource name from WIF (see below) |

Optional: store `GCP_PROJECT_ID` as an Actions **Variable** instead of a secret if you prefer it visible.

## One-time org admin setup (Google Cloud Console — no laptop CLI)

Have a cloud/platform admin do this once in the browser ([Google Cloud Console](https://console.cloud.google.com/)). Engineers only run the GitHub Actions afterward.

### A. Create the deployer service account

1. **IAM & Admin → Service Accounts → Create service account**
2. Name: `github-actions-gcp-deployer`
3. Grant these project roles:
   - **Service Usage Admin** (`roles/serviceusage.serviceUsageAdmin`)
   - **Service Account Admin** (`roles/iam.serviceAccountAdmin`)
   - **Project IAM Admin** (`roles/resourcemanager.projectIamAdmin`)
   - **Model Armor Admin** (`roles/modelarmor.admin`)
4. **Do not** create a JSON key.

### B. Create Workload Identity Federation for GitHub

1. **IAM & Admin → Workload Identity Federation → Create Pool**
   - Pool id example: `github-actions`
2. **Add Provider**
   - Provider type: **OpenID Connect (OIDC)**
   - Provider id example: `github`
   - Issuer: `https://token.actions.githubusercontent.com`
   - Audience: leave default / `https://github.com/OWNER` as your org policy requires  
     (Google’s recommended GitHub mapping uses attribute mapping below.)
3. Attribute mapping (typical GitHub Actions setup):
   - `google.subject` → `assertion.sub`
   - `attribute.actor` → `assertion.actor`
   - `attribute.repository` → `assertion.repository`
   - `attribute.repository_owner` → `assertion.repository_owner`
4. Attribute condition (lock to your org or this repo), e.g.:
   - Org-wide: `assertion.repository_owner == 'javakishore-veleti'`
   - Single repo: `assertion.repository == 'javakishore-veleti/Council-Of-Ancients-Google-ADK'`

Copy the **provider resource name**; it looks like:

```text
projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/github-actions/providers/github
```

That value is `GCP_WORKLOAD_IDENTITY_PROVIDER`.

### C. Allow the GitHub identity to impersonate the deployer SA

1. Open the deployer SA → **Permissions → Grant access**
2. Principal (example for one repo):

```text
principalSet://iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/github-actions/attribute.repository/javakishore-veleti/Council-Of-Ancients-Google-ADK
```

Or org-wide:

```text
principalSet://iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/github-actions/attribute.repository_owner/javakishore-veleti
```

3. Role: **Workload Identity User** (`roles/iam.workloadIdentityUser`)

Official walkthrough: [Authenticate to Google Cloud from GitHub Actions](https://github.com/google-github-actions/auth#workload-identity-federation-through-a-service-account).

### D. Add the three secrets in GitHub

- Org: **Organization settings → Secrets and variables → Actions** (recommended for sharing)
- Or repo: **Settings → Secrets and variables → Actions**

Then any engineer can open **Actions**, pick a `GCP-001-*` workflow, and click **Run workflow**.

## Workflow inputs

- **region** (default `us-central1`) — Model Armor region; both templates must share it.
- Destroy workflows require a confirmation string input (e.g. `delete-model-armor`).

## After Setup-ModelArmor succeeds

Update local `.env` (still local app config only—no `gcloud`):

```env
MODEL_ARMOR_PROMPT_TEMPLATE=projects/<GCP_PROJECT_ID>/locations/us-central1/templates/council-prompt-screening
MODEL_ARMOR_RESPONSE_TEMPLATE=projects/<GCP_PROJECT_ID>/locations/us-central1/templates/council-response-screening
```

Canonical filter JSON (for REST/IaC) lives in `CICD/GCP/templates/`.
