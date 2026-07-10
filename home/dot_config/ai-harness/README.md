# BB Harness

중앙집중식 에이전트 워크플로우, 프로젝트 템플릿, 스킬, 리뷰어 에이전트, 보수적인 훅 모음 —
chezmoi로 관리된다.

임기응변식 Claude Code / Codex / 스킬 사용을 재시작 가능한 사이드 프로젝트 워크플로우로 전환한다.
목표: 에이전트 세션이 끝난 뒤에도 제품 의도, acceptance criteria, 계획, 검증, 리뷰 결정, 잔존
위험이 검사 가능한 상태로 남는 것.

이 README는 사람을 위한 것이다. 에이전트는 `AGENTS.md`, 프로젝트 로컬 지침,
`skills/*/SKILL.md`를 실행 가능한 source of truth로 취급한다. README는 스킬로 링크할 뿐 그
규칙을 중복 기술하지 않는다.

## 설계 목표

- 작업에 맞는 워크플로우 경로.
- 존재한다면 임기응변보다 스킬/플러그인을 우선.
- 채팅 밖에 남는 durable context.
- 사소하지 않은 작업은 구현 전에 리뷰 가능해야 함.
- 품질을 지킬 만큼 충분히 견고한 경량 acceptance artifact.
- context를 낭비하지 않고 실행되는 compact plan.
- 반복 가능한 검증을 위한 TDD + 프로젝트 훅.
- 위험이 정당화할 때만 독립 리뷰, 기본 의례로는 아님.

## 프로젝트에 맞춘 적응

도메인 / DDD / 보안 깊이는 **파일 존재 여부로 opt-in**된다:

- `.ai-harness/CONTEXT.md`나 `.ai-harness/DOMAIN_MODEL.md`가 있으면: `implementation-review`가
  DDD 체크를 수행하고, `write-spec`/`write-plan`의 Self-Review가 도메인 정합성을 검증한다.
- 해당 문서가 없으면: 그 체크들은 자동으로 건너뛴다. 하니스는 여전히 범용 TDD/리뷰
  워크플로우로 동작한다.
- 보안 깊이(`security-review`, `second-review`)는 diff가 보안에 민감한 표면이나 High-Risk
  Surface를 건드릴 때만 트리거된다.
- 스캐폴딩은 초기 문서 세트(`CONTEXT.md`, `CURRENT.md`, `adr/` + host 파일)만 생성한다. 그 외
  모든 durable doc은 해당 관심사를 결정하는 스킬이 생성한다.

작은 CLI = TDD + implementation-review + ship. 도메인 비중이 큰 앱 = 동일한 스킬 + DDD 체크.

## 레이아웃

- `AGENTS.md` — 코딩 에이전트(Claude, Codex, Gemini)를 위한 공유 글로벌 기본값.
- `skills/` — 실행 가능한 워크플로우 스킬. `using-bb-harness`가 bootstrap + router 역할.
- `claude-agents/` — Claude Code의 named subagent(얇은 dispatcher). `skills/<name>/SKILL.md`에
  위임하는 두 리뷰어: `implementation-reviewer`, `security-reviewer`. 그리고 `explore-lite` —
  순수 사실 수집(검색/grep/읽기/웹 조회)을 위한 읽기 전용 `model: haiku` 조회 에이전트로,
  `dispatching-parallel-agents`와 `subagent-driven-development`가 저비용 작업을 메인 모델에서
  분리하는 데 사용한다. 모델 티어링은 Claude 전용이며, 다른 host(Codex, Gemini)는
  `claude-agents/`를 무시한다. `second-review`는 Claude subagent가 없다 — 다른 모델의 리뷰어가
  필요하다(`skills/second-review` 참고). `receiving-review`는 구현자 측 동작이지 subagent가
  아니다.
