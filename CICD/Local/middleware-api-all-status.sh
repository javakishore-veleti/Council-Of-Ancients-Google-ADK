#!/usr/bin/env bash
# Status for middleware APIs: Docker obs stack + coa_agents_api.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="${SCRIPT_DIR}/.coa-agents-api.pid"
PORT="${COA_AGENTS_API_PORT:-8090}"

bash "${SCRIPT_DIR}/docker-all-status.sh"

echo
echo "=== coa_agents_api (host) ==="
if [[ -f "${PID_FILE}" ]]; then
  pid="$(cat "${PID_FILE}" 2>/dev/null || true)"
  if [[ -n "${pid}" ]] && kill -0 "${pid}" 2>/dev/null; then
    echo "  process: running (pid ${pid})"
  else
    echo "  process: stale pid file (${PID_FILE})"
  fi
else
  echo "  process: no pid file (not started via middleware-api-all-up.sh)"
fi

if command -v curl >/dev/null 2>&1; then
  if curl -sf -m 2 "http://127.0.0.1:${PORT}/healthz" >/dev/null 2>&1; then
    echo "  healthz: ok  http://127.0.0.1:${PORT}/healthz"
  else
    echo "  healthz: not reachable at http://127.0.0.1:${PORT}/healthz"
  fi
fi

echo
echo "Tips:"
echo "  Start:  npm run local:middleware:api:all:start"
echo "  Status: npm run local:middleware:api:all:status"
echo "  Stop:   npm run local:middleware:api:all:stop"
