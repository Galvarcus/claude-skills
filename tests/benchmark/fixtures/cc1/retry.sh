#!/usr/bin/env bash
set -euo pipefail

attempt=1
until curl -fsS "$API_URL/health"; do
  if [ "$attempt" -ge 5 ]; then
    exit 1
  fi
  if [ "$attempt" -eq 2 ]; then
    sleep 30
  fi
  attempt=$((attempt + 1))
done