- `hooks/` — 보수적인 훅 스크립트. 기본적으로 전역 연결되어 있지 않다.
- `templates/project/` — 초기 프로젝트 지침과 durable docs. 루트 레벨 `AGENTS.md`/`CLAUDE.md`와
  CONTEXT 및 모든 워크플로우 문서를 담은 `.ai-harness/` 트리(chezmoi source
  `dot_ai-harness/`). 단일 `project/` nest 구조는 구조 변경 없이 향후 템플릿 카테고리(예:
  `library/`, `service/`, `skill/`)를 위한 여지를 남긴다.

## 링크 전략

chezmoi는 `~/.config/ai-harness`를 source of truth로 설치한 뒤, 에이전트가 참조하는 위치로
링크를 되돌려 건다:

- `~/.codex/AGENTS.md` → `~/.config/ai-harness/AGENTS.md`
- `~/.claude/CLAUDE.md` → `~/.config/ai-harness/AGENTS.md`
- `~/.gemini/GEMINI.md` → `~/.config/ai-harness/AGENTS.md`  *(파일 하나가 셋 다 담당)*
- `~/.codex/skills/<name>` → `~/.config/ai-harness/skills/<name>` *(스킬별 symlink들의 실제
  디렉터리 — Codex가 자신의 skills 디렉터리 안에 `.system/`을 자동 생성하는데, 이것이 공유
  SSOT를 오염시켜서는 안 된다)*
- `~/.claude/skills` → `~/.config/ai-harness/skills`
- `~/.gemini/skills` → `~/.config/ai-harness/skills`
- `~/.claude/agents/<agent>.md` → `~/.config/ai-harness/claude-agents/<agent>.md`

새 스킬 디렉터리를 추가할 때는 chezmoi `home/dot_codex/skills/` 아래에 대응하는
`symlink_<name>.tmpl`도 추가한다. Claude와 Gemini는 디렉터리 전체 symlink를 사용하므로
스킬별 항목이 필요 없다.

도구별 런타임 설정은 각자의 네이티브 config 디렉터리 아래에 그대로 둔다 — Codex는 chezmoi
`create_private_`을 사용하고(최초 생성 후 도구가 소유), Claude/Gemini는 `private_`을
사용한다(chezmoi로 동기화됨).

## 스킬 분리 기준

스킬을 추가/분리/병합하기 전 네 가지 모두 적용한다:

1. **절차 길이** — 불릿 1-3개로 충분한가? 그러면 inline 유지. grep 명령, 문서 추적, 다단계
   의사결정일 때만 분리.
2. **Opt-in 신호** — 체크가 특정 신호(도메인 비중이 큼, 타입 언어, 결제, sync)에만 적용될
   때만 분리. 항상 적용되는 체크는 inline 유지.
3. **재사용** — 여러 스킬/단계가 동일한 체크를 호출할 때만 분리.
4. **ROI 대 노이즈** — inline이 무관한 프로젝트의 context를 눈에 띄게 부풀릴 때만 분리.

채택된 패턴(Hexagonal, CQRS, Event Sourcing)은 채택한 프로젝트의 `.ai-harness/ARCHITECTURE.md`나
`.ai-harness/adr/`에 두며, 글로벌 스킬에는 두지 않는다.

DDD operational checks, SOLID, 파일/복잡도 임계값, Coverage Matrix, durable docs drift 체크는
`skills/implementation-review/SKILL.md`가 SSOT로 소유한다. 상류(upstream) 변형(도메인 정합성,
계획 시점의 SOLID)은 `write-spec` / `write-plan`의 Self-Review에 inline된다.

### 표기 관례

- 표/간단 언급: 짧은 형식(`5+ files`, `300/600 lines`).
- 산문: 긴 형식(`five or more files`, `300 lines / 600 lines`).
- 숫자 임계값은 canonical하며 두 형식에서 동일하다.
- 교차 참조에서 독립 리뷰어는 `second-review`로 지칭한다. Codex는 기본 연동으로서
  `skills/second-review/SKILL.md` 안에서만 이름이 명시된다.
