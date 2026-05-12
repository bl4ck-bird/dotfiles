---
name: using-git-worktrees
description: Use when starting a vertical slice that needs isolation from the current workspace, before executing a multi-task plan, or when the host environment has not already provided an isolated workspace.
---

# Using Git Worktrees

Ensure work happens in an isolated workspace. Prefer host-native worktree tooling. Fall back
to manual `git worktree add` only when no native tool exists. Never fight the harness.

This skill is the harness-wide SSOT for worktree creation, detection, and cleanup. Other
skills (`subagent-driven-development` Workspace Isolation, `ship-check` Finishing Options) reference this
file instead of duplicating the rules.

**Core principle**: detect existing isolation first → use native tools → fall back to git.
Owner-of-creation owns cleanup.

## When To Use

- Before `subagent-driven-development` starts a multi-task plan that should not pollute the user's main
  tree.
- For broad refactors that cross module boundaries.
- For any vertical slice the user wants reviewable as a branch / PR.
- When `test-driven-development` is about to make non-trivial changes the user wants to keep
  reversible.

Skip when:

- The host environment already created an isolated workspace (Step 0 detects this).
- The change is Tiny / local per `using-bb-harness` Workflow Weight.
- The user explicitly chose to work in place.

## Step 0 — Detect Existing Isolation

Before creating anything, check whether you are already in an isolated workspace.

```bash
GIT_DIR=$(cd "$(git rev-parse --git-dir)" 2>/dev/null && pwd -P)
GIT_COMMON=$(cd "$(git rev-parse --git-common-dir)" 2>/dev/null && pwd -P)
BRANCH=$(git branch --show-current)
```

**Submodule guard**: `GIT_DIR != GIT_COMMON` is also true inside a git submodule. Verify you
are not in a submodule before concluding "already in a worktree":

```bash
# If this returns a path, you are in a submodule — treat as a normal repo.
git rev-parse --show-superproject-working-tree 2>/dev/null
```

- **If `GIT_DIR != GIT_COMMON` and not a submodule**: already in a linked worktree. Skip to
  Step 3. Do not create another worktree.
- **If `GIT_DIR == GIT_COMMON` or in a submodule**: normal repo checkout.

Report with branch state:

- On a branch: "Already in isolated workspace at `<path>` on branch `<name>`."
- Detached HEAD: "Already in isolated workspace at `<path>` (detached HEAD, externally
  managed). Branch creation deferred to `ship-check` Finishing Options."

If no isolation exists and the user has not declared a worktree preference, ask for consent
before creating one. Honor a declared preference without asking. If the user declines,
work in place and skip to Step 3.

## Step 1 — Create An Isolated Workspace

Two mechanisms. Try them in this order.

### 1a. Host-Native Worktree Tool (preferred)

If the host agent provides a worktree facility (a Claude Code tool named `EnterWorktree`,
a slash command like `/worktree`, a Codex helper, or a project-specific script), use it
and skip to Step 3.

Native tools handle directory placement, branch creation, registration, and cleanup
automatically. Using `git worktree add` when a native tool exists creates phantom state the
host cannot see or manage, and breaks `ship-check` cleanup provenance.

### 1b. Git Worktree Fallback

Use this only when Step 1a does not apply.

#### Directory Selection

Follow this priority. Explicit user preference always wins over observed state.

1. **Declared preference** in `AGENTS.md`, `CLAUDE.md`, `docs/AGENT_WORKFLOW.md`, or chat
   instructions. Use it without asking.
2. **Existing project-local directory**:
   ```bash
   ls -d .worktrees 2>/dev/null     # preferred (hidden)
   ls -d worktrees 2>/dev/null      # alternative
   ```
   If both exist, `.worktrees` wins.
3. **Project-local default**: `.worktrees/` at the project root.

The BB Harness does **not** use a global worktree path (e.g.
`~/.config/superpowers/worktrees/`). Project-local keeps the workspace discoverable by
project-level tooling and lefthook hooks.

#### Safety Verification (project-local only)

Verify the directory is git-ignored before creating the worktree:

```bash
git check-ignore -q .worktrees 2>/dev/null || git check-ignore -q worktrees 2>/dev/null
```

If not ignored, add to `.gitignore`, commit the change (small dedicated commit), then
proceed. Skipping this risks committing worktree contents.

#### Create The Worktree

```bash
LOCATION=".worktrees"                                  # or chosen path
path="$LOCATION/$BRANCH_NAME"
git worktree add "$path" -b "$BRANCH_NAME"
cd "$path"
```

