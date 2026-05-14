---
name: project-scaffold
description: Use when starting a new project or adding/refining AGENTS.md, CLAUDE.md, docs, hooks, skills, or reviewer agents in an existing repo.
---

# Project Scaffold

Set up a repo so Claude Code, Codex, and other coding agents share the same durable project context.

## Workflow

1. Inspect repo root, existing docs, package manifests, tests, current agent config.
2. Preserve existing files. Target exists → update only when user asked for that exact file; otherwise report suggested change.
3. Propose scaffold profile and exact file/action list.
4. Run human decision gate before creating files or changing repo shape.
5. Create only approved files and directories.
6. Add `.claude/`, `.codex/`, `.agents/`, `lefthook.yml` only after user approves.
7. Identify dependency/bootstrap commands when useful; guide user instead of running unless user explicitly asks.
8. End with short report: created files, skipped existing files, approved setup decisions, recommended next setup.

## Scaffold Profiles

Default to smallest profile that preserves restartable context:

- `minimal`: agent instructions, core context, current work, workflow notes.
- `product`: `minimal` + roadmap, testing strategy, specs/plans/reviews folders, architecture, domain model.
- `data-security`: `product` + data and security models for persistence, auth, secrets, deletion, sync, external integrations, sensitive data.
- `full`: `data-security` + context map and formal decision record template; only when user wants heavier governance skeleton.

```text
minimal:
  AGENTS.md
  CLAUDE.md
  CONTEXT.md
  docs/AGENT_WORKFLOW.md
  docs/CURRENT.md

product:
  minimal +
  docs/TESTING_STRATEGY.md
  docs/specs/README.md
  docs/plans/README.md
  docs/reviews/README.md
  docs/ROADMAP.md
  docs/ARCHITECTURE.md
  docs/DOMAIN_MODEL.md

data-security:
  product +
  docs/DATA_MODEL.md
  docs/SECURITY_MODEL.md

full:
  data-security +
  CONTEXT-MAP.md
  docs/DECISIONS/0000-template.md
```

## Human Decision Gate

New project — ask explicit approval before each:

- `git init`
- scaffold profile and template files
- create `.claude/`, `.codex/`, `.agents/`
- create or install `lefthook.yml`
- package install / stack bootstrap commands (only when user explicitly asks agent to execute)
- initial commit

Existing project — ask before: modifying existing files, adding hooks, changing agent config, changing dependency manifests, executing dependency installation, touching git history. Recommending or recording dependency/bootstrap commands is allowed when assumptions stated and no command executed.

Partial approval → complete approved part, report rest as skipped.

## Lefthook / Pre-Commit Hooks

Load `lefthook-recipes.md` (this dir) when project uses (or considers) a git-hook runner. Companion owns:

- Dependency audit hook recipes per language (`npm audit`, `pip-audit`, `cargo audit`, `govulncheck`, `bundler-audit`).
- Commit-msg rationale enforcement for dependency changes.
- Other hook targets (lint, typecheck, secret scan, full-suite pre-push).
- What belongs in hooks vs skills.

Skip companion when project has no hook runner and is not adopting one.

Harness principle: **trigger automation by hook; judgment lives in skills.** Hooks do not replace `write-plan` Self-Review for dependency adds or `security-review` for high-risk deps.

## Defaults

- `README.md` high-level, onboarding-friendly.
- Durable design rules in focused docs, not README.
- Project instructions specific, short enough to read every session.
- Don't copy global rules into project files unless project needs stricter version.
- Mark scaffolded docs as `stub` until TODOs resolved. Agents may read stub docs for structure but must not treat TODO content as project truth.
- Dependency installation is user-managed by default. Record suggested commands, package manager assumptions, unresolved choices instead of running installs.

## New Project Defaults

Propose `minimal` first unless product idea clearly needs roadmap/domain/architecture/data/security/formal decision records. Explain which profile and why before creating files.

## Existing Project Defaults

- Don't overwrite local conventions.
- Identify current commands from package manifests, Makefiles, CI, README.
- Infer product/domain terms from code only when docs missing.
- Mark inferred claims as uncertain until user confirms.
- Prefer suggested additions over broad rewrites.

## Recommended First Prompts

After scaffolding, suggest:

```text
Use product-discovery to define the product goal, MVP boundary,
non-goals, success metrics, and first vertical slice.
```

```text
Use pressure-test and domain-modeling before writing the first acceptance artifact when assumptions or terms are unclear.
```

```text
Use write-spec when an acceptance artifact is needed. Self-Review covers product
clarity and domain alignment. Then use compact write-plan with Self-Review for
plan hygiene and architecture soundness. Run subagent-driven-development for multi-task plans —
each task uses test-driven-development, then spec-compliance-review, then code-quality-review
(security-review and second-review as triggered). Finish with docs-sync, ship-check,
and an approved commit/stack gate only when needed.
```

Use templates from `~/.config/ai-harness/templates/project/` when creating new files.