- 파일/복잡도 임계값은 `skills/implementation-review/SKILL.md`(File And Complexity
  Thresholds)에 정의된다. 다른 문서는 재정의하지 않고 참조만 한다.

### SSOT와 호출 지점

각 canonical list나 임계값은 정확히 하나의 스킬에만 존재한다: High-Risk Surfaces →
`second-review`; Acceptance Brief Fields → `write-spec`; protected base branches →
`using-bb-harness` Branch Policy; SOLID / 파일 임계값 / Coverage Matrix →
`implementation-review`. 호출 시점 분기를 유도하는 짧은 목록은 같은 괄호 안에 SSOT를 명시하는
괄호 리마인더로 inline될 수 있다. 전체 정의는 절대 중복 기술하지 않는다. canonical list를
변경할 때는 그 호출 지점을 grep해서 같은 변경 안에서 함께 업데이트한다.

## 리뷰어 페어 패턴 (유지보수)

`implementation-review`를 위해 두 가지 리뷰어 유형이 병렬로 존재한다:

| 파일 | 역할 |
| --- | --- |
| `skills/subagent-driven-development/<name>-reviewer-prompt.md` | Canonical 리뷰어 프롬프트 — `general-purpose` fallback을 통해 모든 host가 사용. Self-contained. |
| `claude-agents/<name>-reviewer.md` | Claude Code named-subagent 정의 — Claude 전용, symlink로 `~/.claude/agents/`에 위치. canonical 프롬프트의 축약 미러. |

리뷰어 규칙(severity, scope guard, 출력 형식, follow-on 로직 등)을 업데이트할 때는 **두 파일
모두** 업데이트한다. 다른 host(Codex, Gemini)는 `claude-agents/`를 완전히 무시한다 — 이들에게는
sdd 템플릿으로 충분하다. `security-reviewer`는 `claude-agents/`에만 존재하는데, 그 sdd
dispatch가 `implementation-reviewer-prompt.md`의 follow-on 로직으로 처리되기 때문이다.

## Skill-First 태도

BB Harness를 사용할 때 스킬이 곧 워크플로우 표면이다. Skill-first ≠ "모든 스킬을 로드"다:

- 단계가 불명확하면 `using-bb-harness`로 시작/재개한다.
- 작업이 명확히 하나의 스킬에 대응되면 해당 스킬을 바로 사용한다.
- 즉흥이 아니라 스킬을 통해 단계에서 단계로 이동한다.
- 작업이 명백히 작거나 로컬이거나, 스킬이 작업을 실질적으로 보호하지 못할 때만 관련 스킬을
  건너뛴다 — 이유를 기록한다.

## 워크플로우 모델

차용한 것들: Superpowers (design → plan → TDD → review → finish), gstack
(Think/Plan/Build/Review/Test/Ship/Retro), stacked PR practice (논리적 리뷰 레이어별
commit/branch — `subagent-driven-development`의 Workspace Isolation과 `ship-check`의
Finishing Options 참고), Claude feature/review plugin (위험이 정당화할 때 집중 리뷰어).

기본 non-trivial 흐름:

```text
using-bb-harness
-> product-discovery (goal/users/MVP/non-goals unclear)
-> pressure-test (assumptions unclear or risky)
-> domain-modeling (domain language or boundaries matter)
-> write-spec (Self-Review: Product Clarity + Domain Alignment)
-> write-plan (Self-Review: Plan Hygiene + Architecture Soundness)
-> using-git-worktrees (isolated workspace)
-> subagent-driven-development as controller
   per task:
     implementer subagent (test-driven-development inside)
     -> controller verification (tests + diff)
   per slice:
     implementation-review subagent (spec compliance ✅/❌ + Ready to merge? Yes / With fixes / No)
     -> security-review subagent (when triggered)
     -> second-review (different-model reviewer) (high-risk path: required)
     -> receiving-review (between reviewer feedback and next fix)
-> docs-sync
-> ship-check
-> commit/stack gate (only when explicitly approved/required)
```

