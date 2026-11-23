#!/usr/bin/env bash
# GCP-003 Setup ModelArmor — create prompt + response screening templates.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=common.sh
source "${SCRIPT_DIR}/common.sh"
init_gcp_defaults

create_template_if_missing() {
  local template_id="$1"
  shift

  if gcloud model-armor templates describe "${template_id}" \
    --project="${GOOGLE_CLOUD_PROJECT}" \
    --location="${MODEL_ARMOR_REGION}" >/dev/null 2>&1; then
    echo "Template already exists: ${template_id}"
    return 0
  fi

  echo "Creating Model Armor template: ${template_id}"
  gcloud model-armor templates create "${template_id}" \
    --project="${GOOGLE_CLOUD_PROJECT}" \
    --location="${MODEL_ARMOR_REGION}" \
    "$@"
}

echo "Creating prompt screening template (${PROMPT_TEMPLATE_NAME})..."
create_template_if_missing "${PROMPT_TEMPLATE_ID}" \
  --rai-settings-filters="filterType=SEXUALLY_EXPLICIT,confidenceLevel=MEDIUM_AND_ABOVE" \
  --rai-settings-filters="filterType=HATE_SPEECH,confidenceLevel=MEDIUM_AND_ABOVE" \
  --rai-settings-filters="filterType=HARASSMENT,confidenceLevel=MEDIUM_AND_ABOVE" \
  --rai-settings-filters="filterType=DANGEROUS,confidenceLevel=MEDIUM_AND_ABOVE" \
  --pi-and-jailbreak-filter-settings-enforcement="enabled" \
  --pi-and-jailbreak-filter-settings-confidence-level="medium-and-above" \
  --basic-config-filter-enforcement="enabled" \
  --malicious-uri-filter-settings-enforcement="enabled" \
  --template-metadata-log-operations \
  --template-metadata-log-sanitize-operations

echo "Creating response screening template (${RESPONSE_TEMPLATE_NAME})..."
create_template_if_missing "${RESPONSE_TEMPLATE_ID}" \
  --rai-settings-filters="filterType=DANGEROUS,confidenceLevel=HIGH" \
  --rai-settings-filters="filterType=HARASSMENT,confidenceLevel=HIGH" \
  --rai-settings-filters="filterType=HATE_SPEECH,confidenceLevel=MEDIUM_AND_ABOVE" \
  --rai-settings-filters="filterType=SEXUALLY_EXPLICIT,confidenceLevel=MEDIUM_AND_ABOVE" \
  --pi-and-jailbreak-filter-settings-enforcement="enabled" \
  --pi-and-jailbreak-filter-settings-confidence-level="high" \
  --basic-config-filter-enforcement="enabled" \
  --malicious-uri-filter-settings-enforcement="enabled" \
  --template-metadata-log-operations \
  --template-metadata-log-sanitize-operations

echo
echo "Model Armor templates ready. Put these in your local .env:"
print_template_paths

echo
echo "Listing templates in ${MODEL_ARMOR_REGION}:"
gcloud model-armor templates list \
  --project="${GOOGLE_CLOUD_PROJECT}" \
  --location="${MODEL_ARMOR_REGION}" \
  --format="table(name)"
