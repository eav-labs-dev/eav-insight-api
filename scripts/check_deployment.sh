#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${1:-${DEPLOYED_API_URL:-}}"

if [ -z "$BASE_URL" ]; then
  echo "Usage: scripts/check_deployment.sh <base-url>" >&2
  echo "Example: scripts/check_deployment.sh https://eav-insight-api.onrender.com" >&2
  exit 1
fi

BASE_URL="${BASE_URL%/}"

echo "Checking root endpoint..."
curl --fail --silent --show-error "$BASE_URL/" | python -m json.tool

echo "Checking health endpoint..."
curl --fail --silent --show-error "$BASE_URL/api/v1/health" | python -m json.tool

echo "Deployment smoke check passed: $BASE_URL"
