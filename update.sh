#!/usr/bin/env bash

set -euo pipefail

SCRIPTS_TO_RUN=(
  "assets/update_htmx"
  "assets/update_analytics"
  "assets/update_sentry"
  "content/utils/base16/update_data.py"
  "content/post/update_dates.py"
)

for item in "${SCRIPTS_TO_RUN[@]}"; do
  if [ -f "$item" ] && [ -x "$item" ]; then
    echo "Running $item"
    "./$item"
  else
    echo "WARN: Script not found or not executable: $item" >&2
  fi
done
