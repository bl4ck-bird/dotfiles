# Implementation Plans

Document status: ready.

Implementation plans translate reviewed acceptance artifacts into file-mapped, testable work. Keep them compact; link to the acceptance artifact instead of restating it.

Name plans:

```text
YYYY-MM-DD-<feature-or-slice>.md
```

Each plan should include:

- linked acceptance source: spec, PRD, issue, review finding, or approved task
- acceptance review path, accepted-risk note, or reason a separate spec review is unnecessary
- goal
- vertical slice
- file responsibility map
- TDD tasks
- verification commands
- docs impact
- review checkpoints
- residual risks

Prompt:

```text
Use write-plan.
Create docs/plans/YYYY-MM-DD-<feature>.md with acceptance source, file responsibility mapping, TDD steps, verification commands, docs impact, rollback notes, and focused review checkpoints.
```

Review prompt:

```text
Use plan-review on docs/plans/YYYY-MM-DD-<feature>.md.
Confirm the acceptance source is reviewed at the right weight. Review file responsibility, TDD granularity, DDD/SOLID fit, file size risk, docs impact, and verification.
```
