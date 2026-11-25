#!/usr/bin/env bash
# Start local Docker infra for Council of Ancients.
# Default: Redis + Jaeger + OTEL Collector (app uses SQLite).
# Optional: --postgres, --observability (AIOps / LLMOps / DataOps).
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
WITH_OBSERVABILITY=0
DETACH=(-d)

usage() {
  cat <<'EOF'
Usage: ./docker-all-up.sh [--postgres] [--observability] [--foreground] [-h|--help]

  --postgres        Also start Postgres (overrides default SQLite app DB path).
                    Equivalent to USE_POSTGRES=1.
  --observability   Also start Prometheus, Grafana, Phoenix, Loki
                    (AIOps / LLMOps / DataOps). Equivalent to USE_OBSERVABILITY=1.
  --foreground      Run compose in the foreground (no -d).
  -h, --help        Show this help.

Default stack: Redis + Jaeger + OTEL Collector.
App DB defaults to SQLite unless DB_BACKEND=postgres in the repo-root .env.
EOF
}

for arg in "$@"; do
  case "${arg}" in
    --postgres)
      WITH_POSTGRES=1
      ;;
    --observability)
      WITH_OBSERVABILITY=1
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
if [[ "${USE_OBSERVABILITY:-0}" == "1" ]]; then
  WITH_OBSERVABILITY=1
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
MSG="Starting Redis, Jaeger, and OTEL Collector"
if [[ "${WITH_POSTGRES}" -eq 1 ]]; then
  PROFILES+=(--profile postgres)
  MSG="${MSG}, Postgres"
fi
if [[ "${WITH_OBSERVABILITY}" -eq 1 ]]; then
  PROFILES+=(--profile observability)
  MSG="${MSG}, Prometheus, Grafana, Phoenix, Loki, coa_observability_api"
fi
echo "${MSG}..."

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

if [[ "${WITH_OBSERVABILITY}" -eq 1 && -f "${REPO_ENV}" ]]; then
  if ! grep -q '^OTEL_EXPORTER_OTLP_ENDPOINT=' "${REPO_ENV}"; then
    printf '\nOTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317\n' >> "${REPO_ENV}"
  fi
  if ! grep -q '^PHOENIX_OTLP_ENDPOINT=' "${REPO_ENV}"; then
    printf 'PHOENIX_OTLP_ENDPOINT=http://localhost:4319\n' >> "${REPO_ENV}"
  fi
  if ! grep -q '^PROMETHEUS_METRICS_PORT=' "${REPO_ENV}"; then
    printf 'PROMETHEUS_METRICS_PORT=9108\n' >> "${REPO_ENV}"
  fi
  echo "Ensured OTEL / Phoenix / metrics env keys in ${REPO_ENV}"
fi

echo
echo "Local infra is up."
echo "  Redis:          localhost:${REDIS_PORT:-6379}"
echo "  Jaeger UI:      http://localhost:${JAEGER_UI_PORT:-16686}"
echo "  OTEL (OTLP):    localhost:${OTEL_GRPC_PORT:-4317} (gRPC) / :${OTEL_HTTP_PORT:-4318} (HTTP)"
if [[ "${WITH_POSTGRES}" -eq 1 ]]; then
  echo "  Postgres:       localhost:${POSTGRES_PORT:-5432} (user/password: postgres/postgres, db: council)"
else
  echo "  Postgres:       not started (app default: SQLite). Re-run with --postgres to enable."
fi
if [[ "${WITH_OBSERVABILITY}" -eq 1 ]]; then
  echo "  Prometheus:     http://localhost:${PROMETHEUS_PORT:-9090}"
  echo "  Grafana:        http://localhost:${GRAFANA_PORT:-3000} (admin/admin) — dashboard: Council LLMOps Overview"
  echo "  Phoenix LLMOps: http://localhost:${PHOENIX_PORT:-6006}"
  echo "  Loki:           http://localhost:${LOKI_PORT:-3100}"
  echo "  Obs API:        http://localhost:${COA_OBS_API_PORT:-8088}  (POST /v1/obs/feed, OpenAPI /docs)"
  echo "  App /metrics:   http://localhost:${PROMETHEUS_METRICS_PORT:-9108}/metrics (when OBS_TASK_EMIT_METRICS=true)"
else
  echo "  Observability:  not started. Re-run with --observability for Prometheus/Grafana/Phoenix/Loki/coa_observability_api."
fi
echo
echo "Status: ${SCRIPT_DIR}/docker-all-status.sh"
