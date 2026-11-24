#!/usr/bin/env bash
# Stop and remove local Docker infra for Council of Ancients.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

COMPOSE_FILE="${SCRIPT_DIR}/docker-compose.yml"
ENV_FILE="${SCRIPT_DIR}/.env"
ENV_EXAMPLE="${SCRIPT_DIR}/.env.example"

REMOVE_VOLUMES=0

usage() {
  cat <<'EOF'
Usage: ./docker-all-down.sh [--volumes] [-h|--help]

  --volumes   Also remove named volumes (Redis/Postgres/observability data).
  -h, --help  Show this help.
EOF
}

for arg in "$@"; do
  case "${arg}" in
    --volumes)
      REMOVE_VOLUMES=1
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: ${arg}" >&2
      usage >&2
      exit 1
      ;;
  esac
done

if [[ ! -f "${ENV_FILE}" && -f "${ENV_EXAMPLE}" ]]; then
  cp "${ENV_EXAMPLE}" "${ENV_FILE}"
fi

if ! command -v docker >/dev/null 2>&1; then
  echo "docker is required but was not found on PATH." >&2
  exit 1
fi

EXTRA=()
if [[ "${REMOVE_VOLUMES}" -eq 1 ]]; then
  EXTRA+=(--volumes)
  echo "Stopping stack and removing volumes..."
else
  echo "Stopping stack (volumes preserved)..."
fi

# Include optional profiles so Postgres / observability containers are torn down too.
# Bash 3.2 + set -u treats empty "${arr[@]}" as unbound; expand only when set.
docker compose \
  --env-file "${ENV_FILE}" \
  -f "${COMPOSE_FILE}" \
  --profile postgres \
  --profile observability \
  down \
  --remove-orphans \
  ${EXTRA[@]+"${EXTRA[@]}"}

echo "Local infra is down."