**Sandbox fallback**: if `git worktree add` fails with a permission error, tell the user
the sandbox blocked worktree creation and you are working in place instead. Then continue
with Step 3 in the current directory.

## Step 2 — (reserved)

Step 2 in the upstream skill aligned project setup with worktree creation. In the BB
Harness, dependency installation is user-managed by default
(`project-scaffold` Defaults). Move directly to Step 3.

## Step 3 — Project Setup (User-Managed)

Auto-detection of dependencies is allowed; *running* installs is not, unless the user
explicitly authorized it for this session.

Suggest and assume:

```bash
# Detect manifests and propose commands; do not execute without approval.
[ -f package.json ]   && echo "Suggested: npm install (or pnpm/yarn)"
[ -f Cargo.toml ]     && echo "Suggested: cargo build"
[ -f pyproject.toml ] && echo "Suggested: uv sync (or poetry install)"
[ -f go.mod ]         && echo "Suggested: go mod download"
```

If the user already approved running setup commands for this session (e.g. in
`subagent-driven-development` Workspace Isolation Baseline-first rule), run them.

## Step 4 — Verify Clean Baseline

Run the project's narrowest meaningful test suite, type check, or lint to confirm the
workspace starts clean:

```bash
# Use the project-appropriate command. Apply verification-before-completion —
# read the output in this response.
npm test / cargo test / pytest -x / go test ./...
```

- **Tests pass**: report ready.
- **Tests fail**: distinguish pre-existing failures from regressions caused by worktree
  creation. Ask the user before proceeding — do not silently start work on a red baseline.

### Report Format

```text
Worktree ready at <full-path>
Branch: <name>
Baseline: <N> tests, <M> failures (pre-existing / new / clean)
Ready to: <next skill or action>
```

## Cleanup

Worktree cleanup happens at `ship-check` Finishing Options (Merge or Discard). The rule:

- **Cleanup ownership**: only whoever created a worktree removes it. Worktrees created via
  this skill are owned by this skill (and cleaned up by `ship-check`).
- **Project-local provenance**: worktrees under `.worktrees/` or `worktrees/` (the paths
  this skill creates) are owned by the BB Harness. Cleanup is allowed.
- **Host-owned provenance**: worktrees outside those paths are owned by the host (native
  tool or external agent). Do not remove them — the host owns their lifecycle.

Cleanup steps (from `ship-check`):

```bash
MAIN_ROOT=$(git -C "$(git rev-parse --git-common-dir)/.." rev-parse --show-toplevel)
cd "$MAIN_ROOT"
git worktree remove "$WORKTREE_PATH"
git worktree prune
```

Never run `git worktree remove` from inside the worktree being removed — it fails
silently. Always `cd` to the main repo root first.

Order for merge:

1. Merge succeeds.
2. Cleanup worktree.
3. Delete the branch (`git branch -d`).

Reversing this fails because `git branch -d` refuses while the worktree references the
branch.

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
| Neither exists | Use declared preference, else default `.worktrees/`. |
| Directory not ignored | Add to `.gitignore` + commit, then proceed. |
| Permission error on create | Sandbox fallback, work in place, report. |
| Tests fail during baseline | Report, distinguish pre-existing from new, ask. |
| Detached HEAD | Branch creation deferred to `ship-check`. |

## Common Mistakes

- **Fighting the harness**: using `git worktree add` when a native tool exists. → Use the
  native tool.
- **Skipping Step 0**: creating a nested worktree inside an existing one. → Always detect
  first.
- **Skipping ignore verification**: worktree contents get tracked, polluting `git status`
  in the main tree. → Always `git check-ignore` before creating.
- **Running install without approval**: violates user-managed dependency rule. → Suggest;
  do not execute.
- **Cleaning up host-owned worktrees**: leaves the host with phantom state. → Only clean
  up paths this skill created.
- **Removing a worktree from inside it**: silent failure. → `cd` to main repo root first.

## Red Flags

Never:

- Create a worktree when Step 0 detects existing isolation.
- Use `git worktree add` when a native worktree tool is available.
- Skip Step 1a by jumping straight to Step 1b.
- Create a project-local worktree without verifying the directory is git-ignored.
- Skip baseline test verification.
- Proceed silently with failing baseline tests.
- Run `git worktree remove` from inside the worktree being removed.
- Remove a worktree this skill did not create.

Always:

- Run Step 0 detection first.
- Prefer host-native tools over the git fallback.
- Verify directory is ignored for project-local worktrees.
- Read fresh baseline test output in this response (per
  `verification-before-completion`).
- Distinguish pre-existing failures from regressions.
- Honor cleanup provenance.
