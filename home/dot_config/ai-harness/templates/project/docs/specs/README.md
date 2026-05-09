# Specs

Document status: ready.

Specs capture resolved product context for one feature or change. They are temporary working artifacts, not replacements for durable docs.

Do not create a spec just to restate an already clear task. A clear issue, review finding, or approved user request may be enough when acceptance criteria and risk are explicit.

Run primary spec review before durable planning when a full spec or PRD exists, or when acceptance criteria are still being shaped.

Name specs:

```text
YYYY-MM-DD-<feature>.md
```

Each spec should include:

- goal
- problem
- users
- MVP scope
- non-goals
- domain terms
- user stories
- acceptance criteria
- implementation decisions
- testing decisions
- docs impact
- risks
- open questions
- vertical slices

Prompt:

```text
Use write-spec.
Turn the resolved context into the lightest acceptance artifact. Use docs/specs/YYYY-MM-DD-<feature>.md only if a full spec is needed, then split it into vertical slices with AFK/HITL labels.
```

Review prompt:

```text
Use spec-review on docs/specs/YYYY-MM-DD-<feature>.md.
Review product goal, MVP boundary, acceptance criteria, vertical slices, domain language, testing decisions, docs impact, and open risks.
```
