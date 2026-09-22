# bl4ck-harness

제품 탐색과 전체 설계에서 구현·검증·장기 작업 재개까지 연결하는 한글 개발 하네스다. Superpowers 6.3.0에서 출발해 6.4.1의 실패 입력 검토·인라인 리뷰 경계·최종 검사 기준을 반영하고, Matt Pocock의 도메인 모델링·모듈 설계·간결한 명세·수직 작업 분해를 선택적으로 반영했다. 이름만 바꾼 원본 배포판이 아니며 같은 평가 성능을 보장하지 않는다.

## 시작

이 폴더가 Codex 플러그인 소스다. `.codex-plugin/plugin.json`과 `skills/`를 포함한다. chezmoi로 소스·마켓플레이스·기본 AGENTS를 관리하고 Codex 플러그인 명령으로 설치한다. 설치된 환경에서는 `$using-bl4ck-harness`으로 시작하고 사용할 프로젝트를 명시한다. 예를 들어 `using-bl4ck-harness으로 이 프로젝트에 bl4ck-harness을 적용하고 새 제품의 방향부터 정리해줘`라고 요청한다.

스킬이 보이지 않는 상태에서는 설치된 것으로 간주하지 않는다. Codex의 현재 플러그인 설치 경로에서 이 소스를 등록한 뒤 새 세션의 스킬 목록을 확인한다. 자동 선택은 가능하지만 항상 로드되는 시작 훅은 이 패키지에서 제공하지 않는다. 새 세션·재개에서 진입점을 명시 호출한다. [실행 환경](skills/using-bl4ck-harness/references/platforms.md)을 참고한다.

chezmoi의 `home/dot_codex/AGENTS.md`는 하네스 독립 기본 지침이다. 전역 파일에 적용하려면 기존 내용을 검토한 후 별도로 교체한다. 이 패키지는 전역 파일을 변경하지 않는다.

## 설치와 원본 관리

| 대상 | chezmoi 원본 | 적용 위치 |
| --- | --- | --- |
| 플러그인 | `home/dot_config/agents/plugins/bl4ck-harness/` | `~/.config/agents/plugins/bl4ck-harness/` |
| 개인 마켓플레이스 | `home/dot_agents/plugins/marketplace.json` | `~/.agents/plugins/marketplace.json` |
| 기본 지침 | `home/dot_codex/AGENTS.md` | `~/.codex/AGENTS.md` |

개인 마켓플레이스의 로컬 원본은 홈 기준 `./.config/agents/plugins/bl4ck-harness`다. 원본에서 숨김 매니페스트 디렉터리는 chezmoi의 `dot_codex-plugin` 표기를 쓰며 적용 후 `.codex-plugin`이 된다. 개인 환경에만 적용한다. 캐시는 직접 수정하지 않는다. 이 소스 위치는 에이전트별 설치 캐시와 분리한다. 현재 설치 지원은 Codex이며, Claude 등 다른 에이전트는 해당 런타임의 매니페스트·스킬 로딩·도구 호환성을 검증한 뒤 연결한다.

```sh
chezmoi apply --parent-dirs --include=files,dirs ~/.agents/plugins/marketplace.json ~/.config/agents/plugins/bl4ck-harness ~/.codex/AGENTS.md
codex plugin add bl4ck-harness@personal
```

설치 후 새 Codex 작업에서 `$using-bl4ck-harness`를 호출한다. 소스 파일을 변경한 것만으로 설치 캐시는 갱신되지 않는다. 로컬 갱신 시 Codex 제공 캐시 갱신 도구로 매니페스트 버전을 갱신하고 chezmoi 원본에 반영한 뒤 다시 설치한다.

이전 하네스의 활성 프로젝트 기록은 자동 변환하지 않는다. 기존 설정·기록을 보존하고 실제 실행 상태와 승인 범위를 확인한 뒤 활성 변경만 새 상태에 이어받는다. 플러그인 설치는 모든 프로젝트의 지속 활성화나 기록 이관을 뜻하지 않는다.

## 흐름

제품 탐색 → 전체 설계 → 독립 검토·사용자 합의 → 로드맵 → 가까운 변경 명세 → 구현 계획 → 실행·검증 → 기준 문서 갱신과 전달.

신규 프로젝트에서는 사용자·전체 기능·도메인·공유 경계·기술 선택·폴더 책임을 먼저 정한다. 이미 명확한 기존 변경에는 필요한 단계만 적용한다. 중요한 미결정을 구현자가 발명해야 한다면 설계로 돌아간다. 모든 미래 기능의 상세 구현을 선결하지 않는다.

## 스킬

| 역할 | 스킬 |
| --- | --- |
| 진입·재개 | `using-bl4ck-harness` |
| 제품 탐색 | `bl4ck-harness-brainstorming` |
| 전체 설계 | `bl4ck-harness-design` |
| 설계 기법 | `bl4ck-harness-domain-modeling`, `bl4ck-harness-codebase-design` |
| 로드맵·명세·계획 | `bl4ck-harness-roadmap`, `bl4ck-harness-spec`, `bl4ck-harness-writing-plans` |
| 문서 독립 검토 | `bl4ck-harness-review` |
| 위임·인라인·병행 실행 | `bl4ck-harness-subagent-driven-development`, `bl4ck-harness-executing-plans`, `bl4ck-harness-dispatching-parallel-agents` |
| 테스트·진단 | `bl4ck-harness-test-driven-development`, `bl4ck-harness-systematic-debugging` |
| 코드 검토·수정 | `bl4ck-harness-requesting-code-review`, `bl4ck-harness-receiving-code-review` |
| 검증·격리·전달 | `bl4ck-harness-verification-before-completion`, `bl4ck-harness-using-git-worktrees`, `bl4ck-harness-finishing-a-development-branch` |
| 스킬 개선 | `bl4ck-harness-writing-skills` |

## 기록과 문서

에이전트 기록은 Git에서 제외한 `.harness/`에 둔다. `CURRENT.md`는 재개 위치, 단일 `ROADMAP.md`는 성과·순서, `product/`와 `design/`은 합의한 기준, `specs/`는 검증된 현재 계약, `changes/`는 이번 변경과 실행 근거다. 필요한 파일만 만든다. 완료한 근거를 자동 삭제하지 않는다.

자세한 책임·갱신 규칙은 [문서 기준](skills/using-bl4ck-harness/references/documents.md), [상태와 재개](skills/using-bl4ck-harness/references/state.md), [기록 도구](skills/using-bl4ck-harness/references/tools.md)에 있다. 스펙·플랜에는 완성 구현 코드를 요구하지 않으며 내부 작업 ID와 지시를 제품 결과물에 남기지 않는다.

## 검증

플러그인 루트에서 실행한다. 네트워크·패키지 설치·사용자 프로젝트 변경 없이 임시 폴더에서 검증한다.

```sh
python3 scripts/validate.py
python3 -m unittest discover -s tests -v
```

검사는 패키지 구조·참조와 기록 도구 동작을 확인한다. 프로젝트의 `harness.py check`는 Markdown 상태의 필수 항목·완료 모순·미확인 실행·참조도 확인한다. 별도 JSON 실행 상태나 호출 이력 파일은 만들지 않는다. 실제 모델의 모든 행동·호스트 설치·자동 로딩을 증명하지 않는다. [출처와 차이](UPSTREAM.md), [검증 범위](VALIDATION.md), [라이선스 안내](LICENSE.md)를 참고한다.
