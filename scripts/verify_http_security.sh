#!/usr/bin/env bash
set -euo pipefail

url="${1:?Usage: verify_http_security.sh <health-url>}"
headers_file="$(mktemp)"
body_file="$(mktemp)"
trap 'rm -f "$headers_file" "$body_file"' EXIT

curl \
  --fail \
  --silent \
  --show-error \
  --retry 12 \
  --retry-delay 5 \
  --dump-header "$headers_file" \
  --output "$body_file" \
  "$url"

assert_header() {
  local name="$1"
  local expected="$2"
  local actual

  actual="$(tr -d '\r' < "$headers_file" | sed -n "s/^${name}:[[:space:]]*//Ip" | tail -n 1)"
  if [[ "$actual" != "$expected" ]]; then
    echo "Expected ${name}: ${expected}; received: ${actual:-<missing>}" >&2
    exit 1
  fi
}

assert_header "X-Content-Type-Options" "nosniff"
assert_header "X-Frame-Options" "DENY"
assert_header "Referrer-Policy" "no-referrer"
assert_header "Permissions-Policy" "camera=(), microphone=(), geolocation=()"

echo "Public HTTPS health and defensive headers verified for ${url}."
