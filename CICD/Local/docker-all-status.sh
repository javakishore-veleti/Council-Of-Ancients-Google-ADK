#!/usr/bin/env bash
# Show status of local Docker infra for Council of Ancients.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

COMPOSE_FILE="${SCRIPT_DIR}/docker-compose.yml"
ENV_FILE="${SCRIPT_DIR}/.env"
ENV_EXAMPLE="${SCRIPT_DIR}/.env.example"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
REPO_ENV="${REPO_ROOT}/.env"

if [[ ! -f "${ENV_FILE}" && -f "${ENV_EXAMPLE}" ]]; then
  cp "${ENV_EXAMPLE}" "${ENV_FILE}"
fi

if ! command -v docker >/dev/null 2>&1; then
  echo "docker is required but was not found on PATH." >&2
  exit 1
fi

echo "=== Compose services (including postgres profile) ==="
docker compose \
  --env-file "${ENV_FILE}" \
  -f "${COMPOSE_FILE}" \
  --profile postgres \
  ps -a

echo
echo "=== Health / readiness probes ==="

check_tcp() {
  local name="$1"
  local host="$2"
  local port="$3"
  if (echo >/dev/tcp/"${host}"/"${port}") >/dev/null 2>&1; then
    echo "  ${name}: reachable at ${host}:${port}"
  else
    echo "  ${name}: not reachable at ${host}:${port}"
  fi
}

# Portable TCP check without bash /dev/tcp where unavailable.
probe() {
  local name="$1"
  local host="$2"
  local port="$3"
  if command -v nc >/dev/null 2>&1; then
    if nc -z "${host}" "${port}" >/dev/null 2>&1; then
      echo "  ${name}: reachable at ${host}:${port}"
    else
      echo "  ${name}: not reachable at ${host}:${port}"
    fi
  elif command -v python3 >/dev/null 2>&1; then
    if python3 - "${host}" "${port}" <<'PY'
import socket, sys
host, port = sys.argv[1], int(sys.argv[2])
s = socket.socket()
s.settimeout(1.5)
try:
    s.connect((host, port))
except OSError:
    sys.exit(1)
finally:
    s.close()
PY
    then
      echo "  ${name}: reachable at ${host}:${port}"
    else
      echo "  ${name}: not reachable at ${host}:${port}"
    fi
  else
    check_tcp "${name}" "${host}" "${port}"
  fi
}

# shellcheck disable=SC1090
set -a
# shellcheck source=/dev/null
source "${ENV_FILE}"
set +a

probe "Redis" "127.0.0.1" "${REDIS_PORT:-6379}"
probe "Jaeger UI" "127.0.0.1" "${JAEGER_UI_PORT:-16686}"
probe "Jaeger OTLP gRPC" "127.0.0.1" "${JAEGER_OTLP_GRPC_PORT:-4317}"
probe "Postgres" "127.0.0.1" "${POSTGRES_PORT:-5432}"

echo
echo "=== App DB mode ==="
if [[ -f "${REPO_ENV}" ]]; then
  DB_BACKEND="$(grep -E '^DB_BACKEND=' "${REPO_ENV}" | tail -n1 | cut -d= -f2- || true)"
  DATABASE_URL="$(grep -E '^DATABASE_URL=' "${REPO_ENV}" | tail -n1 | cut -d= -f2- || true)"
  echo "  DB_BACKEND=${DB_BACKEND:-sqlite (default)}"
  if [[ -n "${DATABASE_URL}" ]]; then
    echo "  DATABASE_URL=${DATABASE_URL}"
  fi
else
  echo "  No repo-root .env found; app default is SQLite."
fi

echo
echo "Tips:"
echo "  Start default stack:  ${SCRIPT_DIR}/docker-all-up.sh"
echo "  Start with Postgres:  ${SCRIPT_DIR}/docker-all-up.sh --postgres"
echo "  Stop stack:           ${SCRIPT_DIR}/docker-all-down.sh"
