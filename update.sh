#!/usr/bin/env bash
#
# Central maintenance script runner.
#
# This script automatically discovers and executes all maintenance scripts
# (files named 'update_*') that are tracked by git and are executable.
#
# It uses 'git ls-files' instead of 'find' for security and hygiene:
# 1. Security: Prevents execution of untracked (potentially malicious or accidental) files.
# 2. Hygiene: Respects .gitignore, ensuring artifacts are not executed.

for item in $(git ls-files -- "**/update_*"); do
  if [ -x "$item" ]; then
    echo "Running $item"
    "$item"
  fi
done
