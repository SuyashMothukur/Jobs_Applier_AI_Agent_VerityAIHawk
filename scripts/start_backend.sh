#!/usr/bin/env bash
# Start the AIHawk API with optional port override.
set -euo pipefail

export BACKEND_PORT="${BACKEND_PORT:-8001}"
echo "Starting AIHawk API on port ${BACKEND_PORT}..."
exec python run_backend.py
