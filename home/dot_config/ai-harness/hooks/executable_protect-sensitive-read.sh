#!/bin/sh
set -eu

payload="$(cat)"
target="$payload"

if command -v jq >/dev/null 2>&1; then
  extracted="$(printf '%s' "$payload" | jq -r '.tool_input.file_path // .tool_input.path // .file_path // .path // empty' 2>/dev/null || true)"
  if [ -n "$extracted" ]; then
    target="$extracted"
  fi
else
  extracted="$(printf '%s' "$payload" | sed -n 's/.*"file_path"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')"
  if [ -z "$extracted" ]; then
    extracted="$(printf '%s' "$payload" | sed -n 's/.*"path"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')"
  fi
  if [ -n "$extracted" ]; then
    target="$extracted"
  fi
fi

case "$target" in
  *".env.example"|*".env.sample"|*".env.template")
    exit 0
    ;;
  *".env"|*".env."*|*"id_rsa"*|*"id_ed25519"*|*"credentials.json"*|*"secrets."*|*"private-key"*|*"private_key"*)
    printf 'Blocked read of sensitive file: %s\n' "$target" >&2
    exit 1
    ;;
esac

exit 0
