#!/usr/bin/env bash

for item in $(find -executable -type f | grep update_); do
  echo $item
done
