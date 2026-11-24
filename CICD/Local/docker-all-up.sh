#!/usr/bin/env bash
# Start local Docker infra for Council of Ancients.
# Default: Redis + Jaeger (app uses SQLite).
# Optional: --postgres (or USE_POSTGRES=1) also starts Postgres.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

COMPOSE_FILE="${SCRIPT_DIR}/docker-compose.yml"
ENV_FILE="${SCRIPT_DIR}/.env"
ENV_EXAMPLE="${SCRIPT_DIR}/.env.example"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
REPO_ENV="${REPO_ROOT}/.env"
REPO_ENV_TEMPLATE="${REPO_ROOT}/.env.template"

WITH_POSTGRES=0
DETACH=(-d)

usage() {
  cat <<'EOF'
Usage: ./docker-all-up.sh [--postgres] [--foreground] [-h|--help]

  --postgres      Also start Postgres (overrides default SQLite app DB path).
                  Equivalent to USE_POSTGRES=1.
  --foreground    Run compose in the foreground (no -d).
  -h, --help      Show this help.

Default stack: Redis + Jaeger.
App DB defaults to SQLite unless DB_BACKEND=postgres in the repo-root .env.
EOF
}

for arg in "$@"; do
  case "${arg}" in
    --postgres)
      WITH_POSTGRES=1
      ;;
    --foreground)
      DETACH=()
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

if [[ "${USE_POSTGRES:-0}" == "1" || "${DB_BACKEND:-}" == "postgres" ]]; then
  WITH_POSTGRES=1
fi

if [[ ! -f "${ENV_FILE}" && -f "${ENV_EXAMPLE}" ]]; then
  cp "${ENV_EXAMPLE}" "${ENV_FILE}"
  echo "Created ${ENV_FILE} from .env.example"
fi

if [[ ! -f "${REPO_ENV}" && -f "${REPO_ENV_TEMPLATE}" ]]; then
  cp "${REPO_ENV_TEMPLATE}" "${REPO_ENV}"
  echo "Created ${REPO_ENV} from .env.template"
fi

if ! command -v docker >/dev/null 2>&1; then
  echo "docker is required but was not found on PATH." >&2
  exit 1
fi

if ! docker compose version >/dev/null 2>&1; then
  echo "docker compose plugin is required." >&2
  exit 1
fi

PROFILES=()
if [[ "${WITH_POSTGRES}" -eq 1 ]]; then
  PROFILES+=(--profile postgres)
  echo "Starting Redis, Jaeger, and Postgres..."
else
  echo "Starting Redis and Jaeger (SQLite remains the default app DB)..."
fi

# Bash 3.2 + set -u treats empty "${arr[@]}" as unbound; expand only when set.
docker compose \
  --env-file "${ENV_FILE}" \
  -f "${COMPOSE_FILE}" \
  ${PROFILES[@]+"${PROFILES[@]}"} \
  up \
  --remove-orphans \
  ${DETACH[@]+"${DETACH[@]}"}

# Sync override hints into repo-root .env when Postgres was requested.
if [[ "${WITH_POSTGRES}" -eq 1 && -f "${REPO_ENV}" ]]; then
  if grep -q '^DB_BACKEND=' "${REPO_ENV}"; then
    sed -i.bak 's/^DB_BACKEND=.*/DB_BACKEND=postgres/' "${REPO_ENV}" && rm -f "${REPO_ENV}.bak"
  else
    printf '\nDB_BACKEND=postgres\n' >> "${REPO_ENV}"
  fi

  if ! grep -q '^DATABASE_URL=' "${REPO_ENV}"; then
    printf 'DATABASE_URL=postgresql://postgres:postgres@localhost:5432/council\n' >> "${REPO_ENV}"
  fi
  echo "Set DB_BACKEND=postgres in ${REPO_ENV}"
fi

echo
echo "Local infra is up."
echo "  Redis:     localhost:${REDIS_PORT:-6379}"
echo "  Jaeger UI: http://localhost:${JAEGER_UI_PORT:-16686}"
if [[ "${WITH_POSTGRES}" -eq 1 ]]; then
  echo "  Postgres:  localhost:${POSTGRES_PORT:-5432} (user/password: postgres/postgres, db: council)"
else
  echo "  Postgres:  not started (app default: SQLite). Re-run with --postgres to enable."
fi
echo
echo "Status: ${SCRIPT_DIR}/docker-all-status.sh"
