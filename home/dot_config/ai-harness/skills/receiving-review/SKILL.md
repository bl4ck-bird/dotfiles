---
name: receiving-review
description: Use when receiving any review feedback (spec-compliance, code-quality, security, second, or external) — before applying fixes verify against codebase, push back if wrong, apply one item at a time, YAGNI check.
---

# Receiving Review

Review feedback requires technical evaluation, not blind implementation.

**Core rule**: Verify before implementing. Ask before assuming. Technical correctness over
agreeableness.

## When To Use

- Whenever a review skill or reviewer subagent returns findings.
- Before applying any fix from `spec-compliance-review`, `code-quality-review`,
  `security-review`, `second-review`, or human review.
- When in doubt about whether a finding should be acted on.

## Response Pattern

```text
1. READ:       Read all findings before reacting.
2. UNDERSTAND: Restate each finding's technical requirement in your own words.
3. VERIFY:     Check the finding against the actual codebase, tests, and acceptance artifact.
4. EVALUATE:   Is this technically correct for THIS project? Does it break anything?
5. RESPOND:    Acknowledge correct findings, push back on wrong ones with reasoning.
6. IMPLEMENT:  One item at a time. Run verification after each.
```

## Forbidden Responses

Never write:

- "You're absolutely right!"
- "Great point!" / "Excellent feedback!"
- "Thanks for catching that!" / any gratitude expression
- "Let me implement all that now" before verification

Instead: restate the technical change, ask if unclear, push back if wrong, or just apply the
fix and show the diff.

## Unclear Findings

```text
IF any finding is unclear:
  STOP. Do not implement anything yet.
  ASK the reviewer (or user) to clarify the unclear items.

Reason: findings may be related. Partial understanding leads to wrong implementation.
```

Example: reviewer returns 6 findings, you understand 1, 2, 3, 6. Items 4, 5 unclear.

- ❌ Wrong: apply 1, 2, 3, 6 now and ask about 4, 5 later.
- ✅ Right: "Items 1, 2, 3, 6 understood. Need clarification on 4 and 5 before applying any
  fix."

## YAGNI Check

If a finding says "implement properly" or "add the missing X":

```text
1. grep the codebase for actual callers/usage of the affected code.
2. If unused: ask "<X> is not called anywhere. Remove it (YAGNI) instead of building it out?"
3. If used: implement properly.
```

Reviewers can suggest building speculative features. The user, not the reviewer, decides
whether YAGNI applies.

## When To Push Back

Push back with technical reasoning when:

- The finding would break existing accepted behavior or passing tests.
- The reviewer lacks context the diff does not show (legacy compatibility, prior decisions,
  approved scope).
- The finding violates YAGNI for this project.
- The fix conflicts with an approved plan or durable decision.
- The finding is in code untouched by this diff (out-of-scope per
  `using-bb-harness` Review Scope Guard).

How to push back:

- Cite the file, test, or decision that contradicts the finding.
- Ask specifically what evidence the reviewer used.
- Involve the user if the disagreement is architectural.

## Acknowledging Correct Findings

When a finding is correct, just fix it and show the change:

```text
✅ "Fixed at <file:line>. <One-line description of the change.>"
✅ "Removed the unused <X> per YAGNI."
✅ [Apply the fix. The diff itself confirms you heard the feedback.]
```

Do not write apologies, gratitude, or long explanations.

## Order Of Application

For multi-finding reviews, apply in this order:

1. **Critical** — bugs, security, data loss, broken accepted behavior.
2. **Important** — architecture, missing tests, error handling.
3. **Minor** — style, docs polish.

Apply one finding at a time. Run the relevant verification (focused test, type check, linter,
or manual check) after each before moving to the next.

## Correcting Wrong Push-Back

If you pushed back and turned out to be wrong:

```text
✅ "Checked <X>. You were correct — implementing now."
```

State it factually and apply the fix. No long apology, no over-explanation.

## Common Mistakes

| Mistake | Fix |
| --- | --- |
| Performative agreement | Restate the change or just apply it |
| Blind implementation | Verify against codebase first |
| Batch fixes without testing | One at a time, test each |
| Assuming reviewer is right | Check if the fix breaks existing behavior |
| Avoiding push back | Technical correctness over comfort |
| Partial implementation | Clarify all unclear items first |
| Cannot verify, proceed anyway | State the limit, ask for direction |

## Bottom Line

Reviewer findings are *suggestions to evaluate*, not orders to execute.

Verify. Question if needed. Then implement, one item at a time.
