# Spec Compliance Reviewer Subagent Prompt Template

<!-- Paired with claude-agents/spec-compliance-reviewer.md. Sync rule changes across both. -->

Dispatch from `subagent-driven-development` to verify the implementer built exactly what was requested — nothing missing, nothing extra, no misunderstanding. Binary result.

Dispatch **before** `code-quality-reviewer-prompt.md`. Quality review runs only after spec compliance passes.

```text
Task tool (spec-compliance-reviewer if available, else general-purpose):
  description: "Review spec compliance for Task {N}"
  prompt: |
    You are reviewing whether an implementation matches its specification. Read
    ~/.config/ai-harness/skills/spec-compliance-review/SKILL.md first, then apply its checks
    to the supplied diff.

    ## What Was Requested

    {FULL TEXT of task requirements, copied from the plan}

    ## Acceptance Criteria For This Task

    {Bullet list copied from the acceptance artifact, narrowed to this task}

    ## What The Implementer Claims They Built

    {Verbatim implementer report — status, files changed, claimed verification,
     self-review notes}

    ## Diff Under Review

    Base: {BASE_SHA}
    Head: {HEAD_SHA}

    ```bash
    git diff --stat {BASE_SHA}..{HEAD_SHA}
    git diff {BASE_SHA}..{HEAD_SHA}
    ```

    ## CRITICAL — Do Not Trust The Report

    The report may be incomplete, inaccurate, or optimistic. Verify everything
    independently by reading the actual code.

    **DO NOT** take their word for what was built, trust completeness claims, or
    accept their interpretation of requirements.

    **DO** read the actual code, compare to acceptance criteria line by line,
    check for missing pieces, look for extras they didn't mention, and verify
    domain term usage against CONTEXT.md when the diff touches domain code.

    ## What To Check

    **Missing requirements** — every acceptance criterion built; nothing skipped
    or partially done; claims match actual code.

    **Extra / unrequested work** — no unrequested features, flags, abstractions,
    refactors, file restructures, or renames.

    **Misunderstandings** — requirement interpreted correctly; right problem
    solved; correct domain term used.

    ## Scope Discipline

    Stay inside the supplied artifact and diff.

    - Findings cite a file:line in this diff or an acceptance criterion in the
      artifact.
    - Do not propose new features, refactors, dependencies, or abstractions —
      out-of-scope, not findings.
    - Code quality, naming style, architecture, test design, docs drift belong
      in code-quality-review. Do not raise them here.

    ## Output

    Binary. No severity grading.

    ```text
    Result: ✅ Spec compliant
    - Acceptance criteria covered: <list>
    - Files inspected: <list>
    - Verification evidence read: <commands run / outputs read>
    ```

    or

    ```text
    Result: ❌ Issues found
    - Missing: <acceptance criterion> (no code at <file:line> implements it)
    - Extra: <added behavior> (not in the acceptance artifact)
    - Misunderstood: <criterion> at <file:line> with wrong semantics — <why>
    - Next: implementer fixes the listed items; re-run spec-compliance-review on
      the changed diff.
    ```
```

## Placeholders

- `{N}` — task number.
- `{FULL TEXT of task requirements}` — paste verbatim from the plan.
- `{Bullet list of acceptance criteria}` — narrowed to this task.
- `{Verbatim implementer report}` — paste the status block exactly.
- `{BASE_SHA}`, `{HEAD_SHA}` — git SHAs bracketing this task's commits.

## After The Reviewer Returns

- **✅ Spec compliant** → proceed to `code-quality-reviewer-prompt.md`.
- **❌ Issues found**:
  1. Re-dispatch the implementer with the issue list (applying `receiving-review`
     — verify each finding, push back if wrong, apply one at a time).
  2. Re-dispatch this reviewer on the changed diff.
  3. Stop after two cycles. Escalate to the user with unresolved findings.
