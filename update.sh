#!/usr/bin/env bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"

for item in $(git ls-files -- "**/update_*"); do
  if [ -x "$item" ]; then
    echo "Running $item"
    "$item"
  fi
done
