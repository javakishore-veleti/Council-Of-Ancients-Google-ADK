#!/usr/bin/env bash
# GCP-001 Destroy ModelArmor — delete prompt + response screening templates.
# Requires CONFIRM_DESTROY=delete-model-armor
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=common.sh
source "${SCRIPT_DIR}/common.sh"
init_gcp_defaults

if [[ "${CONFIRM_DESTROY:-}" != "delete-model-armor" ]]; then
  echo "Refusing to delete Model Armor templates. Set CONFIRM_DESTROY=delete-model-armor to proceed." >&2
  exit 1
fi

delete_template_if_present() {
  local template_id="$1"
  if gcloud model-armor templates describe "${template_id}" \
    --project="${GOOGLE_CLOUD_PROJECT}" \
    --location="${MODEL_ARMOR_REGION}" >/dev/null 2>&1; then
    echo "Deleting Model Armor template: ${template_id}"
    gcloud model-armor templates delete "${template_id}" \
      --project="${GOOGLE_CLOUD_PROJECT}" \
      --location="${MODEL_ARMOR_REGION}" \
      --quiet
  else
    echo "Template already absent: ${template_id}"
  fi
}

delete_template_if_present "${PROMPT_TEMPLATE_ID}"
delete_template_if_present "${RESPONSE_TEMPLATE_ID}"

echo "Model Armor destroy complete."
