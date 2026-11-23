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

# Newly created service accounts can take a short time to become IAM-visible.
wait_for_service_account() {
  local email="$1"
  local attempts="${2:-30}"
  local sleep_seconds="${3:-5}"
  local i

  echo "Waiting for service account to become visible: ${email}"
  for ((i = 1; i <= attempts; i++)); do
    if gcloud iam service-accounts describe "${email}" \
      --project="${GOOGLE_CLOUD_PROJECT}" >/dev/null 2>&1; then
      echo "Service account is visible (attempt ${i}/${attempts})."
      return 0
    fi
    echo "  not visible yet (attempt ${i}/${attempts}); sleeping ${sleep_seconds}s..."
    sleep "${sleep_seconds}"
  done

  echo "Timed out waiting for service account: ${email}" >&2
  return 1
}

add_project_iam_binding_with_retry() {
  local member="$1"
  local role="$2"
  local attempts="${3:-12}"
  local sleep_seconds="${4:-10}"
  local i

  for ((i = 1; i <= attempts; i++)); do
    if gcloud projects add-iam-policy-binding "${GOOGLE_CLOUD_PROJECT}" \
      --member="${member}" \
      --role="${role}" \
      >/dev/null; then
      echo "Granted ${role} to ${member}"
      return 0
    fi
    echo "  IAM grant failed for ${role} (attempt ${i}/${attempts}); retrying in ${sleep_seconds}s..."
    sleep "${sleep_seconds}"
  done

  echo "Failed to grant ${role} to ${member}" >&2
  return 1
}
