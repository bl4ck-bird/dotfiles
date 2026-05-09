# Reviews And Handoffs

Document status: ready.

Store substantial review records and session handoffs here.

Name reviews:

```text
YYYY-MM-DD-<topic>-<review-type>.md
YYYY-MM-DD-<topic>-handoff.md
```

Review records should include:

- artifact reviewed
- reviewer type
- findings
- fixes applied or accepted risk
- verification after fixes

Handoffs should include:

- current goal
- docs to read
- decisions made
- completed slices
- changed files
- verification evidence
- open risks
- next action

Prompt:

```text
Write a handoff note in docs/reviews/YYYY-MM-DD-<topic>-handoff.md.
Include goal, docs to read, decisions, completed slices, changed files, verification, risks, and next action.
Update docs/CURRENT.md before clearing.
```
