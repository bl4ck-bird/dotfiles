@AGENTS.md

# Claude Code Notes

- Use the local BB Harness skills as the project workflow source of truth.
- Use project docs as the durable source of truth when they conflict with temporary chat context.

## Session Bootstrap

- Invoke `using-bb-harness` at session start. Self-disables when this repo's markers are absent
  (safe to invoke universally).
- Read and update `docs/CURRENT.md` at phase boundaries so next session knows active phase and next
  action.
- Before clearing context, update `docs/CURRENT.md` and write a handoff note in `docs/reviews/`.

## Default Skill Flow

For non-trivial work, the typical chain:

```text
product-discovery → pressure-test → domain-modeling        (discovery, as needed)
write-spec   (with Self-Review)                            (acceptance)
write-plan   (with Self-Review)                            (plan)
using-git-worktrees                                        (workspace isolation)
subagent-driven-development  OR  executing-plans-inline    (execution)
  per task:
    test-driven-development
    spec-compliance-review
    code-quality-review
    security-review     (when triggered)
    second-review       (High-Risk Surface)
    receiving-review    (between reviewer feedback and fix)
verification-before-completion                             (every completion claim)
docs-sync
ship-check
```

Smaller paths:

- Trivial / local change: `test-driven-development` → `ship-check`.
- Bug: `bug-diagnosis` → (companion files when needed) → `test-driven-development` for the fix →
  review.
- Independent investigations (2+ unrelated): `dispatching-parallel-agents`.
- Bounded autonomous repetition: `bounded-loop` (only after goal, scope, allowed autonomous
  actions, iteration budget, verification gate, and stop conditions are explicit).

## Reviewer Subagents

Four reviewer subagents wired (in `~/.claude/agents/`):

- `spec-compliance-reviewer` — binary check after each implementation slice.
- `code-quality-reviewer` — DDD/SOLID/file-size/Coverage Matrix/docs-drift after spec-compliance
  passes.
- `security-reviewer` — when diff touches auth, secrets, crypto, deletion, untrusted input,
  sensitive data, or destructive operations.
- `second-reviewer` — Codex fallback only; Codex is default integration for independent
  double-check via `second-review`.

Inspect worker output via `spec-compliance-review` → `code-quality-review`; add `security-review`
and `second-review` when triggered. Apply `receiving-review` to each reviewer's findings before
applying fixes (verify, push back if wrong, apply one at a time).

## Coding Workers

Use a coding worker (Codex or equivalent) only for a scoped vertical slice with clear files and
verification. Controller stays in the main agent and runs two-stage review per
`subagent-driven-development`.

## Severity And Result Vocabulary

- **Severity**: Critical / Important / Minor (definitions in
  `~/.config/ai-harness/skills/using-bb-harness/severity-definitions.md`).
- **Result**: `Ready to merge? Yes / With fixes / No` (binary ✅/❌ for `spec-compliance-review`).
- **Stop condition**: hard stop after 2 review-fix cycles per channel
  (`using-bb-harness/review-rules.md`).

## When To Ask `second-review` (Codex)

- Required: change touches a High-Risk Surface (security, data-loss, money, auth, crypto, deletion,
  core architecture).
- Strongly consider: large diff + weak tests, broad refactor crossing modules, primary agent stuck,
  bounded automation proposed for user-facing work.
- Optional otherwise. Self-Review + spec-compliance + code-quality is sufficient for routine work.
