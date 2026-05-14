---
name: using-git-worktrees
description: Use when starting a vertical slice that needs isolation from the current workspace, before executing a multi-task plan, or when the host environment has not already provided an isolated workspace.
---

# Using Git Worktrees

Ensure work happens in an isolated workspace. Prefer host-native worktree tooling. Fall back to manual `git worktree add` only when no native tool exists. Never fight the harness.

Harness-wide SSOT for worktree creation, detection, and cleanup. Other skills (`subagent-driven-development` Workspace Isolation, `ship-check` Finishing Options) reference this file.

**Core principle**: detect existing isolation first → use native tools → fall back to git. Owner-of-creation owns cleanup.

## When To Use

- Before `subagent-driven-development` starts a multi-task plan.
- Broad refactors crossing module boundaries.
- Any vertical slice the user wants reviewable as a branch / PR.
- When `test-driven-development` is about to make non-trivial changes the user wants reversible.

Skip when:

- Host already created an isolated workspace (Step 0 detects this).
- Change is Tiny / local per `using-bb-harness` Workflow Weight.
- User explicitly chose to work in place.

## Step 0 — Detect Existing Isolation

Check before creating anything.

```bash
GIT_DIR=$(cd "$(git rev-parse --git-dir)" 2>/dev/null && pwd -P)
GIT_COMMON=$(cd "$(git rev-parse --git-common-dir)" 2>/dev/null && pwd -P)
BRANCH=$(git branch --show-current)
```

**Submodule guard**: `GIT_DIR != GIT_COMMON` is also true in a submodule. Verify:

```bash
# If this returns a path, you are in a submodule — treat as a normal repo.
git rev-parse --show-superproject-working-tree 2>/dev/null
```

- **`GIT_DIR != GIT_COMMON` and not a submodule**: already in a linked worktree. Skip to Step 3. Do not create another.
- **`GIT_DIR == GIT_COMMON` or in submodule**: normal repo checkout.

Report with branch state:

- On branch: "Already in isolated workspace at `<path>` on branch `<name>`."
- Detached HEAD: "Already in isolated workspace at `<path>` (detached HEAD, externally managed). Branch creation deferred to `ship-check` Finishing Options."

No isolation and no declared preference → ask consent before creating. Honor declared preference without asking. User declines → work in place, skip to Step 3.

## Step 1 — Create An Isolated Workspace

Two mechanisms. Try in order.

### 1a. Host-Native Worktree Tool (preferred)

If host provides a worktree facility (Claude Code `EnterWorktree` tool, `/worktree` slash command, Codex helper, project-specific script), use it and skip to Step 3.

Native tools handle placement, branch creation, registration, and cleanup automatically. Using `git worktree add` when native tool exists creates phantom state, breaks `ship-check` cleanup provenance.

### 1b. Git Worktree Fallback

Use only when Step 1a does not apply.

#### Directory Selection

Priority. Explicit user preference always wins.

1. **Declared preference** in `AGENTS.md`, `CLAUDE.md`, `docs/AGENT_WORKFLOW.md`, or chat. Use without asking.
2. **Existing project-local directory**:
   ```bash
   ls -d .worktrees 2>/dev/null     # preferred (hidden)
   ls -d worktrees 2>/dev/null      # alternative
   ```
   Both exist → `.worktrees` wins.
3. **Project-local default**: `.worktrees/` at project root.

BB Harness does **not** use a global worktree path (e.g. `~/.config/superpowers/worktrees/`). Project-local keeps the workspace discoverable by project tooling and lefthook hooks.

#### Safety Verification (project-local only)

Verify directory is git-ignored before creating:

```bash
git check-ignore -q .worktrees 2>/dev/null || git check-ignore -q worktrees 2>/dev/null
```

Not ignored → add to `.gitignore`, commit (small dedicated commit), proceed. Skipping risks committing worktree contents.

#### Create The Worktree

```bash
LOCATION=".worktrees"                                  # or chosen path
path="$LOCATION/$BRANCH_NAME"
git worktree add "$path" -b "$BRANCH_NAME"
cd "$path"
```

**Sandbox fallback**: `git worktree add` fails with permission error → tell user the sandbox blocked creation, working in place. Continue with Step 3 in current directory.

## Step 2 — (reserved)

Step 2 upstream aligned project setup with worktree creation. In BB Harness, dependency installation is user-managed by default (`project-scaffold` Defaults). Go to Step 3.

