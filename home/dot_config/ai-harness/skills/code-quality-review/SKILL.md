---
name: code-quality-review
description: Use when reviewing implementation quality after `spec-compliance-review` passes — covers code quality, architecture (DDD/SOLID), file size, testing, durable docs drift, and production readiness. Returns Ready to merge? Yes / No / With fixes.
---

# Code Quality Review

Review whether the implementation is *well built* — clean, maintainable, tested, aligned with
the architecture, and ready to ship. Only run after `spec-compliance-review` returns
✅ Spec compliant.

This skill is the harness-wide SSOT for:

- DDD operational checks
- SOLID checks
- File and complexity thresholds
- Coverage matrix
- Durable docs drift checks

Other skills (`write-spec` Self-Review, `write-plan` Self-Review, `test-driven-development` Refactor
Gate) reference subsets of these checks; this file owns the full definitions.

## When To Use

- After `spec-compliance-review` passes for a slice or task.
- Before `ship-check` for substantial work.
- Before merge, PR, or release.
- When asked for an independent quality opinion.

## Inputs

Read directly:

- `AGENTS.md`, `CONTEXT.md`, `docs/CURRENT.md`
- The acceptance artifact (spec, PRD, issue, plan task, or approved request).
- The plan when one exists.
- `docs/ARCHITECTURE.md`, `docs/DOMAIN_MODEL.md`, `docs/TESTING_STRATEGY.md` when present and
  relevant to the touched surface.
- Changed file list, diff, and test/verification output.

## What To Check

Five areas. Each finding must cite a file:line in the diff.

### 1. Code Quality

- Clean separation of concerns; functions do one thing.
- Proper error handling: no swallowed exceptions, no broad catches without re-raise, no
  fallbacks that mask upstream failures.
- Type safety where applicable; no `any` / `unknown` leaking past boundaries; no
  stringly-typed states that should be enums or value objects.
- DRY without premature abstraction.
- Edge cases handled or explicitly documented as accepted.
- Comment hygiene: comments explain *why* (constraint, invariant, workaround), not *what*.
  Flag tutorial comments, restated identifiers, and `// added for X` temporal notes.

### 2. Architecture (DDD / SOLID / boundaries)

#### DDD Operational Checks

Load `ddd-operational-checks.md` in this directory when **both**:

- `CONTEXT.md` or `docs/DOMAIN_MODEL.md` exists, **and**
- The diff touches domain code (entities, aggregates, value objects, domain services,
  repositories, ports, anti-corruption layers, or domain events).

If either condition is absent, skip this companion. General CRUD / glue / UI work
does not need DDD review — the other sections of this skill are sufficient.

Summary (full definitions in the companion):

- Ubiquitous language drift.
- Aggregate invariants (each must have a test through a public interface).
- Bounded-context boundaries (no cross-context imports without translation).
- Anti-corruption layer (external types translated at the boundary).
- Entity vs value object discipline.
- Application vs domain service separation.
- Repositories / ports as real boundaries, not CRUD wrappers.

#### SOLID Checks

- **SRP**: each module has one primary reason to change. Multiple reasons → split.
- **OCP**: extension points exist only for real variation, not speculative future needs.
- **LSP**: subtype or interface implementations preserve caller-visible behavior contracts.
- **ISP**: broad interfaces should split when callers use small subsets.
- **DIP**: domain / application code depends on ports or stable interfaces, not framework
  or adapter details.

#### File And Complexity Thresholds

- **300 lines (source file)**: require responsibility review. Split when multiple reasons to
  change are mixed.
- **600 lines (source file)**: review finding unless the file is generated, vendored, a
  fixture, a migration, a data table, or has a documented exception in
  `docs/ARCHITECTURE.md`.
- **50-80 lines (function)**: consider extraction if it mixes concerns or has deep
  branching.
- **3+ repeated conditionals on the same concept**: consider a domain concept, strategy,
  lookup table, or policy object.

Long files are acceptable when they are data tables, generated code, test fixtures, or
documented framework glue.

#### Other Architecture Concerns

- Boundary clarity between domain, application, infrastructure, and UI layers.
- Coupling direction, circular dependencies, framework leakage into domain.
- New abstractions are justified by real complexity or established project patterns; not
  speculative.
- Testability of core behavior without UI, network, database, or filesystem.

### 3. Testing

- Tests prove public behavior, user-visible flows, or domain invariants — not private
  helpers or file layout.
- Mocks do not remove the behavior under test.
- Regression tests for bug fixes fail before the fix.
- Slow, flaky, expensive tests have a focused alternative or a recorded reason.
- Verification commands and expected signals are recorded.

#### Coverage Matrix (Required)

Map every acceptance criterion to its proof.

| Acceptance criterion | Proof (test file:line, command output, or `ACCEPTED` reason) |
| --- | --- |

