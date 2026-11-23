#!/usr/bin/env bash
# GCP-001 Setup APIs — enable required Google Cloud APIs.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=common.sh
source "${SCRIPT_DIR}/common.sh"
init_gcp_defaults

echo "Enabling required Google Cloud APIs on ${GOOGLE_CLOUD_PROJECT}..."
gcloud services enable \
  aiplatform.googleapis.com \
  modelarmor.googleapis.com \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  iam.googleapis.com \
  --project="${GOOGLE_CLOUD_PROJECT}"

echo "APIs enabled."
gcloud services list \
  --enabled \
  --project="${GOOGLE_CLOUD_PROJECT}" \
  --filter="config.name:(aiplatform.googleapis.com OR modelarmor.googleapis.com OR run.googleapis.com OR cloudbuild.googleapis.com OR iam.googleapis.com)" \
  --format="table(config.name)"
