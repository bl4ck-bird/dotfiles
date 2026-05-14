# Reviews And Handoffs

Document status: ready.

Store substantial review records and session handoffs here.

Name reviews:

```text
YYYY-MM-DD-<topic>-<review-type>.md
YYYY-MM-DD-<topic>-handoff.md
YYYY-MM-DD-<topic>-incident.md
```

Review records include:

- artifact reviewed
- reviewer type
- findings
- fixes applied or accepted risk
- verification after fixes

Incident records (post-ship rollback) follow `ship-check` Rollback And Incident Response — what shipped, what broke, blast radius, detection signal, revert commands, verification, root cause or hypothesis, follow-up (test added, durable doc updated, decision recorded).

Handoffs include:

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
