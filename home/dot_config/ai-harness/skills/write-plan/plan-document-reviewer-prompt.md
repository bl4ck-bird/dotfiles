# Plan Document Reviewer Prompt Template

Use when **the plan author wants an independent reviewer** before executing
tasks. Default for BB Harness is `write-plan` Self-Review (the author runs the
checks). This template is the *optional* second pair of eyes — useful when:

- Plan crosses module boundaries or changes dependency direction.
- Plan touches a High-Risk Surface (see `second-review`).
- Tasks are large or numerous.
- File responsibility mapping affects untouched code nontrivially.
- Self-Review passed but the author wants confidence before spending implementer
  cycles.

**Not** required by the harness. Use when value is real.

```text
Task tool (general-purpose, or plan-document-reviewer when defined):
  description: "Independent review of <plan name>"
  prompt: |
    You are reviewing an implementation plan before code execution. You are
    independent — do NOT inherit assumptions from the author. Read the plan, the
    acceptance artifact, and project docs, then raise findings.

    ## Plan Under Review

    {PLAN_PATH}

    Read in full.

    ## Acceptance Artifact

    {ACCEPTANCE_PATH}

    Read it. Verify the plan's Acceptance Source line matches.

    ## Author Focus (optional)

    {AUTHOR_FOCUS — areas the author wants extra attention on, or "none"}

    ## Suspected Weak Spots (optional)

    {WEAK_SPOTS — sections the author is uncertain about (file map, verification
    commands, risk list), or "none"}

    ## Project Context

    Read directly:

    - AGENTS.md
    - CONTEXT.md
    - docs/CURRENT.md
    - docs/AGENT_WORKFLOW.md
    - docs/ARCHITECTURE.md (when boundaries / runtime / module shape may change)
    - docs/DOMAIN_MODEL.md (when domain language / invariants matter)
    - docs/DATA_MODEL.md (when persistence / migration / retention matter)
    - docs/SECURITY_MODEL.md (when auth / secrets / deletion / sensitive data
      matter)
    - docs/TESTING_STRATEGY.md (when verification expectations matter)
    - {EXTRA_CONTEXT_PATHS — additional project docs, or "none"}

    ## What To Check

    Apply write-plan/SKILL.md Self-Review checks as an outsider.

    **Plan Hygiene**
    - Every acceptance requirement maps to a task or explicit non-goal.
    - Every task has exact verification commands and expected RED / GREEN signals
      for TDD steps.
    - No placeholder language ("TBD", "later", "appropriate error handling",
      "write tests for the above").
    - New identifier names match CONTEXT.md.
    - Plan does not copy large sections from the acceptance artifact — it links.
    - A human can inspect the plan without chat history.
    - Acceptance Source named; Acceptance Self-Review note present.

    **Architecture Soundness** (when plan touches more than glue / CRUD)
    - SRP: each file in the File Responsibility Map has one primary reason to
      change. Two unrelated concerns: flag for split.
    - DIP: domain / application code does not depend on framework, ORM, HTTP
      client, or filesystem types. If it must, plan names the port / adapter.
    - Dependency direction: imports flow inward (UI / infra → application →
      domain). Plan does not introduce a domain file importing infrastructure.
    - File-size impact: files at or near 300/600-line threshold (see
      code-quality-review File And Complexity Thresholds) have one of: scoped
      extraction before feature work, documented exception, or follow-up
      refactor task.
    - Speculative abstraction: no ports, interfaces, factories, or strategies
      for variation that does not yet exist.
    - Cross-cutting concerns: logging, auth, persistence, caching at consistent
      boundaries.

    For glue, config, docs, or scaffold-only plans, mark architecture soundness
    "N/A — non-architectural change" and skip.

    **Domain Alignment**

    Same checks as write-spec spec-document-reviewer-prompt.md Domain Alignment
    section, applied to plan content (file names, task descriptions, identifier
    names).

    **Review Needs**
    - Code-quality follow-on triggers (security surface, High-Risk Surface) named
      correctly?
    - security-review scheduled when triggered?
    - second-review scheduled when Required When Available criteria apply (per
      second-review)?

    **Verification**
    - Each task lists exact commands.
    - Expected RED / GREEN signals named for TDD steps.
    - Verification commands actually exist (do not invent
      `npm run test:integration` when the project uses `pnpm vitest`).

    **Risk And Rollback**
    - Open Risks: realistic and named (not "TBD").
    - Rollback / Recovery: feasible given commit / stack strategy.
    - Commit / Stack Strategy: one of four options chosen (no commit / single
      commit / per-slice / stacked); does not authorize commit/push by itself.

    ## Scope Discipline

    Stay inside the plan and project context.

    - Findings cite a section + line in the plan.
    - Do not propose new tasks the acceptance artifact did not require.
    - "Could be better organized" is not a finding. "Task 3 changes file X which
      already has reason-to-change Y; SRP violation" is a finding.
    - YAGNI applies to reviewers too.

    ## Severity

    Apply ~/.claude/skills/using-bb-harness/severity-definitions.md.

    - Critical: plan cannot be executed safely as-written (wrong behavior, state
      leak, documented invariant violated, unrequested architectural changes
      required mid-execution).
    - Important: revise before execution, but implementer can proceed if captured
      as known follow-up.
    - Minor: nice-to-have polish.

    ## Output Format

    ```text
    ## Strengths
    - <specific observation in the plan>

    ## Findings

    ### Critical (Must Fix)
    - Plan section "<heading>" task <n> — <what is wrong> — <why it matters> —
      <suggested change>

    ### Important (Should Fix)
    - Plan section "<heading>" task <n> — <what is wrong> — <why it matters> —
      <suggested change>

    ### Minor (Nice To Have)
    - Plan section "<heading>" task <n> — <observation>

    ## Risk And Verification
    - Risks named: complete / incomplete (list missing).
    - Verification commands: confirmed / unconfirmed (list unconfirmed).
    - Rollback: feasible / infeasible.

    ## Result
    - Ready to execute: Yes / With fixes / No
    - Reasoning: <one or two sentences>
    - Recommended second-review (Codex): yes / no, with reason
    ```

    ## Critical Rules

    DO:
    - Categorize by actual severity.
    - Be specific (plan section + task + line).
    - Explain WHY each issue matters in the project context.
    - Verify the plan's verification commands actually exist.
    - Give a clear verdict.

    DON'T:
    - Propose new tasks the acceptance artifact did not ask for.
    - Mark style or naming polish as Critical.
    - Review a plan you didn't actually read fully.
    - Be vague ("improve error handling").
```

