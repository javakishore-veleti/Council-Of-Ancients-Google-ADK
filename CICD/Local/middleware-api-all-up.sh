#!/usr/bin/env bash
# Start middleware APIs: observability Docker stack + coa_agents_api (host).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
PID_FILE="${SCRIPT_DIR}/.coa-agents-api.pid"
LOG_FILE="${SCRIPT_DIR}/.coa-agents-api.log"

bash "${SCRIPT_DIR}/docker-all-up.sh" --observability

export PYTHONPATH="${REPO_ROOT}/Middleware/API-Services:${REPO_ROOT}/Middleware:${REPO_ROOT}:${PYTHONPATH:-}"
export COA_OBS_API_URL="${COA_OBS_API_URL:-http://localhost:8088}"

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

PORT="${COA_AGENTS_API_PORT:-8090}"

if [[ -f "${PID_FILE}" ]]; then
  old_pid="$(cat "${PID_FILE}" 2>/dev/null || true)"
  if [[ -n "${old_pid}" ]] && kill -0 "${old_pid}" 2>/dev/null; then
    echo "coa_agents_api already running (pid ${old_pid}) on :${PORT}"
    exit 0
  fi
  rm -f "${PID_FILE}"
fi

cd "${REPO_ROOT}"
echo "Starting coa_agents_api on http://0.0.0.0:${PORT} (background; log: ${LOG_FILE})..."
nohup uv run uvicorn coa_agents_api.presentation.app:app \
  --host 0.0.0.0 --port "${PORT}" \
  > "${LOG_FILE}" 2>&1 &
echo $! > "${PID_FILE}"
sleep 2
if kill -0 "$(cat "${PID_FILE}")" 2>/dev/null; then
  echo "coa_agents_api started (pid $(cat "${PID_FILE}"))"
  echo "  Agents:  http://localhost:${PORT}/docs  POST /v1/council/deliberate"
  echo "  Obs API: http://localhost:8088/docs     POST /v1/obs/feed"
else
  echo "coa_agents_api failed to start; see ${LOG_FILE}" >&2
  rm -f "${PID_FILE}"
  exit 1
fi
