@AGENTS.md

# Claude Code Notes

- Use the local BB Harness skills as the project workflow source of truth.
- Use project docs as the durable source of truth when they conflict with temporary chat context.
- Use `using-bb-harness` at session start, resume, or when the next workflow phase is unclear.
- Read and update `docs/CURRENT.md` at phase boundaries so the next session knows the active phase
  and next action.
- Use reviewer subagents for spec-compliance, code-quality, security, and independent
  second review when risk justifies it.
- Use a coding worker (Codex or equivalent) only for a scoped vertical slice with clear
  files and verification. Inspect worker output via `spec-compliance-review` then
  `code-quality-review`; run `security-review` and `second-review` when triggered.
- Use `bounded-loop` only when the goal, scope, allowed autonomous actions, iteration budget,
  verification gate, and stop conditions are explicit.
- Ask for `second-review` (host agent's Codex integration when available) on risky specs, broad
  implementation plans, large diffs, security-sensitive work, or stuck debugging.
- Before clearing context, update `docs/CURRENT.md` and write a handoff note in `docs/reviews/`.
