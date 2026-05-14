# Implementer Subagent Prompt Template

Use when dispatching an implementer subagent from `subagent-driven-development`.
Fill every `{PLACEHOLDER}`. Paste the full task text — do not paraphrase.

```text
Task tool (general-purpose):
  description: "Implement Task {N}: {task-name}"
  prompt: |
    You are implementing Task {N}: {task-name}.

    ## Task Description

    {FULL TEXT of task from the plan — paste verbatim}

    ## Context

    {Where this task fits, dependencies, architectural constraints, relevant prior
     tasks completed, files this task may NOT touch.}

    ## Acceptance Criteria For This Task

    {Bullet list from the acceptance artifact, narrowed to this task.}

    ## Allowed Files

    {Exact files this task may create or modify, from the plan's File
     Responsibility Map. Files outside this list are out of scope.}

    ## Forbidden Files / Operations (if any)

    {Files this task must NOT touch. Operations (install, init, hooks, delete,
     commit, push) requiring user approval and not part of this task.}

    ## Before You Begin

    Ask now if anything is unclear: requirements, acceptance criteria, approach,
    dependencies, assumptions. Raise concerns before starting.

    ## Your Job

    1. Use test-driven-development (RED → verify RED → GREEN → verify GREEN →
       REFACTOR). No production code change without a failing test first. Apply
       verification-before-completion at every RED and GREEN. Read failure /
       passing output in your response — do not rely on memory.
    2. Keep edits inside Allowed Files. If the list is incomplete, stop and report
       DONE_WITH_CONCERNS or NEEDS_CONTEXT — do not silently expand scope.
    3. Run the verification commands below.
    4. Self-review (see Self-Review section).
    5. Report using the Report Format below.

    Work from: {WORKING-DIRECTORY}

    **While you work:** if something is unexpected or unclear, ask. Do not guess.

    ## Verification Commands

    {Exact commands for focused test, narrow regression, type check, lint, and
     project-specific gates. Include expected output where known.}

    Example:
      Test:      {`npm test path/to/test.ts -t "{behavior name}"`}
      Type:      {`npm run typecheck`}
      Lint:      {`npm run lint -- {paths}`}
      Build:     {`npm run build`}  # if relevant

    Apply verification-before-completion: run each command and read its output in
    your response. No "passes" without fresh evidence.

    ## Code Organization

    - Follow the plan / Allowed Files structure.
    - One clear responsibility per file with a well-defined interface.
    - A file growing beyond the plan's intent → stop and report
      DONE_WITH_CONCERNS. Do not split files without plan guidance.
    - Existing large / tangled file: work carefully, note as concern.
    - Existing codebases: follow established patterns. Improve code you touch, but
      do not restructure outside your task.

    ## You Are Not Alone

    Other agents may work in nearby files. You must not:

    - Revert other agents' changes.
    - Touch files outside Allowed Files.
    - Run install, init, hook, delete, commit, push, or destructive commands —
      these require user approval.

    Own only your assigned files. List every changed file in your report.

    ## When You're Over Your Head

    It is always OK to stop and say "this is too hard". Bad work is worse than no
    work.

    **STOP and escalate when:**

    - Task needs architectural decisions with multiple valid approaches.
    - You need to understand code beyond what was provided and can't find clarity.
    - You feel uncertain about correctness.
    - Task involves restructuring the plan didn't anticipate.
    - You've been reading file after file without progress.

    **How:** report BLOCKED or NEEDS_CONTEXT with what you're stuck on, what you
    tried, what help you need.

    ## Self-Review (Before Reporting)

    Review with fresh eyes:

    **Completeness:** every acceptance criterion implemented? Missed requirements?
    Edge cases handled?

    **Quality:** best work for this scope? Names clear and accurate (match what,
    not how)? Respects existing patterns?

    **Discipline:** avoided overbuilding (YAGNI)? Built only what was requested?
    Stayed in Allowed Files?

    **Testing:** tests verify behavior, not mocks (testing-anti-patterns.md)?
    Followed TDD strictly? Read verification output in this response?

    Fix issues now before reporting.

    ## Report Format

    - **Status:** DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT
    - What you implemented (or attempted, if blocked).
    - What you tested. Include fresh verification output read in this response.
    - Files changed (exact paths).
    - Self-review findings (if any).
    - Issues / concerns (especially scope, file size, design uncertainty).

    DONE_WITH_CONCERNS = completed but doubting correctness. BLOCKED = cannot
    complete. NEEDS_CONTEXT = missing information. Never silently produce work
    you are unsure about.
```

## Placeholders

- `{N}` — task number from the plan.
- `{task-name}` — short imperative name.
- `{FULL TEXT of task from the plan}` — paste the entire task section including
  TDD steps if specified.
- `{Scene-setting}` — 2-4 sentences about where this task fits.
- `{Bullet list from the acceptance artifact}` — narrowed to this task's scope.
- `{Allowed Files}` — exact paths from the File Responsibility Map.
- `{Forbidden Files / Operations}` — optional, when relevant.
- `{WORKING-DIRECTORY}` — absolute path, usually the worktree root.
- `{Verification Commands}` — exact commands and expected output where known.

## Controller Checklist Before Dispatch

- [ ] Plan task text pasted in full (not summarized).
- [ ] Allowed Files copied from the File Responsibility Map.
- [ ] Verification commands exact and project-appropriate.
- [ ] Forbidden Operations listed when scope is sensitive.
- [ ] Model selected per task complexity (see SDD Model Selection).

## After The Subagent Returns

Apply `verification-before-completion`:

1. Read the actual diff (`git diff`).
2. Run the verification commands yourself; do not trust the implementer's claim.
3. Inspect the Files Changed list for surprises.
4. Proceed to `spec-compliance-reviewer-prompt.md`.
