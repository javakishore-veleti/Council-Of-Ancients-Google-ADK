#!/usr/bin/env bash
# Shared helpers for GCP-001 setup/destroy scripts.
set -euo pipefail

require_env() {
  local name="$1"
  if [[ -z "${!name:-}" ]]; then
    echo "Missing required env var: ${name}" >&2
    exit 1
  fi
}

init_gcp_defaults() {
  require_env GOOGLE_CLOUD_PROJECT

  export MODEL_ARMOR_REGION="${MODEL_ARMOR_REGION:-us-central1}"
  export COUNCIL_SERVICE_ACCOUNT="${COUNCIL_SERVICE_ACCOUNT:-council-of-ancients-sa}"
  export COUNCIL_SERVICE_ACCOUNT_EMAIL="${COUNCIL_SERVICE_ACCOUNT}@${GOOGLE_CLOUD_PROJECT}.iam.gserviceaccount.com"
  export PROMPT_TEMPLATE_ID="${PROMPT_TEMPLATE_ID:-council-prompt-screening}"
  export RESPONSE_TEMPLATE_ID="${RESPONSE_TEMPLATE_ID:-council-response-screening}"
  export PROMPT_TEMPLATE_NAME="projects/${GOOGLE_CLOUD_PROJECT}/locations/${MODEL_ARMOR_REGION}/templates/${PROMPT_TEMPLATE_ID}"
  export RESPONSE_TEMPLATE_NAME="projects/${GOOGLE_CLOUD_PROJECT}/locations/${MODEL_ARMOR_REGION}/templates/${RESPONSE_TEMPLATE_ID}"

  # Model Armor requires a regional API endpoint from workstations/CI.
  export CLOUDSDK_API_ENDPOINT_OVERRIDES_MODELARMOR="https://modelarmor.${MODEL_ARMOR_REGION}.rep.googleapis.com/"

  gcloud config set project "${GOOGLE_CLOUD_PROJECT}" >/dev/null
}

print_template_paths() {
  echo "PROMPT_TEMPLATE_NAME=${PROMPT_TEMPLATE_NAME}"
  echo "RESPONSE_TEMPLATE_NAME=${RESPONSE_TEMPLATE_NAME}"
}
