#!/bin/sh
set -eu

# Compatibility wrapper for hosts that cannot split read/write hooks.
# Routes to protect-sensitive-read.sh (read tools) or protect-sensitive-write.sh
# (everything else — conservative default) so the path patterns live in exactly
# one place per direction.
# Exit codes: 0 = allow; 2 = block.

payload="$(cat)"
tool_name=""

if command -v jq >/dev/null 2>&1; then
  tool_name="$(printf '%s' "$payload" | jq -r '.tool_name // .tool // empty' 2>/dev/null || true)"
else
  tool_name="$(printf '%s' "$payload" | sed -n 's/.*"tool_name"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')"
  if [ -z "$tool_name" ]; then
    tool_name="$(printf '%s' "$payload" | sed -n 's/.*"tool"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')"
  fi
fi

dir="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"

case "$tool_name" in
  Read|Glob|Grep) child="protect-sensitive-read.sh" ;;
  *) child="protect-sensitive-write.sh" ;;
esac

# The chezmoi source tree keeps the `executable_` prefix; deployed files do not.
if [ ! -f "$dir/$child" ]; then
  child="executable_$child"
fi

printf '%s' "$payload" | sh "$dir/$child"
