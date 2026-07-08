#!/bin/sh
set -eu

# PreToolUse guard for Bash commands.
# Exit codes: 0 = allow; 2 = block (Claude Code treats exit 2 as "block, feed
# stderr to the model"; any other non-zero exit is a non-blocking error).
#
# Checks run per command segment (split on `;`, `|`, `&`) so flags from one
# command cannot satisfy another command's pattern (`rm old.txt && grep -rf p .`
# is allowed). Quotes and backslashes are stripped before matching so quoting
# cannot hide a command (`sh -c "git reset --hard"`, `"git" reset --hard`).

payload="$(cat)"
command="$payload"
scan="$payload"

if command -v jq >/dev/null 2>&1; then
  extracted="$(printf '%s' "$payload" | jq -r '.tool_input.command // .command // empty' 2>/dev/null || true)"
  if [ -n "$extracted" ]; then
    command="$extracted"
    scan="$extracted"
  fi
else
  extracted="$(printf '%s' "$payload" | sed -n 's/.*"command"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')"
  if [ -n "$extracted" ]; then
    command="$extracted"
    # sed extraction stops at the first escaped quote; keep scanning the raw
    # payload too so a truncated tail cannot hide a dangerous suffix.
    scan="$extracted $payload"
  fi
fi

# Normalize: lowercase, join lines, strip quotes/backslashes, collapse spaces.
normalized="$(printf '%s' "$scan" | tr '[:upper:]' '[:lower:]' | tr '\n' ' ' | sed "s/[\"'\\\\]/ /g; s/[[:space:]][[:space:]]*/ /g")"

git_command='(^|[[:space:]])git([[:space:]]+(-c|--git-dir|--work-tree|--namespace)[=[:space:]][^[:space:]]+|[[:space:]]+-[^[:space:]]+)*[[:space:]]+'
reader_command='[[:space:]](cat|less|grep|sed|awk)[[:space:]]'

block() {
  printf '%s Get explicit user approval and use the tool permission/escalation flow before running: %s\n' "$1" "$command" >&2
  exit 2
}

# Split on command separators; evaluate each segment independently.
# set -f: segments are expanded unquoted below; never glob them against the cwd.
set -f
IFS='
'
for segment in $(printf '%s' "$normalized" | tr ';|&' '\n'); do
  seg=" $segment "

  if printf '%s' "$seg" | grep -Eq '[[:space:]]rm[[:space:]]' \
    && printf '%s' "$seg" | grep -Eq '[[:space:]](--recursive|-[^[:space:]]*r[^[:space:]]*)[[:space:]]' \
    && printf '%s' "$seg" | grep -Eq '[[:space:]](--force|-[^[:space:]]*f[^[:space:]]*)[[:space:]]'; then
    block 'Blocked dangerous command.'
  fi

  if printf '%s' "$seg" | grep -Eq "${git_command}reset[[:space:]]" \
    && printf '%s' "$seg" | grep -Eq '[[:space:]]--hard[[:space:]]'; then
    block 'Blocked dangerous command.'
  fi

  if printf '%s' "$seg" | grep -Eq "${git_command}clean[[:space:]]" \
    && printf '%s' "$seg" | grep -Eq '[[:space:]](-[^[:space:]]*f[^[:space:]]*|--force)[[:space:]]' \
    && ! printf '%s' "$seg" | grep -Eq '[[:space:]](-[^[:space:]]*n[^[:space:]]*|--dry-run)[[:space:]]'; then
    block 'Blocked dangerous command.'
  fi

  if printf '%s' "$seg" | grep -Eq "${git_command}push[[:space:]]" \
    && printf '%s' "$seg" | grep -Eq '[[:space:]](-[^[:space:]]*f[^[:space:]]*|--force|--force-with-lease|--force-if-includes)[=[:space:]]|[[:space:]]\+[^[:space:]]+'; then
    block 'Blocked dangerous command.'
  fi

  if printf '%s' "$seg" | grep -Eq '[[:space:]]chmod[[:space:]]' \
    && printf '%s' "$seg" | grep -Eq '[[:space:]](--recursive|-[^[:space:]]*r[^[:space:]]*)[[:space:]]' \
    && printf '%s' "$seg" | grep -Eq '[[:space:]]0?777[[:space:]]'; then
    block 'Blocked dangerous command.'
  fi

  if printf '%s' "$seg" | grep -Eq '[[:space:]]dd[[:space:]]+if='; then
    block 'Blocked dangerous command.'
  fi

  env_seg="$(printf '%s' "$seg" | sed -E 's/\.env\.(example|sample|template)/ /g')"
  if printf '%s' "$env_seg" | grep -Eq "$reader_command" \
    && printf '%s' "$env_seg" | grep -Eq '(^|[[:space:]/])\.env([[:space:].]|$)'; then
    block 'Blocked command that may expose secrets.'
  fi

  # Credential filenames are blocked only for reader commands so legitimate key
  # *use* stays allowed (`ssh -i ~/.ssh/id_rsa`, `chmod 600 ~/.ssh/id_rsa`).
  # Public keys (`*.pub`) are stripped before matching.
  cred_seg="$(printf '%s' "$seg" | sed -E 's/(id_rsa|id_ed25519)[^[:space:]]*\.pub/ /g')"
  if printf '%s' "$cred_seg" | grep -Eq "$reader_command" \
    && printf '%s' "$cred_seg" | grep -Eq 'id_rsa|id_ed25519|credentials\.json|private-key|private_key|secrets\.'; then
    block 'Blocked command that may expose secrets.'
  fi
done

exit 0
