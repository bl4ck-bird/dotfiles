---
name: retro-capture
description: Use when ship-check or any review reports memory candidates or retro insights that should persist beyond the current session. ship-check나 다른 리뷰가 현재 세션을 넘어 유지되어야 할 memory candidate나 retro insight를 보고할 때 사용한다.
---

# Retro Capture

완료된 slice, 리뷰, 또는 배포된 변경에서 나온 non-obvious한 학습 내용을 지속시켜 future agent
session과 프로젝트 작업이 이를 잃지 않도록 한다. 하네스의 "Retro" phase를 구현하며, Memory
Candidates 패턴과 host agent의 memory system을 연결한다.

## When To Trigger

다음일 때 실행한다:

- `ship-check`가 상당한 작업을 완료하고 retro line을 만들었을 때.
- 리뷰 스킬(`implementation-review`, `security-review`, `second-review`, `pressure-test`)이
  출력에서 "Memory candidates"를 보고했을 때.
- 버그 수정이나 사고가 future 작업이 따라야 할 규칙을 드러냈을 때.
- 사용자가 명시적으로 "remember this"를 요청할 때.

## Review Channel Utility Log

이번 cycle에서 실행된 각 리뷰 채널(`implementation-review`, `security-review`, `second-review`,
spec/plan Self-Review)에 대해 retro note에 세 가지 데이터를 기록한다:

- 발견사항의 severity 분포(Critical / Important / Minor 개수)
- **다른 어떤 채널도** 잡아내지 못한 발견사항을 만들었는지(unique yes/no)
- 발견사항이 실제로 fix를 유발했는지(fix yes/no)

목적: 향후 채널 add/remove/merge 결정을 직관이 아니라 이 데이터로 내린다.
`.ai-harness/reviews/YYYY-MM-DD-retro-<topic>.md`에 누적한다.

trivial한 세션, git history에서 보이는 code-only 패턴, 일회성 chat context에는 실행하지 않는다.

## Memory Type Classification

host agent의 memory model을 사용해 각 후보를 분류한다(Claude global memory는 아래 네 가지
type을 사용; 다른 host는 동등하게 매핑해야 함):

- **User**: 사용자의 role, expertise, preference에 대한 durable fact. 대부분 global.
- **Feedback**: 작업 방식에 대해 사용자가 준 규칙 또는 암묵적으로 수용한 규칙. 프로젝트를 넘어
  적용되면 global; 이 codebase에 특화되면 project-local.
- **Project**: 진행 중인 작업 context, deadline, ownership, in-flight 결정. 주로 project-local.
- **Reference**: 외부 시스템(issue tracker, dashboard, runbook)에 대한 포인터.

## Persistence Location

다음 규칙으로 global 대 project-local을 결정한다:

- **Global**(host agent의 memory 디렉터리, 예: `~/.claude/projects/<project-slug>/memory/`):
  - 프로젝트를 넘어 적용됨.
  - non-obvious함; 코드나 git history에서 재구성될 수 없음.
  - 어떤 코드도 읽기 전, future session 시작 시점에 유용함.
- **Project-local**(`.ai-harness/reviews/YYYY-MM-DD-retro-<topic>.md` 또는 `.ai-harness/adr/`):
  - 이 codebase, team, 또는 product context에 특화됨.
  - 긴 공백 이후 프로젝트를 재개할 때 유용함.
  - `.ai-harness/CURRENT.md`에서 참조될 수 있음.
- **둘 다 아님(skip)**:
  - 사실이 코드, git log, lockfile, 또는 눈에 보이는 아티팩트에 있음.
  - 교훈이 재발하기엔 너무 좁음.
  - 후보가 이미 알려진 하네스 규칙을 재진술함.

## Memory Entry Format

host agent의 memory format에 맞춘다. Claude global memory 예시(fact당 파일 1개, 그리고 memory
index `MEMORY.md`에 한 줄 포인터):

```markdown
---
name: <short-kebab-case-slug>
description: <one-line cue used to decide relevance later>
metadata:
  type: user | feedback | project | reference
---

<Rule or fact, one paragraph.>

**Why:** <reason; often a past incident or strong preference>
**How to apply:** <when/where the rule kicks in>
```

project-local 파일의 경우, 선택한 markdown 파일 안에 비슷한 header와 원본 리뷰/결정을 링크하는
짧은 context 섹션을 사용한다.

## Frequency

- 상당한 phase 경계마다 한 번 실행(ship-check, 주요 slice 종료, debugging session 종료). 작은
  step마다 캡처하지 않는다.
- `bounded-loop` 중에는 iteration budget 종료 시점 또는 성공적 종료 시점에만 캡처한다.

## Anti-Patterns

- 코드 패턴 저장("we use X library") — 코드가 source다.
- git activity 요약 저장 — `git log`가 authoritative하다.
- 일회성 버그의 fix recipe 저장 — commit message로 충분하다.
- `AGENTS.md`나 `CLAUDE.md`에 이미 있는 규칙 저장.
- 명확한 재사용 시나리오 없이 "혹시 몰라서" 저장하는 것.

## Output

보고:

- 받은 후보와 그 분류
- 저장된 entry(경로, type, 한 줄 요약)
- 건너뛴 후보와 이유
- memory가 프로젝트 문서화 gap을 드러냈다면 follow-up
