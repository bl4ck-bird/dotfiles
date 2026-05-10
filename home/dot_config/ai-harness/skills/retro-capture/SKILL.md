---
name: retro-capture
description: Use when ship-check or any review reports memory candidates or retro insights that should persist beyond the current session.
---

# Retro Capture

Persist non-obvious learnings from a completed slice, review, or shipped change so future agent
sessions and project work do not lose them. Implements the gstack "Retro" phase and bridges the
harness Memory Candidates pattern with the host agent's memory system.

## When To Trigger

Run when:

- `ship-check` completes substantial work and produced retro lines.
- A review skill (`spec-review`, `pressure-test`, `implementation-review`, `test-review`,
  `architecture-review`) reported "Memory candidates" in its output.
- A bug fix or incident exposed a rule that future work should follow.
- The user explicitly requests "remember this."

Do not run for trivial sessions, code-only patterns visible in git history, or one-off chat
context.

## Memory Type Classification

Classify each candidate using the host agent's memory model (Claude global memory uses these four
types; other hosts should map equivalently):

- **User**: durable facts about the user's role, expertise, or preferences. Mostly global.
- **Feedback**: rules the user gave or implicitly accepted about how to do work. Global if it
  applies across projects; project-local if specific to this codebase.
- **Project**: ongoing work context, deadlines, ownership, in-flight decisions. Project-local
  primarily.
- **Reference**: pointers to external systems (issue tracker, dashboards, runbooks).

## Persistence Location

Decide global vs project-local using these rules:

- **Global** (host agent's memory directory, e.g. `~/.claude/projects/<harness>/memory/`):
  - Applies across projects.
  - Non-obvious; would not be reconstructable from code or git history.
  - Useful at the start of a future session before any code is read.
- **Project-local** (`docs/reviews/YYYY-MM-DD-retro-<topic>.md` or `docs/DECISIONS/`):
  - Specific to this codebase, team, or product context.
  - Useful when picking up the project after a long pause.
  - May be referenced from `docs/CURRENT.md`.
- **Neither (skip)**:
  - The fact is in code, git log, lockfiles, or visible artifacts.
  - The lesson is too narrow to recur.
  - The candidate restates a known harness rule.

## Memory Entry Format

Match the host agent's memory format. Example for Claude global memory:

```markdown
---
name: <short title>
description: <one-line cue used to decide relevance later>
type: <user|feedback|project|reference>
---

<Rule or fact, one paragraph.>

**Why:** <reason; often a past incident or strong preference>
**How to apply:** <when/where the rule kicks in>
```

For project-local files, use a similar header inside the chosen markdown file plus a brief context
section linking to the originating review or decision.

## Frequency

- Run once per substantial phase boundary (ship-check, end of a major slice, end of a debugging
  session). Do not capture after every small step.
- During `bounded-loop`, capture only at iteration budget end or successful exit.

## Anti-Patterns

- Saving code patterns ("we use X library") — code is the source.
- Saving git activity summaries — `git log` is authoritative.
- Saving fix recipes for one-off bugs — the commit message is enough.
- Saving rules already present in `AGENTS.md` or `CLAUDE.md`.
- Saving things "just in case" without a clear reuse scenario.

## Output

Report:

- Candidates received and their classification
- Saved entries (path, type, one-line summary)
- Skipped candidates and the reason
- Follow-up if memory revealed a project documentation gap
