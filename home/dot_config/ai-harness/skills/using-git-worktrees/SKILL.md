---
name: using-git-worktrees
description: Use when starting a vertical slice that needs isolation from the current workspace, before executing a multi-task plan, or when the host environment has not already provided an isolated workspace. 현재 workspace로부터 격리가 필요한 vertical slice를 시작할 때, multi-task plan 실행 전, 또는 host 환경이 격리된 workspace를 아직 제공하지 않았을 때 사용한다.
---

# Using Git Worktrees

**Intent**: 구현은 격리된, clean-baseline workspace에서 이루어진다. **Boundary**: 하네스와 절대
싸우지 않는다 — 먼저 기존 격리를 탐지하고, host-native 도구를 우선하며, 아무것도 없을 때만
`git worktree`로 폴백한다; cleanup은 생성자만 수행한다. **Verify**: 새 workspace에서 baseline
check를 실행하고 최신 출력을 읽는다.

Worktree 생성, 탐지, cleanup의 하네스 전역 SSOT — `subagent-driven-development`와 `ship-check`가
이 파일을 참조한다.

## When

- 보호된 base branch에서 시작하는 모든 코드 변경 작업(규칙 SSOT: `using-bb-harness` Branch
  Policy — 모든 Workflow Path에 적용).
- multi-task plan(`subagent-driven-development` / `executing-plans-inline`), 광범위한 refactor,
  또는 사용자가 branch/PR로 리뷰 가능하길 원하는 모든 slice 이전.

건너뛰는 경우: Step 0에서 기존 격리를 탐지 · 이미 일치하는 non-protected feature branch에 있음 ·
사용자가 이번 세션에서 보호된 branch 작업에 명시적으로 동의(기록할 것) · 작업이 read-only.

## Step 0 — Detect Existing Isolation

```bash
GIT_DIR=$(cd "$(git rev-parse --git-dir)" 2>/dev/null && pwd -P)
GIT_COMMON=$(cd "$(git rev-parse --git-common-dir)" 2>/dev/null && pwd -P)
# Submodule guard — a submodule also has GIT_DIR != GIT_COMMON:
git rev-parse --show-superproject-working-tree 2>/dev/null   # path → submodule → normal repo
```

`GIT_DIR != GIT_COMMON`이고 submodule이 아니면 → 이미 linked worktree 안에 있음: 경로와 branch를
보고하고(detached HEAD → "branch creation deferred to `ship-check` Finishing Options"로 명시)
Step 2로 건너뛴다. 그 외: 격리 없음 → 선언된 preference가 없다면 생성 전에 동의를 구한다; 사용자가
거절하면 → 그 자리에서 작업, Step 2.

## Step 1 — Create

**1a. Host-native tool 우선**(Claude Code `EnterWorktree`, `/worktree`, Codex helper, project
script) — placement, branch 생성, registration, cleanup을 이 도구가 소유한다. native tool이 있는데
raw `git worktree add`를 쓰면 phantom state가 생기고 `ship-check` cleanup provenance가 깨진다.

**1b. Git fallback**(1a가 적용되지 않을 때만):

- Directory: `AGENTS.md`/`CLAUDE.md`/`.ai-harness/AGENT_WORKFLOW.md`/chat에 선언된 preference가
  우선; 없으면 기존 `.worktrees/`(선호) 또는 `worktrees/`; 없으면 project root의 기본값
  `.worktrees/`. global worktree 경로 없음 — project-local이어야 project tooling이 찾을 수 있다.
- Safety: 디렉터리가 git-ignore 되어 있는지 확인(`git check-ignore -q .worktrees`); ignore되지
  않았으면 → `.gitignore`에 추가, stage, 작은 커밋에 대한 승인을 요청(승인된 plan이 이를 커버하지
  않는 한).
- Create: `git worktree add "$LOCATION/$BRANCH_NAME" -b "$BRANCH_NAME" && cd`로 진입. Permission
  error(sandbox) → 보고하고 그 자리에서 작업.

## Step 2 — Project Setup (user-managed)

manifest를 탐지하고 install 명령을 *제안*한다(`npm install`, `cargo build`, `uv sync`,
`go mod download`); 사용자가 이번 세션의 setup을 승인했을 때만 실행한다.

## Step 3 — Verify Clean Baseline

가장 좁은 의미 있는 suite/typecheck/lint를 실행하고 이 응답 안에서 출력을 읽는다. 실패 →
pre-existing인지 regression인지 구분하고, 진행 전에 물어본다 — red baseline에서 조용히 시작하지
않는다.

```text
Worktree ready at <full-path>
Branch: <name>
Baseline: <N> tests, <M> failures (pre-existing / new / clean)
Ready to: <next skill or action>
```

## Cleanup (executed at `ship-check` Finishing Options)

- Provenance: 이 스킬이 생성한 경로(`.worktrees/`, `worktrees/`)만 제거할 수 있다; host가 소유한
  worktree는 host의 lifecycle을 따른다.
- 항상 먼저 main repo root로 `cd`한다 — worktree 안에서 `git worktree remove`를 실행하면 조용히
  실패한다:

```bash
MAIN_ROOT=$(git -C "$(git rev-parse --git-common-dir)/.." rev-parse --show-toplevel)
cd "$MAIN_ROOT" && git worktree remove "$WORKTREE_PATH" && git worktree prune
```

- Merge order: merge 성공 → worktree 제거 → branch 삭제(worktree가 참조하는 동안은
  `git branch -d`가 거부한다).

## Never

탐지된 격리 위에 worktree를 생성 · native tool을 우회해 raw git 사용 · git-ignore 체크 건너뛰기 ·
baseline verification을 건너뛰거나 무시 · 이 스킬이 생성하지 않은 worktree를 제거 · worktree
안에서 `git worktree remove` 실행.
