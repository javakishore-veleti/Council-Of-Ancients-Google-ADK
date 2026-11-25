#!/usr/bin/env bash
# Apply knowledge schema via Liquibase (changelog master) — not raw psql bootstraps.
# Invoked by middleware-api-all-up.sh. Requires Docker + running council-postgres.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
KB_DIR="${REPO_ROOT}/Middleware/API-Services/db/liquibase/knowledge"
LIQUIBASE_IMAGE="${LIQUIBASE_IMAGE:-liquibase/liquibase:4.29}"
DOCKER_NETWORK="${COA_DOCKER_NETWORK:-council-local-net}"
PG_HOST_IN_DOCKER="${COA_PG_HOST_IN_DOCKER:-council-postgres}"
DB_URL="${COA_ADMIN_DATABASE_URL:-${COA_KNOWLEDGE_DATABASE_URL:-postgresql://postgres:postgres@127.0.0.1:5432/council}}"
PGUSER="${POSTGRES_USER:-postgres}"
PGPASSWORD="${POSTGRES_PASSWORD:-postgres}"
PGDATABASE="${POSTGRES_DB:-council}"

if ! command -v docker >/dev/null 2>&1; then
  echo "docker is required to run Liquibase for knowledge schema." >&2
  exit 1
fi

if ! command -v psql >/dev/null 2>&1; then
  echo "psql is required to wait for Postgres readiness." >&2
  exit 1
fi

echo "Waiting for Postgres…"
ready=0
for _ in $(seq 1 60); do
  if docker exec council-postgres pg_isready -U "${PGUSER}" >/dev/null 2>&1 \
    && psql "${DB_URL}" -v ON_ERROR_STOP=1 -c "SELECT 1" >/dev/null 2>&1; then
    ready=1
    break
  fi
  sleep 1
done
if [[ "${ready}" -ne 1 ]]; then
  echo "Postgres not ready after 60s; cannot run Liquibase." >&2
  exit 1
fi

if ! docker network inspect "${DOCKER_NETWORK}" >/dev/null 2>&1; then
  echo "Docker network ${DOCKER_NETWORK} not found (is council-postgres up?)." >&2
  exit 1
fi

run_liquibase() {
  local cmd="$1"
  docker run --rm \
    --network "${DOCKER_NETWORK}" \
    -v "${KB_DIR}:/liquibase/changelog" \
    -w /liquibase/changelog \
    "${LIQUIBASE_IMAGE}" \
    --defaultsFile=liquibase.properties \
    --url="jdbc:postgresql://${PG_HOST_IN_DOCKER}:5432/${PGDATABASE}" \
    --username="${PGUSER}" \
    --password="${PGPASSWORD}" \
    --changelog-file=changelog/db.changelog-master.xml \
    --search-path=/liquibase/changelog \
    "${cmd}"
}

# If schema was applied earlier via bootstrap SQL (no Liquibase history), mark
# current changelogs as ran so update only applies new changesets.
schema_exists="$(psql "${DB_URL}" -tAc "SELECT to_regclass('knowledge.knowledge_source')" | tr -d '[:space:]')"
lb_rows="$(psql "${DB_URL}" -tAc "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'databasechangelog'" | tr -d '[:space:]')"
lb_count=0
if [[ "${lb_rows}" == "1" ]]; then
  lb_count="$(psql "${DB_URL}" -tAc "SELECT COUNT(*) FROM databasechangelog" | tr -d '[:space:]')"
fi

if [[ "${schema_exists}" == "knowledge.knowledge_source" && "${lb_count}" == "0" ]]; then
  echo "Existing knowledge schema without Liquibase history — changelogSync…"
  run_liquibase changelogSync
fi

echo "Liquibase update (knowledge changelog master)…"
if ! run_liquibase update; then
  echo "Liquibase update failed; attempting changelogSync + update (idempotent recovery)…" >&2
  run_liquibase changelogSync
  run_liquibase update
fi

echo "Knowledge schema ready via Liquibase."
