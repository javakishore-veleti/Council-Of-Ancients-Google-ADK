#!/usr/bin/env bash
# Status for all Portals Angular apps.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
PORTALS_DIR="${REPO_ROOT}/Portals"
RUN_DIR="${SCRIPT_DIR}/.portals-run"

# name|relative_path|port
PORTALS=(
  "customer|customer-portal|4200"
  "admin|admin-portal|4201"
)

echo "=== Portals all:status ==="
for entry in "${PORTALS[@]}"; do
  IFS='|' read -r name rel port <<<"${entry}"
  local_dir="${PORTALS_DIR}/${rel}"
  pid_file="${RUN_DIR}/${name}.pid"

  echo
  echo "-- ${name} (port ${port}) --"
  if [[ -d "${local_dir}" ]]; then
    echo "  app dir: present (${rel})"
  else
    echo "  app dir: not created yet (${rel})"
  fi

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

  if command -v lsof >/dev/null 2>&1; then
    listen="$(lsof -tiTCP:"${port}" -sTCP:LISTEN 2>/dev/null || true)"
    if [[ -n "${listen}" ]]; then
      echo "  listen:  :${port} (pids ${listen})"
    else
      echo "  listen:  :${port} free"
    fi
  fi

  if command -v curl >/dev/null 2>&1; then
    code="$(curl -s -o /dev/null -w '%{http_code}' -m 2 "http://127.0.0.1:${port}/" 2>/dev/null || echo 000)"
    echo "  http:    ${code}  http://127.0.0.1:${port}/"
  fi
done

echo
echo "Tips:"
echo "  Start:  npm run local:portals:all:start"
echo "  Status: npm run local:portals:all:status"
echo "  Stop:   npm run local:portals:all:stop"
