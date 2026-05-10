---
name: project-scaffold
description: Use when starting a new project or adding/refining AGENTS.md, CLAUDE.md, docs, hooks, skills, or reviewer agents in an existing repo.
---

# Project Scaffold

Set up a repo so Claude Code, Codex, and other coding agents have the same durable project context.

## Workflow

1. Inspect the repository root, existing docs, package manifests, tests, and current agent config.
2. Preserve existing files. If a target exists, update it only when the user asked for that exact
file; otherwise report the suggested change.
3. Propose a scaffold profile and exact file/action list.
4. Run the human decision gate before creating files or changing repository shape.
5. Create only approved files and directories.
6. Add `.claude/`, `.codex/`, `.agents/`, and `lefthook.yml` only after the user approves them for
the project.
7. Identify dependency or bootstrap commands when useful, but guide the user instead of running them
unless the user explicitly asks the agent to execute.
8. End with a short report listing created files, skipped existing files, approved setup decisions,
and recommended next setup.

## Scaffold Profiles

Default to the smallest profile that preserves restartable context:

- `minimal`: agent instructions, core context, current work, and workflow notes.
- `product`: `minimal` plus roadmap, testing strategy, specs/plans/reviews folders, architecture,
  and domain model.
- `data-security`: `product` plus data and security models for projects with persistence, auth,
  secrets, deletion, sync, external integrations, or sensitive data.
- `full`: `data-security` plus context map and a formal decision record template, only when the user
  wants a heavier governance skeleton.

Recommended files:

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

For a new project, ask for explicit approval before each action:

- initialize git with `git init`
- scaffold profile and exact template files
- create `.claude/`, `.codex/`, or `.agents/`
- create or install `lefthook.yml`
- run package installation or stack bootstrapping commands only when the user explicitly asks the
  agent to execute them
- create an initial commit

For an existing project, ask before modifying existing files, adding hooks, changing agent config,
changing dependency manifests, executing dependency installation, or touching git history.
Recommending or recording dependency/bootstrap commands is allowed when assumptions are stated and
no command is executed.

If the user approves only part of the gate, complete the approved part and report the rest as
skipped.

## Lefthook / Pre-Commit Hooks

When the project uses lefthook (or another git hook runner), include hooks for the concerns the
harness cannot enforce from skills alone. Propose; do not install.

### Dependency Audit Hooks

Trigger when manifest files change in staged commits. Run language-appropriate audit tools and
fail the commit on findings the project rejects.

| Manifest changed | Recommended audit |
| --- | --- |
| `package.json`, `package-lock.json`, `pnpm-lock.yaml`, `yarn.lock` | `npm audit` / `pnpm audit` / `yarn npm audit` |
| `requirements.txt`, `pyproject.toml`, `poetry.lock`, `uv.lock` | `pip-audit` / `safety check` |
| `Cargo.toml`, `Cargo.lock` | `cargo audit` |
| `go.mod`, `go.sum` | `govulncheck ./...` |
| `Gemfile`, `Gemfile.lock` | `bundler-audit` |

Recommended commit-msg behavior: when a commit touches a manifest file, require the message body
to mention dependency rationale (added / replaced / upgraded reason, alternatives considered when
relevant). Lefthook can enforce this with a small commit-msg script. The harness rule is
*trigger* automation by hook; the *judgment* (alternatives, license, removal cost) lives in
`plan-review` and `security-review` for high-risk deps.

### Other Hook Targets

- Pre-commit: lint, typecheck, focused test, secret scan (if available).
- Commit-msg: project conventional-commit format if used.
- Pre-push: full test suite (when fast enough).

Hook implementation specifics belong in `lefthook.yml`, not in this skill.

## Defaults

- Keep `README.md` high-level and onboarding-friendly.
- Put durable design rules in focused docs, not in the README.
- Keep project instructions specific and short enough to be read every session.
- Do not copy global rules into project files unless the project needs a stricter version.
- Mark scaffolded docs as `stub` until TODOs are resolved. Agents may read stub docs for structure,
  but must not treat TODO content as project truth.
- Treat dependency installation as user-managed by default. Record suggested commands, package
  manager assumptions, and unresolved choices instead of running installs.

## New Project Defaults

For a new project, propose `minimal` first unless the product idea clearly needs roadmap, domain,
architecture, data, security, or formal decision records. Explain which profile you recommend and
why before creating files.

## Existing Project Defaults

For an existing project:

- Do not overwrite local conventions.
- Identify current commands from package manifests, Makefiles, CI, or README.
- Infer product and domain terms from code only when docs are missing.
- Mark inferred claims as uncertain until the user confirms them.
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
Use write-spec when an acceptance artifact is needed. Run spec-review for full specs,
PRDs, or unclear acceptance criteria. Then use compact write-plan, required plan-review
for non-trivial or multi-slice work, execute-plan with behavior-tdd inside each slice,
implementation-review, test-review when verification is weak or acceptance-critical,
docs-sync, ship-check, and an approved commit/stack gate only when needed.
```

Use templates from `~/.config/ai-harness/templates/project/` when creating new files.
