# DDD Operational Checks

Load when:

- `CONTEXT.md` or `docs/DOMAIN_MODEL.md` exists, **and**
- The diff touches domain code (entities, aggregates, value objects, domain services,
  repositories, ports, anti-corruption layers, domain events).

Otherwise skip. General CRUD/glue/UI does not need DDD review — `code-quality-review`
sections 1 (Code Quality), 3 (Testing), 4 (Durable Docs Drift), 5 (Production Readiness) are
sufficient.

## What This File Owns

DDD-specific findings. Harness-wide SSOT for: ubiquitous-language drift, aggregate
invariants/consistency boundaries, bounded-context boundaries + anti-corruption layers,
entity vs value object discipline, application vs domain service separation, repository/port
shape.

SOLID, file/complexity thresholds, Coverage Matrix live in `code-quality-review/SKILL.md`
regardless of project type.

## Operational Checks (Seven)

### 1. Ubiquitous Language

- Identifiers (class, function, table, event, log, test names) match `CONTEXT.md` and
  `docs/DOMAIN_MODEL.md` glossary.
- Flag synonyms ("Account"/"User"/"Member" interchanged).
- Flag undefined terms — new domain words appearing in code without a glossary entry.
- Test names count. `it('lets a member join a workspace')` must use the same terms.

How to check:

```bash
git diff --name-only <base>..<head> | xargs grep -n -E '(class|function|interface|type) [A-Z]'
grep -nE '^- [*`]?[A-Z][A-Za-z]+' CONTEXT.md
```

Finding template:

> **Important** — `<file:line>` introduces `Foo` not in `CONTEXT.md` glossary. Add `Foo` or
> rename to an existing term. Synonym drift creates ubiquitous-language decay.

### 2. Aggregate Invariants

- Each invariant in `docs/DOMAIN_MODEL.md` (or implied) has at least one test through a
  public interface or domain event.
- Flag invariants enforced only by convention/comment with no test.

| Invariant | Required proof |
| --- | --- |
| "Workspace owner cannot be removed from their own workspace" | `Workspace.removeMember(ownerId)` throws/refuses |
| "Order total equals sum of line items" | Mutating any line item updates total, or `Order.create` rejects mismatched totals |
| "Payment cannot be captured twice" | Second capture is no-op or throws |

Finding template:

> **Important** — `docs/DOMAIN_MODEL.md` lists invariant "<text>" but no test in this diff
> proves it via a public interface. Add a behavior test through `<Aggregate>.<method>`.

### 3. Bounded-Context Boundaries

- No imports of another context's aggregates/value objects without an explicit translation
  layer.
- `CONTEXT-MAP.md` defines boundaries and translation style (ACL, shared kernel, published
  language).
- Direct import `import { Order } from '../billing/Order'` inside `inventory` is a finding
  unless `CONTEXT-MAP.md` records an exception.

Finding template:

> **Critical** — `<file:line>` imports `Order` from `billing` directly. `CONTEXT-MAP.md`
> requires translation through `BillingAdapter`. Replace with the adapter call.

### 4. Anti-Corruption Layer

- External integrations (HTTP clients, SDKs, queue consumers) translate at the boundary.
  External types do not appear in domain code.
- REST handler returning a Stripe API object directly leaks Stripe's schema — Critical or
  Important depending on downstream coupling.
- Fix: translator at the adapter mapping external type → domain-owned value object/DTO.

### 5. Entity vs Value Object Discipline

- Entities have identity and lifecycle when identity matters (`User` with ID, `Workspace`
  with slug).
- Value objects are immutable, equality-by-value, validate the concept (`Email`, `Money`,
  `DateRange`).
- Common drift:
  - Value object missing constructor validation → `Email("not-an-email")` accepted.
  - Entity compared structurally → cache-key collisions, stale references.
  - Value object with generated UUID → it has identity, it is an entity.
- Important when drift can produce a runtime bug; Minor when purely style.

### 6. Application vs Domain Services

- **Domain service**: rule that does not belong to one entity/VO but operates on domain types
  only (`TransferPolicy.canTransfer(from, to, amount)`).
- **Application service**: orchestrates a use case, owns transaction boundaries, loads
  aggregates, dispatches events (`TransferFunds.execute(command)`).
- Drift to flag:
  - Domain logic in application services ("transfer allowed when `from.balance >= amount`"
    inline — belongs in `Transfer` aggregate or domain service).
  - Application concerns in domain (entity reaching for DB, HTTP client, `Date.now()`).

### 7. Repositories / Ports

- Repository = real boundary (persistence of an aggregate).
- Port = interaction domain owns (notification, charge, publish event).
- Flag fake abstractions:
  - `UserRepository.findById` as one-line `db.query` wrapper → inline.
  - "Port" with no implementation variation in sight (one adapter, one use case) → Minor
    speculative.
- Test for "real boundary": does swapping the implementation matter? (In-memory for tests vs
  real DB.) No realistic alternative → decoration.

## How To Apply

1. Confirm diff touches domain code. If not, skip.
2. Run each check against the diff.
3. Each finding cites a file:line per `code-quality-review` Scope Discipline.
4. Severity per `code-quality-review`:
   - **Critical**: cross-context coupling creating data-integrity risk, leaked external types
     in domain code with downstream dependence, missing invariant test for documented
     safety-critical rule.
   - **Important**: ubiquitous language drift, missing invariant test, entity vs VO drift
     with runtime impact, domain logic in application service.
   - **Minor**: speculative port, one-line repository, naming polish.

## Scope Discipline

Same as parent skill — findings inside the touched surface, no broad rewrites as required
fixes. Outside-scope DDD improvements are Minor.

## Output

Findings feed `code-quality-review` output under each severity heading. No separate output.
