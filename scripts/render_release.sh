#!/usr/bin/env bash
set -euo pipefail

echo "Running EAV Insight API release tasks..."
alembic upgrade head
echo "Release tasks complete."
