#!/usr/bin/env bash
set -euo pipefail
API=${1:-http://localhost:5000}
echo "Testing health endpoint:"
curl -s "$API/health" | jq .
echo "Testing POST /run (requires API keys):"
curl -s -X POST "$API/run" -H "Content-Type: application/json" \
  -d '{"source":"custom","custom":{"urls":["https://example.com"]},"style":"spicy","max_steps":1}' | jq .
