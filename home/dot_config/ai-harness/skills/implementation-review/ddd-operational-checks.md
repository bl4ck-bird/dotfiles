# DDD Operational Checks

다음 조건에서 로드한다:

- `.ai-harness/CONTEXT.md` 또는 `.ai-harness/DOMAIN_MODEL.md`가 존재하고, **동시에**
- diff가 도메인 코드(엔티티, 애그리게이트, 값 객체, 도메인 서비스, 리포지토리, 포트,
  anti-corruption layer, 도메인 이벤트)를 건드릴 때.

그 외에는 건너뛴다. 일반 CRUD/glue/UI는 DDD 리뷰가 필요 없다 — `implementation-review`의
섹션 1(Code Quality), 3(Testing), 4(Durable Docs Drift), 5(Production Readiness)로
충분하다.

## What This File Owns

DDD 관련 발견 사항. harness 전체 SSOT 대상: ubiquitous-language drift, 애그리게이트
불변식/일관성 경계, bounded-context 경계 + anti-corruption layer, 엔티티 vs 값 객체
구분, 애플리케이션 서비스 vs 도메인 서비스 분리, 리포지토리/포트 형태.

SOLID, 파일/복잡도 임계값, Coverage Matrix는 프로젝트 유형과 무관하게
`implementation-review/SKILL.md`에 있다.

## Operational Checks (Seven)

### 1. Ubiquitous Language

- 식별자(클래스, 함수, 테이블, 이벤트, 로그, 테스트 이름)가 `.ai-harness/CONTEXT.md`와
  `.ai-harness/DOMAIN_MODEL.md`의 용어집과 일치하는지.
- 동의어 혼용을 플래그("Account"/"User"/"Member"가 뒤섞여 쓰이는 경우).
- 정의되지 않은 용어를 플래그 — 용어집 항목 없이 코드에 등장하는 새 도메인 단어.
- 테스트 이름도 포함된다. `it('lets a member join a workspace')`도 같은 용어를 써야
  한다.

확인 방법(셸 접근 권한이 없는 리뷰어는 Grep/Glob 툴로 재현하거나, dispatch하는
에이전트에게 아래를 실행하고 출력을 공유해달라고 요청한다):

