#!/usr/bin/env bash
# Expose the local AIHawk backend with a public HTTPS URL for Verity.
set -euo pipefail

PORT="${BACKEND_PORT:-8001}"

echo "Starting Cloudflare tunnel -> http://localhost:${PORT}"
echo "Keep this terminal open while using Verity."
echo ""
npx -y cloudflared tunnel --url "http://localhost:${PORT}"