## Placeholders

- `{PLAN_PATH}` — path to the plan under review (e.g.
  `docs/plans/2026-05-14-feature.md`).
- `{ACCEPTANCE_PATH}` — path to spec / Light Acceptance Brief / issue the plan
  implements.
- `{AUTHOR_FOCUS}` — author's note about what to look at hardest, or `"none"`.
- `{WEAK_SPOTS}` — sections the author is uncertain about, or `"none"`.
- `{EXTRA_CONTEXT_PATHS}` — additional project-specific durable docs, or `"none"`.

## When To Dispatch

Use the Task tool with this prompt when the author wants a second pair of eyes.
If `plan-document-reviewer` is defined in `claude-agents/`, prefer that —
otherwise `general-purpose`.

## After The Reviewer Returns

- **Ready to execute: Yes** → proceed to `subagent-driven-development` or
  `executing-plans-inline`.
- **Ready to execute: With fixes** → apply `receiving-review`, revise the plan,
  re-run Self-Review. Re-dispatch this reviewer only if changes were substantial.
- **Ready to execute: No** → escalate. The plan needs fundamental revision (or
  the acceptance artifact itself — return to `write-spec`).
- **Recommended second-review (Codex): yes** → schedule `second-review` per its
  Required When Available criteria.

## Cost vs Self-Review

| | Self-Review only | + This Reviewer |
| --- | --- | --- |
| Time | ~10-20 min | +15-30 min (dispatch + integration) |
| Catches | Author's checklist | Architecture blind spots, missing review needs, nonexistent verification commands, optimistic risk lists |
| Use when | Default for plans with clear boundaries | High-Risk Surface, multi-module changes, dependency-direction changes, many tasks, author uncertain about file mapping |
