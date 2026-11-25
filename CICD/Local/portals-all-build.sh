#!/usr/bin/env bash
# Build all Portals Angular apps. Ignores extra CLI args (so
# `npm run local:portals:all:build # comment` cannot break ng build).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

echo "=== Portals all:build ==="

echo
echo "-- customer-portal --"
npm --prefix "${REPO_ROOT}/Portals/customer-portal" run build

echo
echo "-- admin-portal --"
npm --prefix "${REPO_ROOT}/Portals/admin-portal" run build

echo
echo "Portals build complete."
