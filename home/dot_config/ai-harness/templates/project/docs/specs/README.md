# Specs

Document status: ready.

Specs capture resolved product context for one feature or change. Temporary working artifacts, not
replacements for durable docs.

Do not create a spec just to restate an already clear task. A clear issue, review finding, or
approved user request may be enough when Acceptance Brief fields, acceptance criteria, and risk are
explicit.

Run primary spec review before durable planning when a full spec or PRD exists, or when acceptance
criteria are still being shaped.

For non-trivial work that does not need a full spec, the acceptance source must still include the
canonical fields.

Use the canonical Acceptance Brief fields from `skills/write-spec/SKILL.md` (Light Acceptance Brief
template). Do not re-list fields here.

Name specs:

```text
YYYY-MM-DD-<feature>.md
```

Each full spec follows the Full Spec Template in `skills/write-spec/SKILL.md`. Do not re-list fields
here.

Prompt:

```text
Use write-spec.
Turn the resolved context into the lightest acceptance artifact.
Use docs/specs/YYYY-MM-DD-<feature>.md only if a full spec is needed.
Split it into vertical slices with AFK/HITL labels.
```

Self-Review prompt:

```text
Run write-spec Self-Review on docs/specs/YYYY-MM-DD-<feature>.md.
Check product goal, MVP boundary, acceptance criteria, vertical slices,
domain alignment (terms match CONTEXT.md, aggregates respect bounded
contexts, invariants have proof paths), testing decisions, and docs
impact. Request second-review (Codex) only when triggers apply.
```
