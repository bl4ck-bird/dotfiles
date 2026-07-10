---
name: project-scaffold
description: Use when starting a new project or adding/refining AGENTS.md, CLAUDE.md, docs, hooks, skills, or reviewer agents in an existing repo. 새 프로젝트를 시작하거나 기존 저장소에서 AGENTS.md/CLAUDE.md/문서/hook/스킬/reviewer agent를 추가·정비할 때 사용한다.
---

# Project Scaffold

**Intent**: Claude Code, Codex, 그 외 agent들이 하나의 scaffold set으로부터 동일한 durable project
context를 공유한다. **Boundary**: 기존 파일을 보존한다(사용자가 요청한 것만 갱신); repo를 바꾸는
모든 액션은 decision gate를 통과한다; 초기 세트를 넘어서는 문서는 그것을 생성하는 스킬이 만들며,
사전에 scaffold되지 않는다; 의존성 설치는 사용자가 관리한다. **Verify**: 최종 보고서는 생성된
파일, 건너뛴 기존 파일, 승인된 결정 사항, 권장 다음 단계를 나열한다.

## Scaffold Set

하나의 세트, profile 없음:

```text
AGENTS.md                        # project root, gitignored
CLAUDE.md                        # project root, gitignored — @AGENTS.md + Claude-only wiring
GEMINI.md                        # project root, gitignored — symlink to AGENTS.md (ln -s AGENTS.md GEMINI.md)
.gitignore                       # merge agent-file entries (see Gitignore Policy)
.ai-harness/CONTEXT.md
.ai-harness/CURRENT.md
.ai-harness/AGENT_WORKFLOW.md    # generic workflow content lives here, not in host files (D5)
.ai-harness/adr/0000-template.md # MADR format
.ai-harness/specs/  plans/  reviews/   # empty dirs (mkdir)
```

그 외 모든 것은 소유 스킬이 실행될 때 나타난다 — 부재는 정상이다:

| Doc | Created by |
| --- | --- |
| `.ai-harness/adr/NNNN-<title>.md` | `write-spec` / `write-plan` output contract; `ship-check` safety net |
| `.ai-harness/ROADMAP.md` | `product-discovery`; `ship-check`에서 확인 |
| `.ai-harness/DOMAIN_MODEL.md`, `CONTEXT-MAP.md` | `domain-modeling` |
| `ARCHITECTURE.md`, `DATA_MODEL.md`, `SECURITY_MODEL.md`, `TESTING_STRATEGY.md` | 해당 관심사를 결정하는 스킬 |

템플릿: `~/.config/ai-harness/templates/project/`. 템플릿 디렉터리는 `.ai-harness/`를 숨긴다 —
`cp -r project/* dest`는 이를 건너뛴다; 파일 목록대로 복사하거나 `cp -R project/. dest`를
사용한다. 빈 디렉터리는 `mkdir`; `GEMINI.md`는 복사본이 아니라 symlink로 생성한다.

## Host File Structure (D5)

Generic workflow content(스킬 흐름, severity/result 어휘, second-review 기준)는 오직
`.ai-harness/AGENT_WORKFLOW.md`에만 존재한다. `CLAUDE.md` = `@AGENTS.md` + Claude 전용 배선
(reviewer subagent 단락). `GEMINI.md` = `AGENTS.md`로의 symlink(Gemini 전용 배선은 존재하지 않음;
링크는 drift될 수 없음) — host가 symlink를 따라갈 수 없는 경우 pointer file로 대체.

## Gitignore Policy

Agent 대상 파일은 로컬 컨텍스트이며 절대 커밋하지 않는다. `.gitignore`에 병합(덮어쓰지 않음):

```gitignore
# AI harness — local agent context, not committed
.ai-harness/
AGENTS.md
CLAUDE.md
GEMINI.md
```

`AGENTS.md`/`CLAUDE.md`/`GEMINI.md`는 repo root에 유지되지만(도구가 요구함) ignore된다.
`.ai-harness/`는 하네스가 생성하는 모든 문서를 담는다. `docs/`는 ignore하지 **않는다** — 이는
커밋되는 사람 대상 문서이며, 하네스가 그 안에 생성하는 일은 없다.