```bash
# Grep the diff for domain identifiers
git diff --name-only <base>..<head> | xargs grep -n -E '(class|function|interface|type) [A-Z]'
# Cross-reference with .ai-harness/CONTEXT.md glossary
grep -nE '^- [*`]?[A-Z][A-Za-z]+' .ai-harness/CONTEXT.md
```

Finding template:

> **Important** — `<file:line>` introduces `Foo` not in `.ai-harness/CONTEXT.md` glossary. Add `Foo` or
> rename to an existing term. Synonym drift creates ubiquitous-language decay.

### 2. Aggregate Invariants

- `.ai-harness/DOMAIN_MODEL.md`에 있는(또는 암묵적으로 존재하는) 각 불변식은 공개
  인터페이스나 도메인 이벤트를 통과하는 테스트를 최소 하나 가져야 한다.
- 규약/주석으로만 강제되고 테스트가 없는 불변식은 플래그.

| Invariant | Required proof |
| --- | --- |
| "Workspace owner cannot be removed from their own workspace" | `Workspace.removeMember(ownerId)` throws/refuses |
| "Order total equals sum of line items" | Mutating any line item updates total, or `Order.create` rejects mismatched totals |
| "Payment cannot be captured twice" | Second capture is no-op or throws |

Finding template:

> **Important** — `.ai-harness/DOMAIN_MODEL.md` lists invariant "<text>" but no test in this diff
> proves it via a public interface. Add a behavior test through `<Aggregate>.<method>`.

### 3. Bounded-Context Boundaries

- 명시적인 변환 계층 없이 다른 컨텍스트의 애그리게이트/값 객체를 import하지 않는다.
- `.ai-harness/CONTEXT-MAP.md`가 경계와 변환 스타일(ACL, shared kernel, published
  language)을 정의한다.
- `inventory` 안에서 `import { Order } from '../billing/Order'`처럼 직접 import하면,
  `.ai-harness/CONTEXT-MAP.md`에 예외가 기록되어 있지 않은 한 finding이다.

Finding template:

> **Critical** — `<file:line>` imports `Order` from `billing` directly. `.ai-harness/CONTEXT-MAP.md`
> requires translation through `BillingAdapter`. Replace with the adapter call.

### 4. Anti-Corruption Layer

- 외부 통합(HTTP 클라이언트, SDK, 큐 컨슈머)은 경계에서 변환한다. 외부 타입은 도메인
  코드에 등장하지 않는다.
- REST 핸들러가 Stripe API 객체를 그대로 반환하면 Stripe의 스키마가 그대로
  노출된다 — 다운스트림 결합도에 따라 Critical 또는 Important.
- 수정: 외부 타입 → 도메인이 소유하는 값 객체/DTO로 변환하는 translator를 어댑터에
  둔다.

### 5. Entity vs Value Object Discipline

- 엔티티는 정체성이 중요할 때 정체성과 생명주기를 가진다(ID를 가진 `User`, slug를
  가진 `Workspace`).
- 값 객체는 불변이고, 값으로 동등성을 비교하며, 개념을 검증한다(`Email`, `Money`,
  `DateRange`).
- 흔한 드리프트:
  - 생성자 검증이 없는 값 객체 → `Email("not-an-email")`이 그대로 통과.
  - 구조적으로 비교되는 엔티티 → 캐시 키 충돌, stale reference.
  - UUID를 자동 생성하는 값 객체 → 정체성을 가진다는 뜻이므로 사실은 엔티티다.
- 드리프트가 런타임 버그를 낳을 수 있으면 Important; 순전히 스타일 문제면 Minor.

### 6. Application vs Domain Services

- **Domain service**: 하나의 엔티티/VO에 속하지 않지만 도메인 타입만으로 동작하는
  규칙(`TransferPolicy.canTransfer(from, to, amount)`).
- **Application service**: 유스케이스를 오케스트레이션하고, 트랜잭션 경계를 소유하며,
  애그리게이트를 로드하고, 이벤트를 디스패치한다(`TransferFunds.execute(command)`).
- 플래그할 드리프트:
  - 애플리케이션 서비스 안의 도메인 로직("transfer allowed when
    `from.balance >= amount`"를 인라인으로 — `Transfer` 애그리게이트나 도메인 서비스에
    있어야 함).
  - 도메인 안의 애플리케이션 관심사(엔티티가 DB, HTTP 클라이언트, `Date.now()`에 접근).

### 7. Repositories / Ports

- Repository = 실제 경계(애그리게이트의 영속화).
- Port = 도메인이 소유하는 상호작용(알림, 결제, 이벤트 발행).
- 가짜 추상화를 플래그:
  - `UserRepository.findById`가 한 줄짜리 `db.query` 래퍼일 뿐이면 → 인라인 처리.
  - 구현 변형의 가능성이 전혀 보이지 않는 "Port"(어댑터 하나, 유스케이스 하나) →
    투기적(speculative)인 Minor.
- "실제 경계"인지 검증하는 방법: 구현을 교체하면 실제로 의미가 달라지는가?(테스트용
  in-memory vs 실제 DB.) 현실적인 대안이 없다면 → 장식(decoration)일 뿐이다.

## How To Apply

1. diff가 도메인 코드를 건드리는지 확인한다. 아니라면 건너뛴다.
2. diff에 대해 각 체크를 실행한다.
3. 각 발견은 `implementation-review` Scope Discipline에 따라 file:line을 인용한다.
4. Severity는 `implementation-review` 기준을 따른다:
   - **Critical**: 데이터 무결성 위험을 만드는 크로스 컨텍스트 결합, 다운스트림
     의존이 있는 상태로 도메인 코드에 새어 나온 외부 타입, 문서화된
     safety-critical 규칙에 대한 누락된 불변식 테스트.
   - **Important**: ubiquitous language drift, 누락된 불변식 테스트, 런타임 영향이
     있는 entity vs VO drift, 애플리케이션 서비스 안의 도메인 로직.
   - **Minor**: 투기적 port, 한 줄짜리 repository, 네이밍 다듬기.

## Scope Discipline

부모 스킬과 동일 — 발견은 건드린 범위 안에서만, 필수 수정으로 광범위한 재작성을
요구하지 않는다. 범위 밖 DDD 개선은 Minor.

## Output

발견 사항은 `implementation-review` 출력의 각 severity 항목 아래로 들어간다. 별도
output 없음.
