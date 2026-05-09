#!/bin/sh
set -eu

if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  branch="$(git branch --show-current 2>/dev/null || true)"
  printf 'Session context:\n'
  if [ -n "$branch" ]; then
    printf '- Git branch: %s\n' "$branch"
  fi
  git status --short 2>/dev/null | sed -n '1,20p' | sed 's/^/- Change: /'
fi
