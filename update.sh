#!/usr/bin/env bash

set -euo pipefail

SCRIPTS=(
  ./assets/update_htmx
  ./assets/update_analytics
  ./assets/update_sentry
  ./content/utils/base16/update_data.py
  ./content/post/update_dates.py
)

for item in "${SCRIPTS[@]}"; do
  if [ -x "$item" ]; then
    echo "Running $item"
    "$item"
  else
    echo "Skipping non-executable file: $item" >&2
  fi
done
