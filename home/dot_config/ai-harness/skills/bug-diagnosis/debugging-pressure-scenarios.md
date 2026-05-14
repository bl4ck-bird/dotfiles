# Debugging Pressure Scenarios

Load when:

- About to skip `bug-diagnosis` ("just try a fix") due to time, exhaustion, social pressure,
  or sunk cost.
- Reaching for `sleep(5000)`, `try { ... } catch {}`, or "temporary" workaround without
  reproducing.
- Authority is pushing for a quick fix without root-cause analysis.
- A teammate/agent says "I have seen this pattern, just do X" without reading the code under
  failure.

**Core principle**: pressure does not change technical reality. A "quick fix" without
reproduction usually produces a slower outcome (re-investigation later, masked second bug,
regression after the demo).

## Scenario 1 — Emergency Production Fix

On-call. Production API at 100% error rate. Real revenue loss.

```text
PaymentError: Connection timeout to payments.api.com
```

Temptation: another service had a similar timeout fixed by retry — add retry, deploy
(5 min vs 35 min investigation).

### Options

- **A** — Full `bug-diagnosis` (35+ min; large incremental loss).
- **B** — Quick fix now, investigate after restored (5 min; investigation deferred).
- **C** — 10-min minimal investigation, then decide.

### Right Answer

**B** for production outage, with hard constraint: investigation is the **very next task**,
the retry is a **temporary mitigation, not a fix**.

`bug-diagnosis` is not "always reproduce before any action" — it is "never claim *fixed*
without reproduction." Mitigation is allowed when harm rate is large; fix (claim closed)
requires the full loop.

### What Goes Wrong

- Pick A: real money lost during investigation.
- Pick B and defer indefinitely: retry masks bug, next incident is worse.
- Pick B and call it fixed: lying about completion, trust cost compounds.

### Rule

```text
For production outages:
  Mitigate immediately. Mark "MITIGATED, NOT FIXED".
  Investigation is the very next task.
  Apply verification-before-completion to the eventual fix.
```

## Scenario 2 — Sunk Cost + Exhaustion

Debugging a flaky test for 4 hours. 8 pm. Dinner at 8:30. Tried `sleep(100/500/1000/2000)`,
none deterministic.

Temptation: `sleep(5000)` + TODO + ticket + dinner. "At least 4 hours not wasted."

### Options

- **A** — Delete all timeout code, restart `bug-diagnosis` from reproduction. 2-3 hours.
- **B** — Keep `sleep(5000)`, file ticket.
- **C** — 30 more minutes for root cause; if not obvious, use timeout.

### Right Answer

**A**, with planning constraint: **stop tonight, restart fresh tomorrow**.

The 4 hours is sunk cost. Treating it as evidence is the fallacy. Right move after 4 hours of
guessing: stop guessing. Second mistake: keep going when exhausted. Restart with
`condition-based-waiting.md`.

### What Goes Wrong

- Pick B: ticket sits for months, 5 s sleep in CI forever, next person re-discovers.
- Pick C exhausted: 31st guess. Insight does not come on demand.
- Pick A but keep working tired: same exhaustion problem.

### Rule

```text
For flaky tests reached via timeout escalation:
  STOP using sleep() escalation — symptom, not fix.
  Switch to condition-based-waiting.
  If exhausted, stop. Resume fresh.
  Sunk cost is sunk. New decision: "what's right next", not "how to salvage hours".
```

## Scenario 3 — Authority + Social Pressure

Zoom call. Senior engineer (10 yrs). Tech lead. Two devs watching.

Senior: "Found it. Token needs refresh after the new middleware. Line 147."
You: "Should we understand why the middleware invalidates tokens first?"
Senior: "I've seen this a hundred times."
Tech lead: "We're 20 min over. Let's just implement."

### Options

- **A** — Push back: "I want the root cause." Look dogmatic/junior.
- **B** — Defer to senior's 10 years.
- **C** — 5-min doc check, then implement senior's fix.

### Right Answer

**A**, phrased technically and briefly: "Adding a refresh hides whatever the middleware did
wrong. If it should keep the token valid, that's a bug. If it should invalidate, the refresh
undoes the security property. Five minutes in the middleware tells us which."

Not "always defer" or "always reject" — **the technical question has a technical answer, and
authority does not change it.** A 10-year senior who has not read this codebase's middleware
can still be wrong here.

### What Goes Wrong

- Pick B: refresh masks a security defect (token invalidated for a reason — re-issuing breaks
  logout/role change/revocation). Or it does nothing and you do not learn.
- Pick A as fight: relationship damaged. Frame as a question about specific code, not process.
- Pick C as performance: a doc check you do not use is theater. Read the middleware or do not.

### Rule

```text
Authority and seniority are signals, not proofs.
"I've seen this before" is faster than "I read this code." Faster ≠ correct.
Push back technically, briefly, with a specific question about this file at this line.
```

## Cross-Cutting Patterns

1. **Pressure is the only argument for skipping the workflow.** Remove the pressure and
   nobody defends the shortcut.
2. **Shortcut produces a second bug**: deferred investigation never happens, 5 s sleep lasts
   forever, security regression masked by token refresh.
3. **Honesty is the cheapest cost.** "Mitigated, not fixed" is one word; saves next on-call
   from re-investigating.
4. **`verification-before-completion` still applies.** A retry mitigation still needs the
   fresh metric to claim "stable now".

## Academic Self-Check

Answer without re-reading `bug-diagnosis/SKILL.md`:

1. Steps of the reproduction loop?
2. What must happen before any fix?
3. What if your first hypothesis is refuted?
4. What does the workflow say about changing multiple things at once?
5. What if you do not fully understand the bug?
6. Is it ever acceptable to skip the workflow for "simple" bugs?

If any answer is "depends on the pressure", re-read this file.

## When To Re-Load

- Right before claiming a bug fixed under high pressure.
- When negotiating with the workflow ("just this once", "good enough", "I'll fix later").
- After an incident — these scenarios double as a retro checklist for which pressure the team
  buckled under.
