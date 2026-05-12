# Debugging Pressure Scenarios

Load this reference when:

- You are about to skip `bug-diagnosis` workflow ("just try a fix") because of time
  pressure, exhaustion, social pressure, or sunk cost.
- You catch yourself reaching for `sleep(5000)`, `try { ... } catch {}`, or a
  "temporary" workaround without reproducing the bug.
- Someone with authority is pushing for a quick fix without root-cause analysis.
- A teammate / agent says "I have seen this pattern before, just do X" without
  reading the actual code under failure.

These scenarios are training material. Read them when you sense any of the pressures
below; the right answer is *not* the convenient one.

**Core principle**: pressure does not change the technical reality. A "quick fix"
without reproduction usually produces a slower outcome (re-investigation later,
masked second bug, regression after the demo).

## Scenario 1 — Emergency Production Fix

You are on-call. Production API is at 100 % error rate. Revenue loss is real
(quote a number; the number is real to the business).

Logs show:
```text
PaymentError: Connection timeout to payments.api.com
```

You remember another service had a timeout fixed by adding a retry.

The temptation: "Add retry, deploy, stop the bleeding. 5 minutes vs 35 minutes of
investigation."

### Options

**A** — Follow `bug-diagnosis` workflow: reproduce, falsifiable hypotheses, root
cause. 35+ minutes; large incremental loss during investigation.

**B** — Quick fix now (add retry, deploy), investigate after restored. 5 minutes;
investigation deferred.

**C** — Compromise: minimal investigation (10 min) then decide.

### The Right Answer

**B** is correct *for production outage*, with a hard constraint: the investigation
is **not** deferred — it is the very next task, before any other work, and the retry
is treated as a **temporary mitigation, not a fix**.

The `bug-diagnosis` workflow is not "always reproduce before any action" — it is
"never claim *fixed* without reproduction." Mitigation (stop the bleeding) is allowed
when the harm rate is large. Fix (claim closed) requires the full loop.

### What Goes Wrong If You Get This Scenario Wrong

- Pick A: real money lost during investigation. Often the wrong tradeoff for live
  outage.
- Pick B and *defer indefinitely*: retry masks the actual bug. The next incident
  finds it again, often during a worse window.
- Pick B and *call it fixed* without investigation: lying about completion. Trust
  cost compounds.

### Rule

```text
For production outages:
  Mitigate immediately. Mark "MITIGATED, NOT FIXED".
  Open the investigation as the very next task.
  Apply verification-before-completion to the eventual fix.
```

## Scenario 2 — Sunk Cost + Exhaustion

You have been debugging a flaky test for 4 hours. It is 8 pm. Dinner plans at 8:30.

You have tried `sleep(100)`, `sleep(500)`, `sleep(1000)`, `sleep(2000)`. Most worked
sometimes; none worked deterministically.

The temptation: bump to `sleep(5000)`, add a TODO comment, file a ticket, go to
dinner. "At least 4 hours not wasted."

### Options

**A** — Delete all timeout code. Restart `bug-diagnosis` from the reproduction loop.
2-3 more hours. Miss dinner.

**B** — Keep `sleep(5000)`, file a "investigate properly later" ticket.

**C** — Spend 30 more minutes looking for root cause; if not obvious, use timeout.

### The Right Answer

**A**, with a planning constraint: **stop tonight, restart fresh tomorrow**.

The 4 hours of `sleep()` tweaking is sunk cost. Treating it as evidence is the
fallacy. The right move when you have been guessing for 4 hours is not to guess
harder — it is to *stop guessing*.

But the second mistake is to keep going when exhausted. The next 2 hours of tired
debugging is likely to add more guesses, not insight. Stop. Sleep. Restart with
`condition-based-waiting.md` (this is a flaky-test symptom — use the right tool).

### What Goes Wrong

- Pick B: the ticket sits open for months. The 5-second sleep adds 5 seconds to
  every CI run forever. The next person to touch this code re-discovers the bug.
- Pick C exhausted: 30 more minutes of guessing produces 31st guess. Insight does
  not come on demand.
