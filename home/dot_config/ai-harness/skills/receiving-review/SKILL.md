---
name: receiving-review
description: Use when receiving any review feedback (spec-compliance, code-quality, security, second, or external) — before applying fixes verify against codebase, push back if wrong, apply one item at a time, YAGNI check.
---

# Receiving Review

Review feedback requires technical evaluation, not blind implementation.

**Core rule**: Verify before implementing. Ask before assuming. Technical correctness over
agreeableness.

## When To Use

- Any review skill or reviewer subagent returns findings.
- Before applying any fix from `spec-compliance-review`, `code-quality-review`,
  `security-review`, `second-review`, or human review.
- When in doubt about whether a finding should be acted on.

## Response Pattern

```text
1. READ:       All findings before reacting.
2. UNDERSTAND: Restate each finding's technical requirement.
3. VERIFY:     Against actual codebase, tests, acceptance artifact.
4. EVALUATE:   Correct for THIS project? Breaks anything?
5. RESPOND:    Acknowledge correct, push back on wrong with reasoning.
6. IMPLEMENT:  One at a time. Verify after each.
```

## Forbidden Responses

Never write:

- "You're absolutely right!"
- "Great point!" / "Excellent feedback!"
- "Thanks for catching that!" / any gratitude expression
- "Let me implement all that now" before verification

Instead: restate the change, ask if unclear, push back if wrong, or just apply and show diff.

## Unclear Findings

```text
IF any finding is unclear:
  STOP. ASK reviewer (or user) to clarify.
```

Findings may be related. Partial understanding → wrong implementation.

Example: 6 findings, you understand 1, 2, 3, 6. Items 4, 5 unclear.

- ❌ Wrong: apply 1, 2, 3, 6 now and ask about 4, 5 later.
- ✅ Right: "Items 1, 2, 3, 6 understood. Need clarification on 4 and 5 before applying any
  fix."

## YAGNI Check

Finding says "implement properly" or "add the missing X":

```text
1. grep codebase for actual callers/usage.
2. If unused: ask "<X> is not called anywhere. Remove it (YAGNI) instead of building it out?"
3. If used: implement properly.
```

User, not reviewer, decides YAGNI.

## When To Push Back

Push back with technical reasoning when:

- Finding breaks existing accepted behavior or passing tests.
- Reviewer lacks context the diff does not show (legacy compatibility, prior decisions, approved
  scope).
- Finding violates YAGNI.
- Fix conflicts with approved plan or durable decision.
- Finding is out-of-scope (code untouched by diff — see `using-bb-harness` Review Scope Guard).

How: cite file/test/decision that contradicts. Ask what evidence reviewer used. Involve user
if disagreement is architectural.

## Acknowledging Correct Findings

Fix and show:

```text
✅ "Fixed at <file:line>. <One-line description.>"
✅ "Removed the unused <X> per YAGNI."
✅ [Apply the fix. The diff confirms you heard.]
```

No apologies, gratitude, or long explanations.

## Order Of Application

For multi-finding reviews, apply in this order:

1. **Critical** — bugs, security, data loss, broken accepted behavior.
2. **Important** — architecture, missing tests, error handling.
3. **Minor** — style, docs polish.

One at a time. Run relevant verification (focused test, type check, linter, manual) after each.

## Correcting Wrong Push-Back

```text
✅ "Checked <X>. You were correct — implementing now."
```

Factual. Apply the fix. No long apology.

## Common Mistakes

| Mistake | Fix |
| --- | --- |
| Performative agreement | Restate or just apply |
| Blind implementation | Verify against codebase first |
| Batch fixes without testing | One at a time, test each |
| Assuming reviewer is right | Check if fix breaks existing behavior |
| Avoiding push back | Technical correctness over comfort |
| Partial implementation | Clarify all unclear items first |
| Cannot verify, proceed anyway | State the limit, ask for direction |

## Bottom Line

Findings are *suggestions to evaluate*, not orders to execute. Verify. Question if needed.
Implement one at a time.
