---
name: code-quality-review
description: Use when reviewing implementation quality after `spec-compliance-review` passes — covers code quality, architecture (DDD/SOLID), file size, testing, durable docs drift, and production readiness. Returns Ready to merge? Yes / With fixes / No.
---

# Code Quality Review

Review whether the implementation is *well built* — clean, maintainable, tested, aligned with architecture, ready to ship. Run only after `spec-compliance-review` returns ✅ Spec compliant.

Harness-wide SSOT for:

- DDD operational checks
- SOLID checks
- File and complexity thresholds
- Coverage matrix
- Durable docs drift checks

Other skills (`write-spec` Self-Review, `write-plan` Self-Review, `test-driven-development` Refactor Gate) reference subsets; this file owns the full definitions.

## When To Use

- After `spec-compliance-review` passes for a slice or task.
- Before `ship-check` for substantial work.
- Before merge, PR, or release.
- When asked for an independent quality opinion.

## Inputs

Read directly:

- `AGENTS.md`, `CONTEXT.md`, `docs/CURRENT.md`
- Acceptance artifact (spec, PRD, issue, plan task, or approved request).
- Plan when one exists.
- `docs/ARCHITECTURE.md`, `docs/DOMAIN_MODEL.md`, `docs/TESTING_STRATEGY.md` when present and relevant.
- Changed file list, diff, test/verification output.

## What To Check

Five areas. Each finding cites a file:line in the diff.

### 1. Code Quality

- Clean separation of concerns; functions do one thing.
- Proper error handling: no swallowed exceptions, no broad catches without re-raise, no fallbacks that mask upstream failures.
- Type safety where applicable; no `any` / `unknown` leaking past boundaries; no stringly-typed states that should be enums or value objects.
- DRY without premature abstraction.
- Edge cases handled or explicitly documented as accepted.
- Comment hygiene: comments explain *why* (constraint, invariant, workaround), not *what*. Flag tutorial comments, restated identifiers, `// added for X` temporal notes.

### 2. Architecture (DDD / SOLID / boundaries)

#### DDD Operational Checks

Load `ddd-operational-checks.md` when **both**:

- `CONTEXT.md` or `docs/DOMAIN_MODEL.md` exists, **and**
- Diff touches domain code (entities, aggregates, value objects, domain services, repositories, ports, anti-corruption layers, or domain events).

Either absent → skip companion. General CRUD / glue / UI does not need DDD review.

Summary (full in companion):

- Ubiquitous language drift.
- Aggregate invariants (each must have a test through a public interface).
- Bounded-context boundaries (no cross-context imports without translation).
- Anti-corruption layer (external types translated at boundary).
- Entity vs value object discipline.
- Application vs domain service separation.
- Repositories / ports as real boundaries, not CRUD wrappers.

#### SOLID Checks

- **SRP**: each module one primary reason to change. Multiple reasons → split.
- **OCP**: extension points exist only for real variation, not speculation.
- **LSP**: subtype / interface implementations preserve caller-visible contracts.
- **ISP**: broad interfaces split when callers use small subsets.
- **DIP**: domain / application depends on ports or stable interfaces, not framework / adapter details.

#### File And Complexity Thresholds

- **300 lines (source file)**: require responsibility review. Split when multiple reasons to change mixed.
- **600 lines (source file)**: review finding unless generated, vendored, fixture, migration, data table, or documented exception in `docs/ARCHITECTURE.md`.
- **50-80 lines (function)**: consider extraction if mixed concerns or deep branching.
- **3+ repeated conditionals on same concept**: consider domain concept, strategy, lookup table, or policy object.

Long files acceptable when data tables, generated code, test fixtures, or documented framework glue.

#### Other Architecture Concerns

- Boundary clarity between domain, application, infrastructure, UI.
- Coupling direction, circular dependencies, framework leakage into domain.
- New abstractions justified by real complexity or established project patterns; not speculative.
- Testability of core behavior without UI, network, DB, or filesystem.

### 3. Testing

- Tests prove public behavior, user-visible flows, or domain invariants — not private helpers or file layout.
- Mocks do not remove the behavior under test.
- Regression tests for bug fixes fail before the fix.
- Slow, flaky, expensive tests have a focused alternative or recorded reason.
- Verification commands and expected signals recorded.

