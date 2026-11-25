#!/usr/bin/env bash
# Start coa_agents_api (Facilitator + counselors) on the host via uvicorn.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
cd "${REPO_ROOT}"

export PYTHONPATH="${REPO_ROOT}/Middleware/API-Services:${REPO_ROOT}/Middleware:${REPO_ROOT}:${PYTHONPATH:-}"
export COA_OBS_API_URL="${COA_OBS_API_URL:-http://localhost:8088}"

# Load KEY=VALUE from repo-root .env without `source` (avoids shell-eval of
# unquoted paths / WIF resource names). FastAPI also calls load_dotenv().
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

# Dedicated agents port — do not reuse generic PORT=8080 from app .env.
PORT="${COA_AGENTS_API_PORT:-8090}"

echo "Starting coa_agents_api on http://0.0.0.0:${PORT} (docs: /docs)..."
exec uv run uvicorn coa_agents_api.presentation.app:app --host 0.0.0.0 --port "${PORT}"