Acceptance/spec/plan 소유권: `skills/write-spec/SKILL.md`(Application Rules)와
`skills/write-plan/SKILL.md` 참고. Canonical Acceptance Brief 필드는 `write-spec`에 있다.

워크플로우 경로 3분류 정의(light / standard / high-risk): `skills/using-bb-harness/SKILL.md`
(Workflow Path).

## 스킬 맵

`skills/using-bb-harness/SKILL.md`의 Routing을 미러링한 것. 스킬이 source of truth다.

| 상황 | 스킬 |
| --- | --- |
| 워크플로우 경로와 다음 단계 선택 | `using-bb-harness` |
| 프로젝트 지침 시작 또는 갱신 | `project-scaffold` |
| 제품 방향이 불명확 | `product-discovery` |
| 가정을 검증해야 함 | `pressure-test` |
| 도메인 언어나 경계가 중요 | `domain-modeling` |
| acceptance artifact와 슬라이스 생성 (Self-Review 포함) | `write-spec` |
| compact 구현 계획 생성 (Self-Review 포함) | `write-plan` |
| 리뷰된 다중 task 계획 실행 (host가 subagent 지원) | `subagent-driven-development` |
| 리뷰된 계획을 inline으로 실행 (subagent 없음, 또는 작은 task 1-3개) | `executing-plans-inline` |
| 실행 전 격리된 worktree 설정 | `using-git-worktrees` |
| red-green-refactor로 동작 구현 | `test-driven-development` |
| 버그나 회귀 진단 | `bug-diagnosis` |
| 독립적인 조사/재현/리서치 2개 이상을 동시에 | `dispatching-parallel-agents` |
| 구현된 슬라이스 리뷰 (spec compliance + 품질, 한 번에) | `implementation-review` |
| auth, secrets, crypto, deletion, untrusted input, data loss 리뷰 | `security-review` |
| 독립적인 double-check (다른 모델 리뷰어) | `second-review` |
| 리뷰어 피드백 처리 (검증, push back, 하나씩 적용) | `receiving-review` |
| 동작이나 워크플로우 변경 후 문서 동기화 | `docs-sync` |
| 최종 handoff, 검증, 잔존 위험 확인 | `ship-check` |
| `ship-check`나 어떤 리뷰가 현재 세션 이후에도 남아야 할 memory candidate나 retro insight를 보고할 때 | `retro-capture` |
| bounded 자율 반복 계속 | `bounded-loop` |

## 리뷰 라우팅

상세 라우팅: `skills/using-bb-harness/SKILL.md`(Review Routing)와 각 리뷰 스킬. 작업을 보호할
수 있는 가장 가벼운 리뷰를 사용한다.

독립적인 second review는: `second-review` 스킬(다른 모델 리뷰어가 기본 + fallback 절차).

## 커밋 및 스택 게이트

상세 동작: `skills/ship-check/SKILL.md`(Commit / Stack Gate). 기본값: commit/PR/stack 작업은
명시적 사용자 승인, 프로젝트 로컬 지침, 또는 승인된 bounded goal이 있을 때만 실행된다.

Stacked 워크플로우: `skills/subagent-driven-development/SKILL.md`(Workspace Isolation) +
`skills/ship-check/SKILL.md`(Finishing Options + Worktree Cleanup Provenance).

## 검증

동작 변경은 `test-driven-development`를 사용한다(red-green-refactor, 실패하는
public-interface 테스트를 먼저 하나 작성). 버그는 `bug-diagnosis`로 시작한 뒤 수정을 위해
TDD로 돌아온다.

수동/브라우저 QA보다 자동화된 프로젝트 체크(focused test, 위험이 정당화될 때 전체 테스트,
typecheck, lint, build, 프로젝트 훅)를 우선한다. 자동화 체크가 잘 커버하지 못하는 동작에는
수동 체크를 사용한다.

