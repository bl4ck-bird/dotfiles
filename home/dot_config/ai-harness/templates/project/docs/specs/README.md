# Specs

Document status: ready.

Specs capture resolved product context for one feature or change. They are temporary working artifacts, not replacements for durable docs.

Run primary spec review before implementation planning.

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
Use spec-to-slices.
Turn the resolved context into docs/specs/YYYY-MM-DD-<feature>.md and split it into vertical slices with AFK/HITL labels.
```

Review prompt:

```text
Use review-gate on docs/specs/YYYY-MM-DD-<feature>.md.
Review product goal, MVP boundary, acceptance criteria, vertical slices, domain language, testing decisions, docs impact, and open risks.
```
