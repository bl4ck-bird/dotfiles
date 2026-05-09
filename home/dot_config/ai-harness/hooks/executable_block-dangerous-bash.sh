#!/bin/sh
set -eu

payload="$(cat)"
command="$payload"

if command -v jq >/dev/null 2>&1; then
  extracted="$(printf '%s' "$payload" | jq -r '.tool_input.command // .command // empty' 2>/dev/null || true)"
  if [ -n "$extracted" ]; then
    command="$extracted"
  fi
else
  extracted="$(printf '%s' "$payload" | sed -n 's/.*"command"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')"
  if [ -n "$extracted" ]; then
    command="$extracted"
  fi
fi

case "$command" in
  *"rm -rf "*|*"rm -fr "*|*"git reset --hard"*|*"git clean -fd"*|*"git push --force"*|*"chmod -R 777"*|*"dd if="*)
    printf 'Blocked dangerous command. Ask the user for explicit approval before running: %s\n' "$command" >&2
    exit 1
    ;;
  *"cat .env"*|*"cat ./.env"*|*"cat "*/.env*|*"less .env"*|*"less "*/.env*|*"grep "*".env"*|*"sed "*".env"*|*"awk "*".env"*|*"id_rsa"*|*"id_ed25519"*|*"credentials.json"*|*"private-key"*|*"private_key"*|*"secrets."*)
    printf 'Blocked command that may expose secrets. Ask the user for explicit approval before running: %s\n' "$command" >&2
    exit 1
    ;;
esac

exit 0
