#!/usr/bin/env bash

set -euo pipefail

# An explicit list of scripts to run is used to mitigate command injection.
# Do not use 'find' to dynamically execute scripts.
declare -a scripts=(
  "./assets/update_htmx"
  "./assets/update_analytics"
  "./assets/update_sentry"
  "./content/utils/base16/update_data.py"
  "./content/post/update_dates.py"
)

for item in "${scripts[@]}"; do
  if [ -x "$item" ]; then
    echo "Running $item"
    "$item"
  else
    echo "Skipping non-executable script: $item" >&2
  fi
done
