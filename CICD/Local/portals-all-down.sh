#!/usr/bin/env bash
# Stop all Portals Angular apps started via portals-all-up.sh.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUN_DIR="${SCRIPT_DIR}/.portals-run"

# name|port
PORTALS=(
  "customer|4200"
  "admin|4201"
)

stop_pid_file() {
  local name="$1"
  local pid_file="${RUN_DIR}/${name}.pid"
  if [[ ! -f "${pid_file}" ]]; then
    return 0
  fi
  local pid
  pid="$(cat "${pid_file}" 2>/dev/null || true)"
  if [[ -n "${pid}" ]] && kill -0 "${pid}" 2>/dev/null; then
    echo "Stopping ${name} portal (pid ${pid})..."
    kill "${pid}" 2>/dev/null || true
    pkill -P "${pid}" 2>/dev/null || true
    sleep 1
    kill -9 "${pid}" 2>/dev/null || true
    # ng serve often leaves a child node; sweep port below
  fi
  rm -f "${pid_file}"
}

free_port() {
  local name="$1"
  local port="$2"
  if ! command -v lsof >/dev/null 2>&1; then
    return 0
  fi
  local pids
  pids="$(lsof -tiTCP:"${port}" -sTCP:LISTEN 2>/dev/null || true)"
  if [[ -n "${pids}" ]]; then
    echo "Stopping stray ${name} listeners on :${port}: ${pids}"
    # shellcheck disable=SC2086
    kill ${pids} 2>/dev/null || true
    sleep 1
    # shellcheck disable=SC2086
    kill -9 ${pids} 2>/dev/null || true
  fi
}

echo "=== Portals all:stop ==="
for entry in "${PORTALS[@]}"; do
  IFS='|' read -r name port <<<"${entry}"
  stop_pid_file "${name}"
  free_port "${name}" "${port}"
done

echo "Portals are down."
