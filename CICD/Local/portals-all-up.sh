#!/usr/bin/env bash
# Start all Portals Angular apps (customer now; admin later).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
PORTALS_DIR="${REPO_ROOT}/Portals"
RUN_DIR="${SCRIPT_DIR}/.portals-run"
mkdir -p "${RUN_DIR}"

# name|relative_path|port|npm_script
PORTALS=(
  "customer|customer-portal|4200|start"
  # "admin|admin-portal|4201|start"   # enable when Portals/admin-portal exists
)

need_npm_install() {
  local app_dir="$1"
  [[ ! -d "${app_dir}/node_modules" ]]
}

start_one() {
  local name="$1" rel="$2" port="$3" script="$4"
  local app_dir="${PORTALS_DIR}/${rel}"
  local pid_file="${RUN_DIR}/${name}.pid"
  local log_file="${RUN_DIR}/${name}.log"

  if [[ ! -d "${app_dir}" ]]; then
    echo "skip ${name}: missing ${app_dir}"
    return 0
  fi

  if [[ -f "${pid_file}" ]]; then
    local old_pid
    old_pid="$(cat "${pid_file}" 2>/dev/null || true)"
    if [[ -n "${old_pid}" ]] && kill -0 "${old_pid}" 2>/dev/null; then
      echo "${name} already running (pid ${old_pid}) on :${port}"
      return 0
    fi
    rm -f "${pid_file}"
  fi

  if need_npm_install "${app_dir}"; then
    echo "Installing deps for ${name}..."
    npm --prefix "${app_dir}" install
  fi

  echo "Starting ${name} portal on http://127.0.0.1:${port} (log: ${log_file})..."
  (
    cd "${app_dir}"
    # Prefer package.json start (includes proxy for customer)
    nohup npm run "${script}" -- --host 127.0.0.1 --port "${port}" \
      > "${log_file}" 2>&1 &
    echo $! > "${pid_file}"
  )

  sleep 2
  if kill -0 "$(cat "${pid_file}")" 2>/dev/null; then
    echo "  ${name}: started (pid $(cat "${pid_file}"))  http://127.0.0.1:${port}/"
  else
    echo "  ${name}: failed to start; see ${log_file}" >&2
    rm -f "${pid_file}"
    return 1
  fi
}

echo "=== Portals all:start ==="
fail=0
for entry in "${PORTALS[@]}"; do
  IFS='|' read -r name rel port script <<<"${entry}"
  start_one "${name}" "${rel}" "${port}" "${script}" || fail=1
done

echo
echo "Tips:"
echo "  Status: npm run local:portals:all:status"
echo "  Stop:   npm run local:portals:all:stop"
exit "${fail}"