프로덕션 동작 변경은 명시적 사용자 승인 + 기록된 residual-risk 이유가 있을 때만 TDD를
건너뛸 수 있다. 전체 규칙: `skills/test-driven-development/SKILL.md`.

## 스캐폴드 세트

`project-scaffold`는 초기 세트 하나를 생성한다: `AGENTS.md`, `CLAUDE.md`(@AGENTS.md + Claude
wiring), `GEMINI.md`(symlink), `.ai-harness/CONTEXT.md`, `.ai-harness/CURRENT.md`,
`.ai-harness/AGENT_WORKFLOW.md`, `.ai-harness/adr/`(MADR 템플릿), 빈 `specs/`, `plans/`,
`reviews/` 디렉터리. 그 외 모든 durable doc은 이를 생성하는 스킬이 만든다(ROADMAP은
`product-discovery`, DOMAIN_MODEL은 `domain-modeling`, ADR은 `write-spec`/`write-plan` 등).

의존성 설치는 기본적으로 사용자가 관리한다. 에이전트는 명령을 제안할 수 있지만 요청받지 않는
한 설치를 실행하지 않는다. 의존성 추가/교체/업그레이드 시 프로젝트 lefthook 훅이 언어에 맞는
audit 도구(npm audit / pip-audit / cargo audit / govulncheck)를 실행해야 한다. `write-plan`의
Self-Review가 그 근거를 기록한다.

## Durable Docs

별도 소유권:

- `.ai-harness/CONTEXT.md` — 제품 정체성, canonical 용어, 현재 경계.
- `.ai-harness/CONTEXT-MAP.md` — 다중 context, 앱, 패키지, 통합.
- `.ai-harness/CURRENT.md` — 단계, 활성 acceptance artifact/source, blocker, 마지막 검증,
  다음 액션.
- `.ai-harness/AGENT_WORKFLOW.md` — 프로젝트 로컬 오버라이드; `using-bb-harness` 규칙을
  중복하지 않음.
- `.ai-harness/ROADMAP.md` — 제품 목표, MVP, 마일스톤, parking lot.
- `.ai-harness/ARCHITECTURE.md` — 경계, 레이어, 의존성 규칙, 트레이드오프.
- `.ai-harness/DOMAIN_MODEL.md` — 도메인 용어, invariant, 워크플로우, entity, value object.
- `.ai-harness/DATA_MODEL.md` — 저장소, 보존, 삭제, 마이그레이션, 백업.
- `.ai-harness/SECURITY_MODEL.md` — secrets, auth, 권한, trust boundary, 민감 데이터.
- `.ai-harness/TESTING_STRATEGY.md` — TDD 규칙, 테스트 레벨, 검증 명령, 훅.
- `.ai-harness/specs/` — 임시 feature spec.
- `.ai-harness/plans/` — compact 구현 계획.
- `.ai-harness/reviews/` — 실질적인 리뷰 기록, handoff, 프로젝트 로컬 retro.
- `.ai-harness/adr/` — MADR 형식 ADR, 되돌리기 어렵고 놀라운 트레이드오프에만.

위 항목은 모두 `.ai-harness/` 아래에 있으며 **gitignore 대상**이다 — 커밋된 artifact가 아니라
로컬 에이전트 context다. `AGENTS.md` / `CLAUDE.md` / `GEMINI.md`는 저장소 루트에 그대로
둔다(도구가 그 위치를 요구하기 때문)만, 이것들 역시 gitignore 대상이다. 저장소의 `docs/`
경로는 사람을 위한 제품/사용자 문서 전용으로 커밋 상태를 유지한다. 하니스는 절대 `docs/`에
생성하지 않는다. `project-scaffold`의 Gitignore Policy 참고.

프로젝트 README 파일은 사용자 대상, 하이레벨을 유지한다.