## Human Decision Gate

새 프로젝트 — 다음 각각에 대해 명시적 승인: `git init` · scaffold 파일 · `.claude/` / `.codex/` /
`.agents/` · `lefthook.yml` · 패키지/부트스트랩 실행(명시적으로 요청된 경우만) · 최초 커밋. 기존
프로젝트 — 기존 파일 수정, hook 추가, agent 설정 또는 의존성 manifest 변경, install 실행, history
변경 전에 확인. 부분 승인 → 승인된 부분만 수행하고, 나머지는 건너뛰었다고 보고.

## Human-Facing vs Agent-Internal Separation

사람이 보는 표면은 하네스 어휘를 절대 유출해서는 안 된다. 커밋되는 파일(`README.md`, root
`ROADMAP.md`, `LICENSE`, `docs/`) **그리고 커밋 메시지, 코드 주석, PR body** — `.ai-harness/`를
벗어나는 모든 것에 적용된다:

- slice/task ID(`S0`, `M1`, `I1`…), 리뷰 라벨(AFK/HITL, Risk High/Medium), severity 용어 없음.
- `.ai-harness/` 경로, 스킬명, "BB Harness" 언급 없음(`ship-check`가 commit gate에서 강제).
- 마일스톤은 사용자에게 보이는 능력으로, 커밋은 변경 내용으로 기술 — 하네스 단계나 slice 순서로
  기술하지 않는다.

Agent-internal 아티팩트(`.ai-harness/` 아래)는 하네스 어휘를 자유롭게 사용한다. Human-facing 파일
작성 = internal 문서로부터 *번역*하는 것이며, slice 표나 라벨을 경계 너머로 그대로 복사하지 않는다.

## Roadmap: Two Homes

`.ai-harness/ROADMAP.md` — internal slice SSOT(gitignored; `product-discovery`가 생성). Root
`ROADMAP.md` — 선택적으로 커밋되는 사람 대상 마일스톤 뷰: 능력 체크리스트, MVP / later /
non-goals, internal ID 없음; internal SSOT로부터 능력 단위로 재생성하며 slice 단위로는 하지 않는다.
README는 인라인 대신 이 파일로 링크한다.

## Defaults

- `README.md`: what/why, tech stack, getting started; roadmap은 인라인 대신 링크.
- 프로젝트 지침은 매 세션 읽을 수 있을 만큼 구체적이고 짧게; 프로젝트가 더 엄격한 버전을 필요로
  하지 않는 한 global rule을 복사하지 않는다.
- Scaffold된 문서는 `stub`로 시작 — 첫 본문 줄 `Document status: <stub|draft|ready>.`가 하네스
  전역 상태 메커니즘(`docs-sync`가 승격). stub 안의 TODO 주장은 프로젝트 사실이 아니다.
- 의존성 설치는 사용자 관리: 실행하는 대신 제안 명령과 가정을 기록한다.

## Hooks

프로젝트가 git-hook 러너를 사용(또는 고려)한다 → `lefthook-recipes.md`를 로드(언어별
dependency-audit hook, commit-msg 근거, lint/typecheck/secret-scan 대상). 원칙: **hook은 자동화를
트리거하고, 판단은 스킬에 있다** — hook은 의존성 추가에 대한 `write-plan` Self-Review나 고위험
의존성에 대한 `security-review`를 대체하지 않는다.

## Existing Project Defaults

로컬 컨벤션을 덮어쓰지 않는다; manifest/Makefile/CI/README에서 명령을 읽는다; 문서가 없을 때만
코드에서 도메인 용어를 추론하고 확인 전까지 uncertain으로 표시한다; 광범위한 재작성보다 제안형
추가를 선호한다.

## After Scaffolding

제안: goal/MVP/non-goals와 첫 vertical slice를 위한 `product-discovery`; 가정이나 용어가 불명확할
때 `pressure-test` / `domain-modeling`; 그다음 `write-spec` → `write-plan` →
`subagent-driven-development`(슬라이스별 `implementation-review`, 트리거 시
`security-review`/`second-review`) → `docs-sync` → `ship-check`.
