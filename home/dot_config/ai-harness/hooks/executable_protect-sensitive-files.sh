#!/bin/sh
set -eu

payload="$(cat)"
target="$payload"
tool_name=""

if command -v jq >/dev/null 2>&1; then
  extracted="$(printf '%s' "$payload" | jq -r '.tool_input.file_path // .tool_input.path // .file_path // .path // empty' 2>/dev/null || true)"
  if [ -n "$extracted" ]; then
    target="$extracted"
  fi
  tool_name="$(printf '%s' "$payload" | jq -r '.tool_name // .tool // empty' 2>/dev/null || true)"
else
  extracted="$(printf '%s' "$payload" | sed -n 's/.*"file_path"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')"
  if [ -z "$extracted" ]; then
    extracted="$(printf '%s' "$payload" | sed -n 's/.*"path"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')"
  fi
  if [ -n "$extracted" ]; then
    target="$extracted"
  fi
  tool_name="$(printf '%s' "$payload" | sed -n 's/.*"tool_name"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')"
  if [ -z "$tool_name" ]; then
    tool_name="$(printf '%s' "$payload" | sed -n 's/.*"tool"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')"
  fi
fi

case "$target" in
  *".env.example"|*".env.sample"|*".env.template")
    exit 0
    ;;
  *".env"|*".env."*|*"id_rsa"*|*"id_ed25519"*|*"credentials.json"*|*"secrets."*|*"private-key"*|*"private_key"*)
    printf 'Blocked direct access to sensitive file: %s\n' "$target" >&2
    exit 1
    ;;
  *"package-lock.json"|*"pnpm-lock.yaml"|*"yarn.lock"|*"Cargo.lock"|*"poetry.lock"|*"Pipfile.lock"*)
    case "$tool_name" in
      Read|Glob|Grep)
        exit 0
        ;;
      *)
        printf 'Avoid direct lockfile edits. Use the package manager instead: %s\n' "$target" >&2
        exit 1
        ;;
    esac
    ;;
esac

exit 0
