#!/usr/bin/env bash

set -euo pipefail

scripts=(
  ./assets/update_analytics
  ./assets/update_htmx
  ./assets/update_sentry
  ./content/post/update_dates.py
  ./content/utils/base16/update_data.py
)

for item in "${scripts[@]}"; do
  if [ -x "$item" ]; then
    echo "Running $item"
    "$item"
  else
    echo "Skipping non-executable script: $item" >&2
  fi
done
