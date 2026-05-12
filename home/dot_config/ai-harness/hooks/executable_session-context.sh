#!/bin/sh
set -eu

if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  branch="$(git branch --show-current 2>/dev/null || true)"
  printf 'Session context:\n'
  if [ -n "$branch" ]; then
    printf '- Git branch: %s\n' "$branch"
  fi
  git status --short 2>/dev/null | sed -n '1,20p' | sed 's/^/- Change: /'

  # BB Harness bootstrap reminder: surface when the repo references the harness
  # so the agent invokes `using-bb-harness` before non-trivial replies.
  if grep -lE 'BB Harness|using-bb-harness' \
       AGENTS.md CLAUDE.md docs/AGENT_WORKFLOW.md 2>/dev/null | head -1 >/dev/null; then
    printf '\n'
    printf 'BB Harness detected. Before any non-trivial action, invoke `using-bb-harness`\n'
    printf 'to verify the next phase, or invoke the directly matching skill when the task\n'
    printf 'obviously maps to one (e.g., `bug-diagnosis` for a bug, `test-driven-development` for a\n'
    printf 'small behavior change). Skipping is only valid for trivial questions.\n'
  fi
fi
