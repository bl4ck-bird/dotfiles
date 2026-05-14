# Spec Document Reviewer Prompt Template

Use when **the spec author wants an independent reviewer** before writing the
plan. Default for BB Harness is `write-spec` Self-Review (the author runs the
checks). This template is the *optional* second pair of eyes — useful when:

- Domain language is being introduced or renamed.
- Spec touches a High-Risk Surface (see `second-review`).
- Spec changes product direction, MVP boundary, or core architecture.
- Author is uncertain whether acceptance criteria are testable.
- Self-Review passed but the author wants confidence before plan effort.

**Not** required by the harness. Use when value is real.

```text
Task tool (general-purpose, or spec-document-reviewer when defined):
  description: "Independent review of <spec name>"
  prompt: |
    You are reviewing a feature spec for correctness, clarity, and domain
    alignment before the plan is written. You are independent — do NOT inherit
    assumptions from the author. Read the spec and context, then raise findings.

    ## Spec Under Review

    {SPEC_PATH}

    Read in full.

    ## Author Focus (optional)

    {AUTHOR_FOCUS — areas the author wants extra attention on, or "none"}

    ## Suspected Weak Spots (optional)

    {WEAK_SPOTS — sections the author is uncertain about, or "none"}

    ## Project Context

    Read directly (not from chat summary):

    - AGENTS.md
    - CONTEXT.md
    - docs/CURRENT.md
    - docs/ROADMAP.md (when product scope or milestones relevant)
    - docs/DOMAIN_MODEL.md (when domain terms or invariants relevant)
    - docs/DATA_MODEL.md (when persistence, migration, retention relevant)
    - docs/SECURITY_MODEL.md (when auth, secrets, deletion, sensitive data
      relevant)
    - {EXTRA_CONTEXT_PATHS — additional project docs, or "none"}

    ## What To Check

    Apply write-spec/SKILL.md Self-Review checks as an outsider.

    **Product clarity**
    - Goal, problem, users, MVP, non-goals: explicit and unambiguous?
    - Acceptance criteria: testable through a public interface or user-visible
      flow? Each has a clear yes/no answer when implementation runs?
    - Vertical slices deliver reviewable behavior, not horizontal layers
      ("build DB" / "build API" / "build UI")?
    - AFK / HITL labels: realistic?
    - Testing decisions and docs impact: named?

    **Domain alignment** (when CONTEXT.md / docs/DOMAIN_MODEL.md exists)
    - Every domain term matches CONTEXT.md glossary.
    - New terms defined and added to CONTEXT.md as acceptance work — not
      silently introduced.
    - Aggregate boundaries respect bounded contexts in docs/DOMAIN_MODEL.md.
      Cross-context interactions name the translation layer.
    - Documented invariants the spec touches are listed with how each is proven
      (test or domain event).
    - Spec uses entity / value object / aggregate vocabulary correctly when
      introducing or changing one.

    For purely UI / CRUD / glue specs with low domain complexity, mark domain
    alignment "N/A — non-domain change" and skip.

    **Acceptance Brief Fields** (Light Acceptance Brief specs only)

    Every canonical field present. Canonical field set lives in
    `~/.claude/skills/write-spec/SKILL.md` § Light Acceptance Brief — load that
    file before checking; do not rely on memory of the field list.

    ## Scope Discipline

    Stay inside the spec and project context.

    - Findings cite a line in the spec or a project doc.
    - Do not propose new features, additional scope, or new dependencies.
    - YAGNI applies to reviewers too — speculative future-proofing is Minor at
      most.

    ## Severity

    Apply ~/.claude/skills/using-bb-harness/severity-definitions.md.

    - Critical: spec change required before any plan can be written safely
      (untestable acceptance criterion, missing security / data-loss
      consideration, domain term breaking the glossary).
    - Important: revise before planning, but plan author can proceed with a
      known gap (missing edge case, unclear non-goal).
    - Minor: nice-to-have polish.

    ## Output Format

    ```text
    ## Strengths
    - <specific observation in the spec>

    ## Findings

    ### Critical (Must Fix)
    - Section "<heading>" line <n> — <what is wrong> — <why it matters> —
      <suggested change>

    ### Important (Should Fix)
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

- `{SPEC_PATH}` — path to spec under review (e.g.
  `docs/specs/2026-05-14-feature.md`).
- `{AUTHOR_FOCUS}` — author's note about what to look at hardest, or `"none"`.
- `{WEAK_SPOTS}` — sections the author is uncertain about, or `"none"`.
- `{EXTRA_CONTEXT_PATHS}` — additional project docs, or `"none"`.

## When To Dispatch

Use the Task tool with this prompt when the author wants a second pair of eyes.
If `spec-document-reviewer` is defined in `claude-agents/`, prefer that —
otherwise `general-purpose`.

## After The Reviewer Returns

- **Ready to plan: Yes** → proceed to `write-plan`.
- **Ready to plan: With fixes** → apply `receiving-review`, revise the spec,
  re-run Self-Review. Re-dispatch this reviewer only if changes were substantial.
- **Ready to plan: No** → escalate. The spec needs fundamental revision (or the
  acceptance idea itself needs rework).
- **Recommended second-review (Codex): yes** → schedule `second-review` before
  shipping; record in the spec's Required Reviews / Second Review fields.

## Cost vs Self-Review

| | Self-Review only | + This Reviewer |
| --- | --- | --- |
| Time | ~5-15 min | +10-20 min (dispatch + integration) |
| Catches | Author's checklist | Author's blind spots, fresh-eyes drift, domain glossary errors |
| Use when | Default for clear specs | High-stakes specs, new domain terms, High-Risk Surface, author uncertain |
