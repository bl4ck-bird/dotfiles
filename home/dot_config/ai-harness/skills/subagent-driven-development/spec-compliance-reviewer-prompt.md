# Spec Compliance Reviewer Subagent Prompt Template

Use this template when dispatching a `spec-compliance-review` subagent from
`subagent-driven-development`.

**Purpose**: verify the implementer built exactly what was requested — nothing missing,
nothing extra, no misunderstanding. Binary result.

Dispatch **before** `code-quality-reviewer-prompt.md`. Quality review only runs after
spec compliance passes.

```text
Task tool (spec-compliance-reviewer if available, else general-purpose):
  description: "Review spec compliance for Task {N}"
  prompt: |
    You are reviewing whether an implementation matches its specification. Read the
    authoritative checklist in ~/.claude/skills/spec-compliance-review/SKILL.md
    first, then apply its checks to the supplied diff.

    ## What Was Requested

    {FULL TEXT of task requirements, copied from the plan}

    ## Acceptance Criteria For This Task

    {Bullet list copied from the acceptance artifact, narrowed to this task}

    ## What The Implementer Claims They Built

    {Verbatim copy of the implementer's report — status, files changed, claimed
     verification, self-review notes}

    ## Diff Under Review

    Base: {BASE_SHA}
    Head: {HEAD_SHA}

    ```bash
    git diff --stat {BASE_SHA}..{HEAD_SHA}
    git diff {BASE_SHA}..{HEAD_SHA}
    ```

    ## CRITICAL — Do Not Trust The Report

    The implementer finished. Their report may be incomplete, inaccurate, or
    optimistic. You MUST verify everything independently by reading the actual code.

    **DO NOT:**
    - Take their word for what they implemented.
    - Trust their claims about completeness.
    - Accept their interpretation of requirements.

    **DO:**
    - Read the actual code they wrote.
    - Compare it to the acceptance criteria, line by line.
    - Check for missing pieces they claimed to implement.
    - Look for extra features they did not mention.
    - Verify domain term usage against CONTEXT.md if the diff touches domain code.

    ## What To Check

    **Missing requirements**

    - Did the implementer build everything the acceptance criteria require?
    - Are any criteria skipped or partially done?
    - Did the report claim something works but the code does not actually do it?

    **Extra / unrequested work**

    - Did the implementer add features, flags, abstractions, or refactors that were
      not requested?
    - Did they add "nice to haves" outside the approved scope?
    - Did they restructure files or rename identifiers without explicit instruction?

    **Misunderstandings**

    - Did they interpret a requirement differently than the artifact intends?
    - Did they solve the wrong problem?
    - Did they implement the right feature using the wrong domain term?

    ## Scope Discipline

    Stay inside the supplied artifact and diff.

    - Findings must cite a file:line in this diff or an acceptance criterion in the
      artifact.
    - Do not propose new features, refactors, dependencies, or abstractions. Those
      are out-of-scope improvements — not findings.
    - Code quality, naming style, architecture, test design, and docs drift belong
      in code-quality-review. Do not raise them here.

    ## Output

    Binary result. No severity grading.

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
- `{Verbatim implementer report}` — paste the status block exactly as the
  implementer returned it.
- `{BASE_SHA}`, `{HEAD_SHA}` — git SHAs bracketing this task's commits.

## After The Reviewer Returns

- **✅ Spec compliant**: proceed to `code-quality-reviewer-prompt.md`.
- **❌ Issues found**:
  1. Re-dispatch the implementer with the issue list (applying `receiving-review`
     in the implementer prompt — verify each finding, push back if wrong, apply
     one at a time).
  2. Re-dispatch this reviewer on the changed diff.
  3. Stop after two cycles. Escalate to the user with the unresolved findings.
