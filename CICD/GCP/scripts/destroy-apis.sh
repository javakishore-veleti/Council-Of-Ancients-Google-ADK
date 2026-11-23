#!/usr/bin/env bash
# GCP-001 Destroy APIs — disable optional APIs (does not disable IAM).
# Requires CONFIRM_DESTROY=disable-apis
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=common.sh
source "${SCRIPT_DIR}/common.sh"
init_gcp_defaults

if [[ "${CONFIRM_DESTROY:-}" != "disable-apis" ]]; then
  echo "Refusing to disable APIs. Set CONFIRM_DESTROY=disable-apis to proceed." >&2
  exit 1
fi

echo "Disabling Model Armor / AI Platform / Cloud Run / Cloud Build APIs on ${GOOGLE_CLOUD_PROJECT}..."
# Keep iam.googleapis.com enabled — disabling it can lock out project admin tooling.
gcloud services disable \
  modelarmor.googleapis.com \
  aiplatform.googleapis.com \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  --project="${GOOGLE_CLOUD_PROJECT}" \
  --force

echo "APIs disabled (iam.googleapis.com left enabled)."