- Pick A but keep working tired: same exhaustion problem applies to systematic
  debugging.

### Rule

```text
For flaky tests reached via timeout escalation:
  STOP using sleep() escalation. That is the symptom, not the fix.
  Switch to condition-based-waiting (see condition-based-waiting.md).
  If exhausted, stop. Resume fresh.
  Sunk cost is sunk. New decision is "what's right next", not "how to salvage hours."
```

## Scenario 3 — Authority + Social Pressure

Zoom call. Senior engineer (10 years experience). Tech lead. Two devs watching.

Senior engineer: "Found it. Token needs refresh after the new middleware. Add a
refresh at line 147."

You: "Should we understand why the middleware is invalidating tokens first?"

Senior: "I've seen this pattern a hundred times. The fix is the refresh."

Tech lead: "How long for investigation?"

You: "30-45 minutes through the middleware."

Tech lead: "We're already 20 minutes over. [Senior] knows this. Let's just
implement."

The temptation: defer to expertise. Everyone wants the call done.

### Options

**A** — Push back: "I want to understand the root cause." Look dogmatic / junior.

**B** — Go with the senior's fix. They have 10 years; you have ~?

**C** — Compromise: 5-minute doc check, then implement senior's fix.

### The Right Answer

**A**, phrased technically and briefly: "Adding a refresh hides whatever the
middleware did wrong. If it was supposed to keep the token valid, that's a bug. If
it was supposed to invalidate the token, the refresh undoes the security
property. Five minutes to read the middleware tells us which."

The right answer is not "always defer to seniors" and not "always reject
authority". It is: **the technical question still has a technical answer, and the
authority does not change it.** A 10-year senior who has not read this codebase's
middleware can still be wrong about this specific middleware.

If after reading the middleware the senior was right, the fix takes 30 seconds and
you all learn something. If they were wrong, you just prevented a security
regression.

### What Goes Wrong

- Pick B (deferring to authority): the refresh masks a security defect (token was
  invalidated for a reason — re-issuing it breaks logout, role change, or revocation).
  Or it does nothing (middleware was fine), and you do not learn why the test
  failure looked like it did.
- Pick A but as a fight: relationship damaged, technical point lost in social
  conflict. Frame as a question about the specific code, not a defense of process.
- Pick C as performance: a 5-minute doc check that you do not actually use is
  theater. Either read the middleware or do not.

### Rule

```text
Authority and seniority are signals, not proofs.
"I've seen this before" is faster than "I read this code."
Faster is not the same as correct.

Push back technically, briefly, with a specific question about the code under
discussion. Do not argue about process. Argue about this file at this line.
```

## Cross-Cutting Patterns

What all three scenarios share:

1. **Pressure is the only argument for skipping the workflow.** When the pressure
   is removed (production stable, you are rested, the call is over), nobody would
   defend the shortcut.
2. **The shortcut produces a second bug**: deferred investigation that never
   happens, 5-second sleep that lasts forever, security regression masked by a
   token refresh.
3. **Honesty is the cheapest cost.** "Mitigated, not fixed" is one extra word and
   it saves the next on-call from re-investigating.
4. **`verification-before-completion` still applies.** If you mitigate with a
   retry, the claim "production is stable now" still needs the fresh metric.

## Academic Self-Check

If you can answer these without re-reading `bug-diagnosis/SKILL.md`, you understand
the workflow:

1. What are the steps of the reproduction loop?
2. What must happen *before* attempting any fix?
3. What do you do if your first hypothesis is refuted?
4. What does the workflow say about changing multiple things at once?
5. What do you do if you do not fully understand the bug?
6. Is it ever acceptable to skip the workflow for "simple" bugs?

If your answer to any of these is "depends on the pressure", re-read this file.

## When To Re-Load

- Right before claiming a bug is fixed in a high-pressure situation.
- When you find yourself negotiating ("just this once", "good enough", "I'll fix it
  later") with the workflow.
- After an incident — these scenarios are training, but they are also a checklist
  for retros: which pressure did the team buckle under?
