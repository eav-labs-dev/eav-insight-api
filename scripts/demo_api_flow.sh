#!/usr/bin/env bash
set -euo pipefail

API_BASE_URL="${API_BASE_URL:-http://localhost:8000}"
DEMO_EMAIL="${DEMO_EMAIL:-admin@example.com}"
DEMO_PASSWORD="${DEMO_PASSWORD:-ChangeMe123!}"
TMP_DIR="$(mktemp -d)"

cleanup() {
  rm -rf "$TMP_DIR"
}
trap cleanup EXIT

json_value() {
  local file_path="$1"
  local expression="$2"
  python - "$file_path" "$expression" <<'PY'
import json
import sys

file_path = sys.argv[1]
expression = sys.argv[2]

with open(file_path, "r", encoding="utf-8") as file:
    data = json.load(file)

value = data
for part in expression.split("."):
    if part.isdigit():
        value = value[int(part)]
    else:
        value = value[part]

print(value)
PY
}

request() {
  local label="$1"
  shift
  echo
  echo "==> $label"
  curl --fail --silent --show-error "$@"
  echo
}

echo "Running EAV Insight API demo against: $API_BASE_URL"
echo "Demo user: $DEMO_EMAIL"

request "Health check" "$API_BASE_URL/api/v1/health" > "$TMP_DIR/health.json"
cat "$TMP_DIR/health.json"
echo

curl --fail --silent --show-error \
  -X POST "$API_BASE_URL/api/v1/auth/token" \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"$DEMO_EMAIL\", \"password\": \"$DEMO_PASSWORD\"}" \
  > "$TMP_DIR/token.json"

TOKEN="$(json_value "$TMP_DIR/token.json" access_token)"
echo

echo "==> Login succeeded"
echo "Received bearer token."

request "Current user" \
  "$API_BASE_URL/api/v1/auth/me" \
  -H "Authorization: Bearer $TOKEN" \
  > "$TMP_DIR/me.json"
cat "$TMP_DIR/me.json"
echo

curl --fail --silent --show-error \
  -X POST "$API_BASE_URL/api/v1/reports" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Field Operations Intake",
    "summary": "Demo report created through the API demo script.",
    "status": "submitted",
    "source": "demo-script"
  }' \
  > "$TMP_DIR/report.json"

REPORT_ID="$(json_value "$TMP_DIR/report.json" id)"
echo

echo "==> Created report"
cat "$TMP_DIR/report.json"
echo

request "Filtered report list" \
  "$API_BASE_URL/api/v1/reports?search=Field&status=submitted&source=demo-script&sort_by=created_at&sort_order=desc&limit=10&offset=0" \
  -H "Authorization: Bearer $TOKEN" \
  > "$TMP_DIR/reports.json"
cat "$TMP_DIR/reports.json"
echo

curl --fail --silent --show-error \
  -X POST "$API_BASE_URL/api/v1/documents" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"report_id\": \"$REPORT_ID\",
    \"filename\": \"field-operations-intake.pdf\",
    \"content_type\": \"application/pdf\",
    \"storage_path\": \"demo/field-operations-intake.pdf\",
    \"size_bytes\": 4096
  }" \
  > "$TMP_DIR/document.json"

echo

echo "==> Created document metadata"
cat "$TMP_DIR/document.json"
echo

request "Filtered document list" \
  "$API_BASE_URL/api/v1/documents?search=field&content_type=application/pdf&min_size_bytes=1&sort_by=created_at&sort_order=desc&limit=10&offset=0" \
  -H "Authorization: Bearer $TOKEN" \
  > "$TMP_DIR/documents.json"
cat "$TMP_DIR/documents.json"
echo

echo

echo "==> Validation error example"
curl --silent --show-error \
  -X POST "$API_BASE_URL/api/v1/reports" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "No"}'
echo

echo

echo "Demo API flow completed."
