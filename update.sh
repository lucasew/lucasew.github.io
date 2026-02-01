#!/usr/bin/env bash
#
# Master Update Script
#
# This script serves as the single entry point for all project maintenance tasks.
# It automatically discovers and executes any executable script matching the
# pattern `**/update_*` tracked by git.
#
# Usage: ./update.sh
#
# Flow:
# 1. Lists all files matching "**/update_*" using git ls-files.
# 2. Checks if each file is executable.
# 3. Executes it.
#

for item in $(git ls-files -- "**/update_*"); do
  if [ -x "$item" ]; then
    echo "Running $item"
    "$item"
  fi
done
