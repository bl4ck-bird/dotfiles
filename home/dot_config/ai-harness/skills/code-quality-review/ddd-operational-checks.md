# DDD Operational Checks

Load this reference when:

- `CONTEXT.md` or `docs/DOMAIN_MODEL.md` exists in the project, **and**
- The diff under review touches domain code (entities, aggregates, value objects,
  domain services, repositories, ports, anti-corruption layers, or domain events).

If either condition is absent, skip this file. General CRUD / glue / UI work does not
need DDD review — `code-quality-review` SKILL.md sections 1 (Code Quality), 3
(Testing), 4 (Durable Docs Drift), and 5 (Production Readiness) are sufficient.

## What This File Owns

DDD-specific findings in code-quality review. The harness-wide SSOT for:

- Ubiquitous-language drift.
- Aggregate invariants and consistency boundaries.
- Bounded-context boundaries and anti-corruption layers.
- Entity vs value object discipline.
- Application vs domain service separation.
- Repository / port shape (real boundary vs CRUD wrapper).

SOLID, file/complexity thresholds, and the Coverage Matrix live in
`code-quality-review/SKILL.md` regardless of project type.

## Operational Checks (Seven)

### 1. Ubiquitous Language

- Code identifiers (class, function, table, event, log message names) match the
  glossary in `CONTEXT.md` and `docs/DOMAIN_MODEL.md`.
- Flag synonyms ("Account" vs "User" vs "Member" used interchangeably).
- Flag undefined terms — new domain words appearing in code without a matching entry
  in `CONTEXT.md`.
- Test names also count. `it('lets a member join a workspace')` must use the same
  terms as the domain code under test.

How to check:

```bash
# Grep the diff for domain identifiers
git diff --name-only <base>..<head> | xargs grep -n -E '(class|function|interface|type) [A-Z]'
# Cross-reference with CONTEXT.md glossary
grep -nE '^- [*`]?[A-Z][A-Za-z]+' CONTEXT.md
```

Finding template:

> **Important** — `<file:line>` introduces identifier `Foo` not in `CONTEXT.md`
> glossary. Either add `Foo` to the glossary as a domain term, or rename to an
> existing term. Synonym drift creates ubiquitous-language decay.

### 2. Aggregate Invariants

- Each invariant documented in `docs/DOMAIN_MODEL.md` (or implied by the aggregate's
  responsibility) has at least one test through a public interface or domain event.
- "Cannot be in state X without state Y" — verify there is a test that proves it.
- Flag invariants enforced only by convention or comment, with no test.

Examples:

| Invariant | Required proof |
| --- | --- |
| "A workspace owner cannot be removed from their own workspace" | Test: `Workspace.removeMember(ownerId)` throws / refuses |
| "An order's total equals the sum of its line items" | Test: mutating any line item updates the total, or `Order.create` rejects mismatched totals |
| "A payment cannot be captured twice" | Test: second capture call is a no-op or throws |

Finding template:

> **Important** — `docs/DOMAIN_MODEL.md` lists invariant "<text>" but no test in this
> diff (or in the existing suite) proves it via a public interface. Add a behavior
> test through `<Aggregate>.<method>`.

### 3. Bounded-Context Boundaries

- No imports of another bounded context's aggregates or value objects without an
  explicit translation layer.
- `CONTEXT-MAP.md` defines the boundaries and the translation style (anti-corruption
  layer, shared kernel, published language, etc.).
- A direct import like `import { Order } from '../billing/Order'` inside the
  `inventory` context is a finding unless `CONTEXT-MAP.md` records an exception.

Finding template:

> **Critical** — `<file:line>` imports `Order` from the `billing` context directly.
> `CONTEXT-MAP.md` requires translation through `BillingAdapter`. This couples
> `inventory` to `billing`'s internal model. Replace with the adapter call.

### 4. Anti-Corruption Layer

- External integrations (HTTP clients, third-party SDKs, queue consumers) translate
  at the boundary. External types do not appear in domain code.
- A REST handler that returns a Stripe API object directly leaks Stripe's schema into
  the domain — that is a Critical / Important finding depending on how much downstream
  code now depends on Stripe-shaped types.
- The fix: introduce a translator at the adapter that maps the external type into a
  domain-owned value object or DTO.

### 5. Entity vs Value Object Discipline

- Entities have identity and lifecycle when identity matters (a `User` with an ID; a
  `Workspace` with a slug).
- Value objects are immutable, equality-by-value, and validate the concept they
  encode (`Email`, `Money`, `DateRange`).
- Common drift:
  - A value object missing validation in its constructor → `Email("not-an-email")`
    is accepted.
  - An entity treated as a value (compared by structural equality) → cache key
    collisions, stale references.
  - A value object with a generated UUID → it has identity, it is an entity.
- Apply Important when the drift can produce a runtime bug. Apply Minor when it is
  purely style.

### 6. Application vs Domain Services

- **Domain service**: a rule that does not naturally belong to one entity or value
  object but operates on domain types only (e.g., `TransferPolicy.canTransfer(from,
  to, amount)` — pure domain).
- **Application service**: orchestrates a use case, owns transaction boundaries,
  loads aggregates from repositories, dispatches events (e.g.,
  `TransferFunds.execute(command)`).
- Drift to flag:
  - Domain logic creeping into application services ("a transfer is allowed when
    `from.balance >= amount`" inline in an application service — should be in the
    `Transfer` aggregate or a domain service).
  - Application concerns leaking into domain code (a domain entity reaching for the
    database, the HTTP client, or `Date.now()`).

### 7. Repositories / Ports

- A repository represents a real boundary — the persistence of an aggregate.
- A port represents an interaction the domain owns (sending a notification, charging
  a card, publishing an event).
- Flag fake abstractions:
  - `UserRepository` with one method `findById` that is a one-line wrapper around
    `db.query` is not a real boundary. Inline the query.
  - A "port" with no implementation variation in sight (only one adapter, only one
    use case) is speculative — flag as Minor.
- The test for "real boundary": does swapping the implementation matter? In-memory
  for tests, real database in production. If there is no realistic alternative
  implementation, the port is decoration.

## How To Apply

1. Confirm the diff touches domain code. If not, do not run these checks.
2. Run each check against the diff.
3. Each finding cites a file:line in the diff per `code-quality-review` Scope
   Discipline.
4. Severity per `code-quality-review` Severity definitions:
   - **Critical**: cross-context coupling that creates data-integrity risk, leaked
     external types in domain code that downstream depends on, missing invariant test
     for a documented safety-critical rule.
   - **Important**: ubiquitous language drift, missing invariant test, entity vs
     value-object drift with runtime impact, domain logic in application service.
   - **Minor**: speculative port, one-line repository, naming polish.

## Scope Discipline

Same as the parent skill — findings inside the touched surface, no broad rewrites
proposed as required fixes. Outside-scope DDD improvements are Minor.

## Output

These findings feed into the `code-quality-review` output format under each severity
heading. There is no separate output for this file.
