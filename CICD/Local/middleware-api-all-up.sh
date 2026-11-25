#!/usr/bin/env bash
# Start middleware APIs on the host: knowledge Liquibase + coa_agents_api + coa_admin_api.
# Does NOT start/stop Docker. Containers (Postgres, Redis, obs) must already be up:
#   npm run local:containers:all:start -- --postgres --observability
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
AGENTS_PID="${SCRIPT_DIR}/.coa-agents-api.pid"
AGENTS_LOG="${SCRIPT_DIR}/.coa-agents-api.log"
ADMIN_PID="${SCRIPT_DIR}/.coa-admin-api.pid"
ADMIN_LOG="${SCRIPT_DIR}/.coa-admin-api.log"

if ! docker exec council-postgres pg_isready -U postgres >/dev/null 2>&1; then
  echo "Postgres container not ready. Start containers first:" >&2
  echo "  npm run local:containers:all:start -- --postgres --observability" >&2
  exit 1
fi

export PYTHONPATH="${REPO_ROOT}/Middleware/API-Services:${REPO_ROOT}/Middleware:${REPO_ROOT}:${PYTHONPATH:-}"
export COA_OBS_API_URL="${COA_OBS_API_URL:-http://localhost:8088}"
export COA_ADMIN_DATABASE_URL="${COA_ADMIN_DATABASE_URL:-postgresql://postgres:postgres@localhost:5432/council}"
export COA_KNOWLEDGE_DATABASE_URL="${COA_KNOWLEDGE_DATABASE_URL:-postgresql://postgres:postgres@localhost:5432/council}"

if [[ -f "${REPO_ROOT}/.env" ]]; then
  while IFS= read -r line || [[ -n "${line}" ]]; do
    [[ -z "${line}" || "${line}" =~ ^[[:space:]]*# ]] && continue
    if [[ "${line}" =~ ^([A-Za-z_][A-Za-z0-9_]*)=(.*)$ ]]; then
      key="${BASH_REMATCH[1]}"
      val="${BASH_REMATCH[2]}"
      if [[ "${val}" =~ ^\"(.*)\"$ ]]; then
        val="${BASH_REMATCH[1]}"
      elif [[ "${val}" =~ ^\'(.*)\'$ ]]; then
        val="${BASH_REMATCH[1]}"
      fi
      export "${key}=${val}"
    fi
  done < "${REPO_ROOT}/.env"
fi

bash "${SCRIPT_DIR}/knowledge-db-apply.sh"

start_uvicorn() {
  local name="$1"
  local module="$2"
  local port="$3"
  local pid_file="$4"
  local log_file="$5"

  if [[ -f "${pid_file}" ]]; then
    old_pid="$(cat "${pid_file}" 2>/dev/null || true)"
    if [[ -n "${old_pid}" ]] && kill -0 "${old_pid}" 2>/dev/null; then
      echo "${name} already running (pid ${old_pid}) on :${port}"
      return 0
    fi
    rm -f "${pid_file}"
  fi

  cd "${REPO_ROOT}"
  echo "Starting ${name} on http://0.0.0.0:${port} (log: ${log_file})..."
  nohup uv run uvicorn "${module}" \
    --host 0.0.0.0 --port "${port}" \
    > "${log_file}" 2>&1 &
  echo $! > "${pid_file}"
  sleep 2
  if kill -0 "$(cat "${pid_file}")" 2>/dev/null; then
    echo "${name} started (pid $(cat "${pid_file}"))"
  else
    echo "${name} failed to start; see ${log_file}" >&2
    rm -f "${pid_file}"
    return 1
  fi
}

start_uvicorn "coa_agents_api" "coa_agents_api.presentation.app:app" \
  "${COA_AGENTS_API_PORT:-8090}" "${AGENTS_PID}" "${AGENTS_LOG}"

start_uvicorn "coa_admin_api" "coa_admin_api.presentation.app:app" \
  "${COA_ADMIN_API_PORT:-8094}" "${ADMIN_PID}" "${ADMIN_LOG}"

echo
echo "  Agents: http://localhost:${COA_AGENTS_API_PORT:-8090}/docs"
echo "  Admin:  http://localhost:${COA_ADMIN_API_PORT:-8094}/docs"
echo "  Obs:    http://localhost:8088/docs"
