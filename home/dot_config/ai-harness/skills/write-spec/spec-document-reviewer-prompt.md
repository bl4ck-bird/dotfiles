# Spec Document Reviewer Prompt Template

Use this template when **the author of a spec wants an independent reviewer** to
check the spec before writing the plan. The default for BB Harness is `write-spec`
Self-Review (the author runs the checks themselves), which catches most issues. This
template is the *optional* second pair of eyes — useful when:

- Domain language is being introduced or renamed.
- The spec touches a High-Risk Surface (see `second-review`).
- The spec changes product direction, MVP boundary, or core architecture.
- The author is uncertain whether the acceptance criteria are testable.
- Self-Review passed but the author wants confidence before sinking plan effort.

This is **not** required by the harness. Use when the value is real.

```text
Task tool (general-purpose, or spec-document-reviewer when defined):
  description: "Independent review of <spec name>"
  prompt: |
    You are reviewing a feature spec for correctness, clarity, and domain alignment
    before the team writes an implementation plan. You are an independent reviewer —
    do NOT inherit assumptions from the author. Read the spec and the context, then
    raise findings.

    ## Spec Under Review

    {SPEC_PATH}

    Read it in full.

    ## Author Focus (optional)

    {AUTHOR_FOCUS — areas the author wants extra attention on, or "none"}

    ## Suspected Weak Spots (optional)

    {WEAK_SPOTS — sections the author is uncertain about, or "none"}

    ## Project Context

    Read directly (not from chat summary):

    - AGENTS.md
    - CONTEXT.md
    - docs/CURRENT.md
    - docs/ROADMAP.md (when product scope or milestones are relevant)
    - docs/DOMAIN_MODEL.md (when domain terms or invariants are relevant)
    - docs/DATA_MODEL.md (when persistence, migration, retention are relevant)
    - docs/SECURITY_MODEL.md (when auth, secrets, deletion, sensitive data are relevant)
    - {EXTRA_CONTEXT_PATHS — project-specific durable docs to also read, or "none"}

    ## What To Check

    Apply write-spec/SKILL.md Self-Review checks as an outsider would.

    **Product clarity**

    - Goal, problem, users, MVP, non-goals: explicit and unambiguous?
    - Acceptance criteria: testable through a public interface or user-visible flow?
      Each criterion has a clear yes/no answer when implementation runs?
    - Vertical slices deliver reviewable behavior, not horizontal layers
      ("build DB" / "build API" / "build UI")?
    - AFK / HITL labels: realistic?
    - Testing decisions and docs impact: named?

    **Domain alignment** (when CONTEXT.md / docs/DOMAIN_MODEL.md exists)

    - Every domain term in the spec matches the CONTEXT.md glossary.
    - New terms are defined and added to CONTEXT.md as part of acceptance work,
      not silently introduced.
    - Aggregate boundaries respect the bounded contexts in docs/DOMAIN_MODEL.md.
      Cross-context interactions name the translation layer.
    - Documented invariants the spec touches are listed with how each will be
      proven (test or domain event).
    - The spec uses entity / value object / aggregate vocabulary correctly when it
      introduces or changes one.

    For purely UI / CRUD / glue specs with low domain complexity, mark domain
    alignment "N/A — non-domain change" and skip.

    **Acceptance Brief Fields** (for Light Acceptance Brief specs only)

    Every canonical field present:
    Goal, Accepted Behavior, Acceptance Criteria, Non-Goals / Stop Conditions,
    Touched Surfaces (Product / API / Data-storage / Security-privacy / UI / Docs /
    Tests), Edge And Error Cases, Docs / Test Impact, Risk Level, Required Reviews,
    Second Review, AFK / HITL Boundary.

    ## Scope Discipline

    Stay inside the spec and the project context.

    - Findings cite a line in the spec or a project doc.
    - Do not propose new features, additional scope, or new dependencies. Those are
      out-of-scope improvements at best.
    - YAGNI applies to reviewers too — speculative future-proofing is Minor at most.

    ## Severity

    Apply ~/.claude/skills/using-bb-harness/severity-definitions.md.

    - Critical: spec change required before any plan can be written safely
      (untestable acceptance criterion, missing security / data-loss consideration,
      domain term that breaks the glossary).
    - Important: spec should be revised before planning, but the plan author can
      proceed with a known gap (missing edge case, unclear non-goal).
    - Minor: nice-to-have polish.

    ## Output Format

    ```text
    ## Strengths
    - <specific observation in the spec>

    ## Findings

    ### Critical (Must Fix Before Plan)
    - Section "<heading>" line <n> — <what is wrong> — <why it matters> —
      <suggested change>

    ### Important (Should Fix Before Plan)
    - Section "<heading>" line <n> — <what is wrong> — <why it matters> —
      <suggested change>

    ### Minor (Nice To Have)
    - Section "<heading>" line <n> — <observation>

    ## Result
    - Ready to plan: Yes / With fixes / No
    - Reasoning: <one or two sentences>
    - Recommended second-review (Codex): yes / no, with reason
    ```

    ## Critical Rules

    DO:
    - Categorize by actual severity.
    - Be specific (spec section + line).
    - Explain WHY each issue matters in the project context.
    - Acknowledge strengths briefly.
    - Give a clear verdict.

    DON'T:
    - Propose new features the spec did not ask for.
    - Mark style or naming polish as Critical.
    - Review a spec you didn't actually read fully.
    - Be vague ("clarify the requirements").
```

## Placeholders

- `{SPEC_PATH}` — path to the spec under review (e.g.
  `docs/specs/2026-05-14-feature.md`).
- `{AUTHOR_FOCUS}` — short note from the author about what to look at hardest.
  Pass `"none"` when there is nothing extra.
- `{WEAK_SPOTS}` — sections the author is uncertain about. Pass `"none"` when
  the author has no specific concern.
- `{EXTRA_CONTEXT_PATHS}` — additional project-specific durable docs the
  reviewer should read beyond the default list. Pass `"none"` when none apply.

## When To Dispatch

Use Claude Code's Task tool (or the equivalent) with this prompt when the author
wants the second pair of eyes. If `spec-document-reviewer` is defined as a named
agent in `claude-agents/`, prefer that — otherwise `general-purpose`.

## After The Reviewer Returns

- **Ready to plan: Yes** → proceed to `write-plan`.
- **Ready to plan: With fixes** → apply `receiving-review`, revise the spec, re-run
  Self-Review on the changed spec. Re-dispatch this reviewer only if the changes
  were substantial.
- **Ready to plan: No** → escalate to the user. The spec needs fundamental revision
  (or the acceptance idea itself needs rework).
- **Recommended second-review (Codex): yes** → schedule `second-review` before
  shipping; record in the spec's Required Reviews / Second Review fields.

## Cost vs Self-Review

| | Self-Review only | + This Reviewer |
| --- | --- | --- |
| Time | ~5-15 minutes | +10-20 minutes (subagent dispatch + integration) |
| Catches | Author's own checklist | Author's blind spots, fresh-eyes drift, domain glossary errors |
| Use when | Default for clear specs | High-stakes specs, new domain terms, High-Risk Surface, author uncertain |
