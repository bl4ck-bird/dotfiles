#!/bin/sh
set -eu

# PreToolUse guard for Read-style tools (Read, Glob, Grep).
# Exit codes: 0 = allow; 2 = block.

payload="$(cat)"
target="$payload"

if command -v jq >/dev/null 2>&1; then
  extracted="$(printf '%s' "$payload" | jq -r '.tool_input.file_path // .tool_input.path // .tool_input.notebook_path // .file_path // .path // empty' 2>/dev/null || true)"
  if [ -n "$extracted" ]; then
    target="$extracted"
  fi
else
  extracted="$(printf '%s' "$payload" | sed -n 's/.*"file_path"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')"
  if [ -z "$extracted" ]; then
    extracted="$(printf '%s' "$payload" | sed -n 's/.*"notebook_path"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')"
  fi
  if [ -z "$extracted" ]; then
    extracted="$(printf '%s' "$payload" | sed -n 's/.*"path"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')"
  fi
  if [ -n "$extracted" ]; then
    target="$extracted"
  fi
fi

# Match case-insensitively: default APFS is case-insensitive, so `.ENV` opens
# the real `.env`. Keep the original spelling for the message.
match="$(printf '%s' "$target" | tr '[:upper:]' '[:lower:]')"

case "$match" in
  *".env.example"|*".env.sample"|*".env.template"|*"id_rsa.pub"|*"id_ed25519.pub")
    exit 0
    ;;
  *".env"|*".env."*|*"id_rsa"*|*"id_ed25519"*|*"credentials.json"*|*"secrets."*|*"private-key"*|*"private_key"*)
    printf 'Blocked read of sensitive file: %s\n' "$target" >&2
    exit 2
    ;;
esac

exit 0
