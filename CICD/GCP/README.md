# GCP-001 — GitHub Actions setup / destroy

Manually triggered workflows under `.github/workflows/` that run the scripts in `CICD/GCP/scripts/`.

## Recommended order

1. **GCP-001-Setup-APIs**
2. **GCP-001-Setup-ServiceAccount**
3. **GCP-001-Setup-ModelArmor**

Destroy in reverse: ModelArmor → ServiceAccount → APIs.

## GitHub Actions secrets to create

Repo → **Settings → Secrets and variables → Actions → New repository secret**:

| Secret name | What to put |
|-------------|-------------|
| `GCP_PROJECT_ID` | Your GCP project id (e.g. `gen-lang-client-0604720781`) |
| `GCP_SA_KEY` | Full JSON key for a **deployer** service account that can run these jobs |

### Deployer service account (create once locally)

This is **not** the runtime `council-of-ancients-sa`. It is a bootstrap account used only by GitHub Actions.

```bash
export PROJECT_ID="gen-lang-client-0604720781"
export DEPLOYER_SA="github-actions-gcp-deployer"
export DEPLOYER_EMAIL="${DEPLOYER_SA}@${PROJECT_ID}.iam.gserviceaccount.com"

gcloud iam service-accounts create "${DEPLOYER_SA}" \
  --project="${PROJECT_ID}" \
  --display-name="GitHub Actions GCP Deployer"

# Least-privilege-ish bootstrap roles for these workflows
for role in \
  roles/serviceusage.serviceUsageAdmin \
  roles/iam.serviceAccountAdmin \
  roles/resourcemanager.projectIamAdmin \
  roles/modelarmor.admin
do
  gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
    --member="serviceAccount:${DEPLOYER_EMAIL}" \
    --role="${role}"
done

gcloud iam service-accounts keys create ./gcp-sa-key.json \
  --iam-account="${DEPLOYER_EMAIL}" \
  --project="${PROJECT_ID}"
```

Paste the **entire contents** of `gcp-sa-key.json` into the `GCP_SA_KEY` secret, then delete the local file:

```bash
rm ./gcp-sa-key.json
```

## Workflow inputs

- **region** (default `us-central1`) — Model Armor region; both templates must share it.
- Destroy workflows require a confirmation string input (e.g. `delete-model-armor`).

## After Setup-ModelArmor succeeds

Update local `.env`:

```env
MODEL_ARMOR_PROMPT_TEMPLATE=projects/<GCP_PROJECT_ID>/locations/us-central1/templates/council-prompt-screening
MODEL_ARMOR_RESPONSE_TEMPLATE=projects/<GCP_PROJECT_ID>/locations/us-central1/templates/council-response-screening
```

Canonical filter JSON (for REST/IaC) lives in `CICD/GCP/templates/`.