## Step 3 — Project Setup (User-Managed)

Auto-detection allowed; *running* installs is not, unless user explicitly authorized this session.

Suggest and assume:

```bash
# Detect manifests and propose commands; do not execute without approval.
[ -f package.json ]   && echo "Suggested: npm install (or pnpm/yarn)"
[ -f Cargo.toml ]     && echo "Suggested: cargo build"
[ -f pyproject.toml ] && echo "Suggested: uv sync (or poetry install)"
[ -f go.mod ]         && echo "Suggested: go mod download"
```

User already approved running setup commands for this session (e.g., `subagent-driven-development` Workspace Isolation Baseline-first rule) → run them.

## Step 4 — Verify Clean Baseline

Run narrowest meaningful test suite, type check, or lint:

```bash
# Use the project-appropriate command. Apply verification-before-completion —
# read the output in this response.
npm test / cargo test / pytest -x / go test ./...
```

- **Pass**: report ready.
- **Fail**: distinguish pre-existing from regression caused by worktree creation. Ask user before proceeding — never silently start on a red baseline.

### Report Format

```text
Worktree ready at <full-path>
Branch: <name>
Baseline: <N> tests, <M> failures (pre-existing / new / clean)
Ready to: <next skill or action>
```

## Cleanup

Cleanup happens at `ship-check` Finishing Options (Merge or Discard). Rules:

- **Cleanup ownership**: only the creator removes it. Worktrees created via this skill are owned by this skill (cleaned by `ship-check`).
- **Project-local provenance**: `.worktrees/` or `worktrees/` paths (this skill's paths) are owned by BB Harness. Cleanup allowed.
- **Host-owned provenance**: worktrees outside those paths are owned by the host (native tool or external agent). Do not remove — host owns lifecycle.

Cleanup steps (from `ship-check`):

```bash
MAIN_ROOT=$(git -C "$(git rev-parse --git-common-dir)/.." rev-parse --show-toplevel)
cd "$MAIN_ROOT"
git worktree remove "$WORKTREE_PATH"
git worktree prune
```

Never run `git worktree remove` from inside the worktree being removed — silent fail. Always `cd` to main repo root first.

Order for merge:

1. Merge succeeds.
2. Cleanup worktree.
3. Delete branch (`git branch -d`).

Reverse fails — `git branch -d` refuses while worktree references the branch.

## Quick Reference

| Situation | Action |
| --- | --- |
| Already in linked worktree | Skip creation (Step 0). |
| In a submodule | Treat as normal repo (Step 0 guard). |
| Host-native worktree tool available | Use it (Step 1a). |
| No native tool | Git worktree fallback (Step 1b). |
| `.worktrees/` exists | Use it (verify ignored). |
| `worktrees/` exists | Use it (verify ignored). |
| Both exist | Use `.worktrees/`. |
| Neither exists | Declared preference, else default `.worktrees/`. |
| Directory not ignored | Add to `.gitignore` + commit, then proceed. |
| Permission error on create | Sandbox fallback, work in place, report. |
| Tests fail during baseline | Report, distinguish pre-existing from new, ask. |
| Detached HEAD | Branch creation deferred to `ship-check`. |

## Common Mistakes

- **Fighting the harness**: `git worktree add` when a native tool exists. → Use native.
- **Skipping Step 0**: nested worktree inside existing one. → Always detect first.
- **Skipping ignore verification**: worktree contents tracked, polluting `git status`. → Always `git check-ignore` first.
- **Running install without approval**: violates user-managed dependency rule. → Suggest; do not execute.
- **Cleaning up host-owned worktrees**: leaves host with phantom state. → Only clean paths this skill created.
- **Removing worktree from inside it**: silent failure. → `cd` to main repo root first.

## Red Flags

Never:

- Create a worktree when Step 0 detects existing isolation.
- Use `git worktree add` when a native worktree tool is available.
- Skip Step 1a by jumping to Step 1b.
- Create a project-local worktree without verifying it is git-ignored.
- Skip baseline test verification.
- Proceed silently with failing baseline tests.
- Run `git worktree remove` from inside the worktree being removed.
- Remove a worktree this skill did not create.

Always:

- Run Step 0 detection first.
- Prefer host-native tools over the git fallback.
- Verify directory is ignored for project-local worktrees.
- Read fresh baseline test output in this response (per `verification-before-completion`).
- Distinguish pre-existing failures from regressions.
- Honor cleanup provenance.