#### Coverage Matrix (Required)

Map every acceptance criterion to its proof.

| Acceptance criterion | Proof (test file:line, command output, or `ACCEPTED` reason) |
| --- | --- |

- `MISSING` for gaps.
- `ACCEPTED` only when acceptance source explicitly excludes the case.
- Edge / error cases without coverage listed separately.

### 4. Durable Docs Drift

- README stays user-facing and high-level.
- `CONTEXT.md` owns canonical domain terms — flag drift.
- `docs/CURRENT.md` reflects current phase, acceptance source, last verification, next action when substantial state changed.
- `docs/ARCHITECTURE.md`, `docs/DOMAIN_MODEL.md`, `docs/DATA_MODEL.md`, `docs/SECURITY_MODEL.md`, `docs/TESTING_STRATEGY.md`: updated when their concern changed.
- Stub / TODO content not treated as project truth.
- Specs and plans do not duplicate or contradict durable docs.

### 5. Production Readiness

- Migration strategy if schema changed.
- Backward compatibility for public APIs.
- Documentation complete for new behavior or interfaces.
- No obvious bugs in adjacent code touched by the diff.

## Scope Discipline

Findings stay inside the diff and the approved acceptance artifact.

- Cite file:line *touched by this diff*. Findings on untouched code are Minor unless the change makes it unsafe (then Critical / Important with explicit evidence).
- No proposing new product behavior, broad rewrites, new dependencies, new storage / API shape, or unrelated cleanup as required fixes.
- "Could be better organized" is not a finding. "This diff added a reason-to-change that conflicts with existing responsibility at <file:line>" is a finding.
- YAGNI applies to reviewers. Speculative future-proofing is Minor at best.
- No recommending large rewrites unless current design blocks the requested work. Prefer small refactor slices keeping tests green.

## Follow-On Reviews

`using-bb-harness` Review Chain Depth Cap allows at most **one** automatic follow-on. Pick the one whose trigger signal is strongest in the diff:

| Trigger present in this diff | Follow-on |
| --- | --- |
| Auth, secrets, crypto, deletion, untrusted input, destructive operation, sensitive data | `security-review` |
| Independent double-check requested or High-Risk Surface touched | `second-review` |

Second follow-on justified → name it as a recommendation and ask user. Do not auto-chain.

## Severity

Classify findings using these definitions. Do not promote above real impact.

- **Critical (Must Fix)**: bug, security defect, data loss risk, broken accepted behavior, silent failure, missing test for behavior the diff claims.
- **Important (Should Fix)**: architecture problem (DDD / SOLID violation, file-size threshold breach without documented exception, wrong boundary in touched path), missing error handling, weak test design, durable doc claim already false.
- **Minor (Nice To Have)**: style, naming polish, optimization opportunity, comment hygiene, out-of-scope improvement.

Findings on untouched code are Minor unless the change makes them unsafe.

## Result

Apply this gate.

- **Ready to merge: Yes** — no Critical or Important findings remain.
- **Ready to merge: With fixes** — only Critical / Important findings fixable by the implementer; reviewer re-runs after fixes.
- **Ready to merge: No** — fundamental architecture, scope, or correctness problem requires artifact (plan or acceptance) revision, not just code.

Minor findings do not block. List but do not require tracking in the plan.

### Iteration Rule

**With fixes** → implementer applies Critical / Important findings, same review re-runs on changed diff. Stop after **two cycles** in same phase — escalate with unresolved findings rather than running a third. Cycle 2 findings not visible in cycle 1 must be labeled `introduced-in-cycle-2` with a reason; signal that review scope is expanding rather than code failing.

## Output

Lead with strengths (specific, brief), then findings, then result.

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

Substantial reviews → save record in `docs/reviews/YYYY-MM-DD-<topic>-code-quality-review.md`.

## Do Not

- Mark nitpicks as Critical.
- Give vague findings ("improve error handling"). Be specific.
- Review code you did not actually read.
- Avoid a clear verdict.
- Recommend broad rewrites or new dependencies as required fixes.
- Auto-chain into a second follow-on review.