- Mark `MISSING` for gaps.
- Mark `ACCEPTED` only when the acceptance source explicitly excludes the case.
- Edge / error cases without coverage must be listed separately.

### 4. Durable Docs Drift

- README stays user-facing and high-level.
- `CONTEXT.md` owns canonical domain terms — flag drift.
- `docs/CURRENT.md` reflects current phase, acceptance source, last verification, next
  action when substantial state changed.
- `docs/ARCHITECTURE.md`, `docs/DOMAIN_MODEL.md`, `docs/DATA_MODEL.md`,
  `docs/SECURITY_MODEL.md`, `docs/TESTING_STRATEGY.md`: updated when their concern changed.
- Stub / TODO content is not treated as project truth.
- Specs and plans do not duplicate or contradict durable docs.

### 5. Production Readiness

- Migration strategy if schema changed.
- Backward compatibility considered for public APIs.
- Documentation complete for new behavior or interfaces.
- No obvious bugs in adjacent code touched by the diff.

## Scope Discipline

Review findings must stay inside the diff and the approved acceptance artifact.

- Findings must cite a file:line *touched by this diff*. Findings on untouched code are
  Minor unless the change makes the untouched code unsafe (then they may be Critical /
  Important with explicit evidence of the new unsafety).
- Do not propose new product behavior, broad rewrites, new dependencies, new storage / API
  shape, or unrelated cleanup as required fixes.
- "Could be better organized" is not a finding. "This diff added a reason-to-change that
  conflicts with existing responsibility at <file:line>" is a finding.
- YAGNI applies to reviewers too. Speculative future-proofing is Minor at best.
- Do not recommend large rewrites unless the current design blocks the requested work.
  Prefer small refactor slices that keep tests green.

## Follow-On Reviews

`using-bb-harness` Review Chain Depth Cap allows at most **one** automatic follow-on review.
Pick the single follow-on whose trigger signal is strongest in the touched diff:

| Trigger present in this diff | Follow-on |
| --- | --- |
| Auth, secrets, crypto, deletion, untrusted input, destructive operation, sensitive data | `security-review` |
| Independent double-check requested or High-Risk Surface touched | `second-review` |

If a second follow-on is justified, name it as a recommendation and ask the user before
running it. Do not auto-chain.

## Severity

Reviewers must classify findings using these definitions. Do not promote a finding above
its real impact.

- **Critical (Must Fix)**: bug, security defect, data loss risk, broken accepted behavior,
  silent failure, missing test for a behavior the diff claims.
- **Important (Should Fix)**: architecture problem (DDD / SOLID violation, file-size
  threshold breach without documented exception, wrong boundary in touched path), missing
  error handling, weak test design, durable doc claim already false.
- **Minor (Nice To Have)**: style, naming polish, optimization opportunity, comment hygiene,
  out-of-scope improvement.

Findings on code untouched by the diff are Minor unless the change makes the untouched code
unsafe.

## Result

Use this gate. Reviewers and authoring skills must apply it.

- **Ready to merge: Yes** — no Critical or Important findings remain.
- **Ready to merge: With fixes** — only Critical / Important findings that can be fixed by
  the implementer; reviewer re-runs after fixes.
- **Ready to merge: No** — fundamental architecture, scope, or correctness problem requires
  the artifact (plan or acceptance) to be revised, not just the code.

Minor findings do not block. List them but do not require tracking in the plan.

### Iteration Rule

If the result is **With fixes**, the implementer applies the Critical / Important findings
and the same review re-runs on the changed diff. Stop after **two cycles** in the same
phase — escalate to the user with the unresolved findings rather than running a third
cycle. Cycle 2 findings that were not visible in cycle 1 must be labeled
`introduced-in-cycle-2` with a reason; this is the signal that review scope is expanding
rather than the code failing.

## Output

Lead with strengths (specific, brief), then findings, then the result.

```text
## Strengths
- <specific observation with file:line>

## Findings

### Critical (Must Fix)
- <file:line> — <what is wrong> — <why it matters> — <how to fix>

### Important (Should Fix)
- <file:line> — <what is wrong> — <why it matters> — <how to fix>

### Minor (Nice To Have)
- <file:line> — <observation>

## Coverage Matrix
<see Coverage Matrix section above>

## Follow-On
- Required: <security-review / second-review / none>
- Recommended (needs user confirmation): <none / one named review>

## Result
- Ready to merge: Yes / With fixes / No
- Reasoning: <one or two sentences>
```

For substantial reviews, save the record in
`docs/reviews/YYYY-MM-DD-<topic>-code-quality-review.md`.

## Do Not

- Mark nitpicks as Critical.
- Give vague findings ("improve error handling"). Be specific.
- Review code you did not actually read.
- Avoid a clear verdict.
- Recommend broad rewrites or new dependencies as required fixes.
- Auto-chain into a second follow-on review.
