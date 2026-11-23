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

wait_for_service_account "${COUNCIL_SERVICE_ACCOUNT_EMAIL}"

echo "Granting roles/aiplatform.user and roles/modelarmor.user..."
add_project_iam_binding_with_retry \
  "serviceAccount:${COUNCIL_SERVICE_ACCOUNT_EMAIL}" \
  "roles/aiplatform.user"

add_project_iam_binding_with_retry \
  "serviceAccount:${COUNCIL_SERVICE_ACCOUNT_EMAIL}" \
  "roles/modelarmor.user"

echo "Service account ready: ${COUNCIL_SERVICE_ACCOUNT_EMAIL}"
