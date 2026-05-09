@AGENTS.md

# Claude Code Notes

- Use the local BB Harness skills as the project workflow source of truth.
- Use project docs as the durable source of truth when they conflict with temporary chat context.
- Use `bb-workflow` at session start, resume, or when the next workflow phase is unclear.
- Read and update `docs/CURRENT.md` at phase boundaries so the next session knows the active phase and next action.
- Use reviewer subagents for architecture, tests, docs, and security when risk justifies it.
- Use Codex or another coding worker only for a scoped vertical slice with clear files and verification. Inspect worker output for acceptance and code quality; run `implementation-review` when the result is substantial, risky, hard to inspect, or required by the plan.
- Use `bounded-loop` only when the goal, scope, allowed autonomous actions, iteration budget, verification gate, and stop conditions are explicit.
- Ask for Codex second review on risky specs, broad implementation plans, large diffs, security-sensitive work, or stuck debugging when available.
- Before clearing context, update `docs/CURRENT.md` and write a handoff note in `docs/reviews/`.
