#!/usr/bin/env bash
# Stop middleware APIs on the host only (coa_agents_api + coa_admin_api).
# Does NOT stop Docker containers or wipe volumes — use local:containers:all:stop for that.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

stop_pid_file() {
  local name="$1"
  local pid_file="$2"
  local port="$3"

  if [[ -f "${pid_file}" ]]; then
    pid="$(cat "${pid_file}" 2>/dev/null || true)"
    if [[ -n "${pid}" ]] && kill -0 "${pid}" 2>/dev/null; then
      echo "Stopping ${name} (pid ${pid})..."
      kill "${pid}" 2>/dev/null || true
      pkill -P "${pid}" 2>/dev/null || true
      sleep 1
      kill -9 "${pid}" 2>/dev/null || true
    fi
    rm -f "${pid_file}"
  elif command -v lsof >/dev/null 2>&1; then
    pids="$(lsof -tiTCP:"${port}" -sTCP:LISTEN 2>/dev/null || true)"
    if [[ -n "${pids}" ]]; then
      echo "Stopping stray listeners on :${port}: ${pids}"
      # shellcheck disable=SC2086
      kill ${pids} 2>/dev/null || true
    fi
  fi
}

stop_pid_file "coa_agents_api" "${SCRIPT_DIR}/.coa-agents-api.pid" "${COA_AGENTS_API_PORT:-8090}"
stop_pid_file "coa_admin_api" "${SCRIPT_DIR}/.coa-admin-api.pid" "${COA_ADMIN_API_PORT:-8094}"

echo "Middleware APIs are down (containers left running)."
