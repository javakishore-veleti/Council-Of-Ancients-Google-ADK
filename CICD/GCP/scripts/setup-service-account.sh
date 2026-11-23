#!/usr/bin/env bash
# GCP-002 Setup ServiceAccount — create runtime SA + least-privilege roles.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=common.sh
source "${SCRIPT_DIR}/common.sh"
init_gcp_defaults

echo "Ensuring service account ${COUNCIL_SERVICE_ACCOUNT_EMAIL} exists..."
if ! gcloud iam service-accounts describe "${COUNCIL_SERVICE_ACCOUNT_EMAIL}" \
  --project="${GOOGLE_CLOUD_PROJECT}" >/dev/null 2>&1; then
  gcloud iam service-accounts create "${COUNCIL_SERVICE_ACCOUNT}" \
    --project="${GOOGLE_CLOUD_PROJECT}" \
    --display-name="Council of Ancients Cloud Run Runtime"
else
  echo "Service account already exists."
fi

echo "Granting roles/aiplatform.user and roles/modelarmor.user..."
gcloud projects add-iam-policy-binding "${GOOGLE_CLOUD_PROJECT}" \
  --member="serviceAccount:${COUNCIL_SERVICE_ACCOUNT_EMAIL}" \
  --role="roles/aiplatform.user" \
  --condition=None \
  >/dev/null

gcloud projects add-iam-policy-binding "${GOOGLE_CLOUD_PROJECT}" \
  --member="serviceAccount:${COUNCIL_SERVICE_ACCOUNT_EMAIL}" \
  --role="roles/modelarmor.user" \
  --condition=None \
  >/dev/null

echo "Service account ready: ${COUNCIL_SERVICE_ACCOUNT_EMAIL}"