## 훅

보수적인 빌딩 블록(자세한 내용과 bypass gap은 `hooks/README.md` 참고):

- `block-dangerous-bash.sh` — 파괴적인 셸 명령 체크 + 흔한 셸 기반 secret 읽기.
- `protect-sensitive-read.sh` — `.env`, private key, credential, secret 파일에 대한 읽기 체크.
- `protect-sensitive-write.sh` — 민감 파일에 대한 쓰기 체크 + 직접적인 lockfile 편집.
- `protect-sensitive-files.sh` — read/write 훅을 분리할 수 없는 도구를 위한 호환성 wrapper.
- `session-context.sh` — 지원될 때 짧은 세션 시작 git context.

훅은 guardrail이지 샌드박스가 아니다. `tail`, `head`, `cp`, 리다이렉션, 언어 인터프리터는
이를 우회한다. 먼저 프로젝트 레벨에서 연결하고, 일상적으로 사용하기에 충분히 조용해진 뒤에만
전역으로 승격한다.

## 빠른 시작

새 프로젝트:

```text
Use using-bb-harness.
Project state: new project.
Goal: <short product idea>.
Decide workflow path, next phase, scaffold needs, approvals before editing.
```

기존 프로젝트:

```text
Use using-bb-harness.
Task: <describe>.
Read project instructions, current docs, tests, relevant code. Report workflow path, next skill, required artifact/approval, next safe action before editing.
```

작은 동작 변경:

```text
Use test-driven-development and ship-check.
Run docs-sync only if behavior/architecture/testing/user-facing behavior changes.
Change: <describe>.
```

Non-trivial 기능:

```text
Use using-bb-harness first.
Feature: <describe>.
Use relevant skills for acceptance artifact, review, compact plan, subagent-driven-development for multi-slice, TDD inside behavior-changing slices, docs sync, ship check. Keep weight proportional to risk.
```

Bounded 자율 루프:

```text
Use bounded-loop.
Goal: <specific outcome>.
Allowed scope: <files/modules/docs/commands>.
Allowed autonomous actions: <exact file areas, commands, review/fix scope, worker-agent use>.
Forbidden actions: <setup/dependencies/hooks/git history/deletes/deploys>.
Iteration budget: <max loops or timebox>.
Verification gate: <test/typecheck/lint/build/manual>.
Stop and ask if scope expands, verification fails twice for the same reason, or an unapproved product/domain/architecture/setup/destructive/git-history decision appears.
```

## 흔한 안티패턴

- 명확한 작업에 full spec.
- 파일 변경을 제약하는 대신 spec을 그대로 복사한 plan.
- 위험이 요구해서가 아니라 스킬이 존재해서 하는 광범위한 리뷰.
- 이유를 기록하지 않고 동작 변경에 TDD를 건너뜀.
- 검증되지 않은 주장으로 durable docs를 업데이트.
- 훅을 완전한 보안 통제로 취급.
- audit 훅을 실행하거나 결정을 기록하지 않고 의존성 추가.
- 브랜치별로 구별되는 리뷰 관심사 없이 branch/PR을 stacking.
- 코드나 git log에서 재구성 가능한 "memory candidate".
- 해결되지 않은 product/domain/architecture/dependency/setup/delete/history 결정을 worker에게
  위임.

## 도구 정책

- 의존성 설치는 기본적으로 사용자가 관리한다.
- 다음 전에는 먼저 묻는다: setup, 의존성 실행, 훅, 삭제, history rewrite, 광범위한 범위 확장,
  미해결 product/domain/architecture 결정.
- 반복 가능한 체크에는 TDD + 프로젝트 훅(lefthook)을 우선한다.
- 테스트와 훅이 잘 커버하지 못하는 동작에만 수동/브라우저 QA를 사용한다.
- 장기적인 프로젝트 결정은 채팅 기록이 아니라 프로젝트 문서에 남긴다.
