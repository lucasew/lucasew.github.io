#!/usr/bin/env bash

scripts_to_run=(
  "assets/update_analytics"
  "assets/update_htmx"
  "assets/update_sentry"
  "content/post/update_dates.py"
  "content/utils/base16/update_data.py"
)

for item in "${scripts_to_run[@]}"; do
  if [ -x "$item" ]; then
    echo "Running $item"
    "$item"
  else
    echo "Skipping $item, not executable or not found" >&2
  fi
done
