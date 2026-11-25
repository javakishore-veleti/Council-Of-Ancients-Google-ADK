#!/usr/bin/env bash
# Stop middleware APIs: coa_agents_api (host) + observability Docker stack.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="${SCRIPT_DIR}/.coa-agents-api.pid"

if [[ -f "${PID_FILE}" ]]; then
  pid="$(cat "${PID_FILE}" 2>/dev/null || true)"
  if [[ -n "${pid}" ]] && kill -0 "${pid}" 2>/dev/null; then
    echo "Stopping coa_agents_api (pid ${pid})..."
    kill "${pid}" 2>/dev/null || true
    # Also stop child uvicorn if nohup left a process tree
    pkill -P "${pid}" 2>/dev/null || true
    sleep 1
    kill -9 "${pid}" 2>/dev/null || true
  fi
  rm -f "${PID_FILE}"
else
  # Best-effort: free the agents port if a stray uvicorn is listening
  PORT="${COA_AGENTS_API_PORT:-8090}"
  if command -v lsof >/dev/null 2>&1; then
    pids="$(lsof -tiTCP:"${PORT}" -sTCP:LISTEN 2>/dev/null || true)"
    if [[ -n "${pids}" ]]; then
      echo "Stopping stray listeners on :${PORT}: ${pids}"
      # shellcheck disable=SC2086
      kill ${pids} 2>/dev/null || true
    fi
  fi
fi

bash "${SCRIPT_DIR}/docker-all-down.sh" "$@"
echo "Middleware APIs are down."
