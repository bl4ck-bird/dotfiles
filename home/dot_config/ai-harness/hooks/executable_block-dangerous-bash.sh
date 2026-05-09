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

normalized="$(printf '%s' "$command" | tr '[:upper:]' '[:lower:]' | tr '\n' ' ' | sed 's/[[:space:]][[:space:]]*/ /g')"
git_command='(^|[;&|[:space:]])git([[:space:]]+(-c|-c|--git-dir|--work-tree|--namespace)[=[:space:]][^[:space:]]+|[[:space:]]+-[^[:space:]]+)*[[:space:]]+'

if printf '%s' "$normalized" | grep -Eq '(^|[;&|[:space:]])rm[[:space:]]' \
  && printf '%s' "$normalized" | grep -Eq '(^|[[:space:]])(--recursive|-[^[:space:]]*r[^[:space:]]*)([[:space:]]|$)' \
  && printf '%s' "$normalized" | grep -Eq '(^|[[:space:]])(--force|-[^[:space:]]*f[^[:space:]]*)([[:space:]]|$)'; then
  printf 'Blocked dangerous command. Get explicit user approval and use the tool permission/escalation flow before running: %s\n' "$command" >&2
  exit 1
fi

if printf '%s' "$normalized" | grep -Eq "${git_command}reset([[:space:]]|$)" \
  && printf '%s' "$normalized" | grep -Eq '(^|[[:space:]])--hard([[:space:]]|$)'; then
  printf 'Blocked dangerous command. Get explicit user approval and use the tool permission/escalation flow before running: %s\n' "$command" >&2
  exit 1
fi

if printf '%s' "$normalized" | grep -Eq "${git_command}clean([[:space:]]|$)" \
  && printf '%s' "$normalized" | grep -Eq '(^|[[:space:]])(-[^[:space:]]*f[^[:space:]]*|--force)([[:space:]]|$)' \
  && ! printf '%s' "$normalized" | grep -Eq '(^|[[:space:]])(-[^[:space:]]*n[^[:space:]]*|--dry-run)([[:space:]]|$)'; then
  printf 'Blocked dangerous command. Get explicit user approval and use the tool permission/escalation flow before running: %s\n' "$command" >&2
  exit 1
fi

if printf '%s' "$normalized" | grep -Eq "${git_command}push([[:space:]]|$)" \
  && printf '%s' "$normalized" | grep -Eq '(^|[[:space:]])(-[^[:space:]]*f[^[:space:]]*|--force|--force-with-lease|--force-if-includes)([=[:space:]]|$)|(^|[[:space:]])\+[^[:space:]]+'; then
  printf 'Blocked dangerous command. Get explicit user approval and use the tool permission/escalation flow before running: %s\n' "$command" >&2
  exit 1
fi

if printf '%s' "$normalized" | grep -Eq 'chmod[[:space:]]+-r[[:space:]]+777|dd[[:space:]]+if='; then
  printf 'Blocked dangerous command. Get explicit user approval and use the tool permission/escalation flow before running: %s\n' "$command" >&2
  exit 1
fi

env_check=" $normalized "
env_check="$(printf '%s' "$env_check" | sed 's#\([ /]\)\.env\.example\([ ;|&]\)#\1\2#g; s#\([ /]\)\.env\.sample\([ ;|&]\)#\1\2#g; s#\([ /]\)\.env\.template\([ ;|&]\)#\1\2#g')"

if printf '%s' "$normalized" | grep -Eq '(^|[;&|[:space:]])(cat|less|grep|sed|awk)[[:space:]]' \
  && printf '%s' "$env_check" | grep -Eq '(^|[[:space:]/])\.env($|[[:space:];|&.])'; then
  printf 'Blocked command that may expose secrets. Get explicit user approval and use the tool permission/escalation flow before running: %s\n' "$command" >&2
  exit 1
fi

if printf '%s' "$normalized" | grep -Eq 'id_rsa|id_ed25519|credentials\.json|private-key|private_key|secrets\.'; then
  printf 'Blocked command that may expose secrets. Get explicit user approval and use the tool permission/escalation flow before running: %s\n' "$command" >&2
  exit 1
fi

exit 0
