#!/usr/bin/env bash

for item in $(git ls-files -- "**/update_*"); do
  if [ -x "$item" ]; then
    echo "Running $item"
    "$item"
  fi
done
