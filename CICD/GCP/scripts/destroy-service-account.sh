#!/usr/bin/env bash
# GCP-001 Destroy ServiceAccount — remove IAM bindings and delete runtime SA.
# Requires CONFIRM_DESTROY=delete-service-account
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=common.sh
source "${SCRIPT_DIR}/common.sh"
init_gcp_defaults

if [[ "${CONFIRM_DESTROY:-}" != "delete-service-account" ]]; then
  echo "Refusing to delete service account. Set CONFIRM_DESTROY=delete-service-account to proceed." >&2
  exit 1
fi

MEMBER="serviceAccount:${COUNCIL_SERVICE_ACCOUNT_EMAIL}"

echo "Removing IAM roles from ${COUNCIL_SERVICE_ACCOUNT_EMAIL}..."
for role in roles/aiplatform.user roles/modelarmor.user; do
  gcloud projects remove-iam-policy-binding "${GOOGLE_CLOUD_PROJECT}" \
    --member="${MEMBER}" \
    --role="${role}" \
    --condition=None \
    >/dev/null 2>&1 || true
done

if gcloud iam service-accounts describe "${COUNCIL_SERVICE_ACCOUNT_EMAIL}" \
  --project="${GOOGLE_CLOUD_PROJECT}" >/dev/null 2>&1; then
  echo "Deleting service account ${COUNCIL_SERVICE_ACCOUNT_EMAIL}..."
  gcloud iam service-accounts delete "${COUNCIL_SERVICE_ACCOUNT_EMAIL}" \
    --project="${GOOGLE_CLOUD_PROJECT}" \
    --quiet
else
  echo "Service account already absent."
fi

echo "Service account destroy complete."
