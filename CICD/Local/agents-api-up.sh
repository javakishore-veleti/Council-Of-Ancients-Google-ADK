#!/usr/bin/env bash
# Start coa_agents_api (Facilitator + counselors) on the host via uvicorn.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
cd "${REPO_ROOT}"

PORT="${COA_AGENTS_API_PORT:-8090}"
export PYTHONPATH="${REPO_ROOT}/Middleware/API-Services:${REPO_ROOT}/Middleware:${REPO_ROOT}:${PYTHONPATH:-}"

if [[ -f "${REPO_ROOT}/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "${REPO_ROOT}/.env"
  set +a
fi

echo "Starting coa_agents_api on http://0.0.0.0:${PORT} (docs: /docs)..."
exec uv run uvicorn coa_agents_api.presentation.app:app --host 0.0.0.0 --port "${PORT}"
