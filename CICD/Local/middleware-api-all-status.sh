#!/usr/bin/env bash
# Status for middleware APIs: Docker obs stack + coa_agents_api + coa_admin_api.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

bash "${SCRIPT_DIR}/docker-all-status.sh"

status_one() {
  local name="$1"
  local pid_file="$2"
  local port="$3"
  echo
  echo "=== ${name} (host) ==="
  if [[ -f "${pid_file}" ]]; then
    pid="$(cat "${pid_file}" 2>/dev/null || true)"
    if [[ -n "${pid}" ]] && kill -0 "${pid}" 2>/dev/null; then
      echo "  process: running (pid ${pid})"
    else
      echo "  process: stale pid file (${pid_file})"
    fi
  else
    echo "  process: no pid file"
  fi
  if command -v curl >/dev/null 2>&1; then
    if curl -sf -m 2 "http://127.0.0.1:${port}/healthz" >/dev/null 2>&1; then
      echo "  healthz: ok  http://127.0.0.1:${port}/healthz"
    else
      echo "  healthz: not reachable at http://127.0.0.1:${port}/healthz"
    fi
  fi
}

status_one "coa_agents_api" "${SCRIPT_DIR}/.coa-agents-api.pid" "${COA_AGENTS_API_PORT:-8090}"
status_one "coa_admin_api" "${SCRIPT_DIR}/.coa-admin-api.pid" "${COA_ADMIN_API_PORT:-8094}"

echo
echo "Tips:"
echo "  Start:  npm run local:middleware:api:all:start"
echo "  Status: npm run local:middleware:api:all:status"
echo "  Stop:   npm run local:middleware:api:all:stop"
