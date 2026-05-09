# AI Harness Hooks

These scripts are conservative building blocks for Claude Code or Codex hook systems.

They are not connected to global settings by default. Wire them at the project level first, then promote globally only after they are quiet enough for daily use.

Recommended use:

- `block-dangerous-bash.sh` for destructive shell command checks and common shell-based secret reads.
- `protect-sensitive-read.sh` for `Read` pre-tool checks on `.env`, private keys, credentials, and secret files.
- `protect-sensitive-write.sh` for `Edit`/`Write`/`MultiEdit` pre-tool checks on sensitive files and direct lockfile edits.
- `protect-sensitive-files.sh` as a compatibility wrapper when a tool cannot split read/write hooks yet.
- `session-context.sh` for short session-start context when a tool supports context-injection hooks.

## Expected Payload

These scripts are intended for `PreToolUse`-style hooks. They accept JSON on stdin and also tolerate raw text for simple adapters.
If `jq` is unavailable, the scripts use a small POSIX `sed` fallback for `tool_name`, `file_path`, `path`, and Bash `command`.

Common fields:

```json
{
  "tool_name": "Read",
  "tool_input": {
    "file_path": ".env"
  }
}
```

For Bash:

```json
{
  "tool_name": "Bash",
  "tool_input": {
    "command": "git reset --hard"
  }
}
```

## Smoke Tests

```sh
printf '%s' '{"tool_name":"Bash","tool_input":{"command":"git reset --hard"}}' | ./block-dangerous-bash.sh
printf '%s' '{"tool_name":"Read","tool_input":{"file_path":".env"}}' | ./protect-sensitive-read.sh
printf '%s' '{"tool_name":"Edit","tool_input":{"file_path":"pnpm-lock.yaml"}}' | ./protect-sensitive-write.sh
```

Each command above should exit non-zero. `.env.example`, `.env.sample`, and `.env.template` are allowed so agents can inspect onboarding templates. Test project-specific hook wiring locally before promoting it globally.

To verify the no-`jq` fallback on macOS-like systems:

```sh
printf '%s' '{"tool_name":"Read","tool_input":{"file_path":".env"}}' | PATH=/bin ./protect-sensitive-read.sh
```
