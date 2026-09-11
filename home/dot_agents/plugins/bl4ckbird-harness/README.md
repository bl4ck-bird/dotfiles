# bl4ckbird Harness

탐색·설계·명세·계획부터 구현·리뷰·완료까지 연결하는 개인 Codex 플러그인이다. 이 문서는 설치와 수동 유지보수의 시작점이며, 작업 단계별 규칙은 각 스킬을 기준으로 한다.

## Quick Start

Codex CLI, chezmoi, Python 3.9 이상이 필요하다. 기록 도구와 로컬 테스트는 Python 표준 라이브러리를 사용한다. 실제 모델 평가는 Codex 인증과 모델 호출이 추가로 필요하다.

chezmoi에 원본과 개인 마켓플레이스가 준비된 환경에서 실행한다.

```sh
chezmoi apply "$HOME/.agents/plugins"
codex plugin add bl4ckbird-harness@personal
codex plugin list
```

목록에서 `bl4ckbird-harness@personal`의 설치·활성 상태를 확인하고 새 Codex 작업을 시작한다. `bl4ckbird-harness로 현재 작업을 진행해줘`라고 요청하면 현재 근거에 맞는 단계에서 시작한다.

프로젝트에 지속 적용하려면 `이 프로젝트에 하네스를 활성화해줘`라고 명시한다. 자동 진입에는 유효한 `.harness/config.toml`이 필요하며, 플러그인 설치만으로 프로젝트가 활성화되지는 않는다. 활성화·수동 설정과 기록 제외 방법은 [진입 규칙](skills/using-harness/references/entry.md)을 따른다.

## Files and Ownership

| Purpose | Chezmoi Source | Applied Location |
| --- | --- | --- |
| 플러그인 | `home/dot_agents/plugins/bl4ckbird-harness/` | `~/.agents/plugins/bl4ckbird-harness/` |
| 마켓플레이스 | `home/dot_agents/plugins/marketplace.json` | `~/.agents/plugins/marketplace.json` |
| Codex 전역 지침 | `home/dot_codex/AGENTS.md` | `~/.codex/AGENTS.md` |

위 원본 경로는 chezmoi Git 저장소 기준이다. 실제 편집 경로는 `chezmoi source-path ~/.agents/plugins/bl4ckbird-harness`로 확인한다. 이 저장소는 개인 환경에서만 플러그인과 마켓플레이스를 적용한다.

Codex가 실행하는 설치본은 `~/.codex/plugins/cache/` 아래에 있다. 유지보수는 chezmoi 원본에서 하고, 캐시는 설치 명령으로 갱신한다. 홈의 적용본을 직접 수정했다면 해당 파일을 `chezmoi add`로 원본에 반영해야 다음 적용 때 유지된다.

| File or Directory | What to Edit |
| --- | --- |
| `dot_codex-plugin/plugin.json` | 이름·설명·버전·스킬 경로. 적용 후 이름은 `.codex-plugin/plugin.json` |
| `skills/<name>/SKILL.md` | 해당 단계의 진입 조건·절차·완료 조건 |
| `skills/<name>/references/` | 상세 계약·검토 기준·참조 문서 |
| `skills/<name>/assets/` | 작업 문서 템플릿 |
| `scripts/records.py`, `scripts/harness_records/` | 기록 명령과 형식·참조·상태 검증 |
| `scripts/validate_bundle.py` | 번들 구성·참조·런타임 모듈 검사 |
| `tests/records/`, `tests/bundle/` | 기록 도구·번들 검사의 회귀 테스트 |
| `evaluations/` | 실제 모델 평가와 평가 실행기 테스트 |

마켓플레이스의 `source.path`는 `./.agents/plugins/bl4ckbird-harness`다. 기준은 마켓플레이스 루트인 홈이며, `marketplace.json`이 놓인 디렉터리 기준이 아니다.

## Skills

| Skill | Responsibility |
| --- | --- |
| [using-harness](skills/using-harness/SKILL.md) | 프로젝트 진입·활성화·재개·단계 선택 |
| [harness-discover](skills/harness-discover/SKILL.md) | 문제·사용자·성공 기준·범위 탐색 |
| [harness-design](skills/harness-design/SKILL.md) | 시스템 책임·경계·공유 계약 설계 |
| [harness-roadmap](skills/harness-roadmap/SKILL.md) | 성과·우선순위·의존 관계 정리 |
| [harness-spec](skills/harness-spec/SKILL.md) | 가까운 작업의 동작·계약·수용 기준 구체화 |
| [harness-plan](skills/harness-plan/SKILL.md) | 슬라이스·태스크·검증·실행 권한 계획 |
| [harness-execute](skills/harness-execute/SKILL.md) | 배정·실행·검증·수정 진행 |
| [harness-review](skills/harness-review/SKILL.md) | 산출물의 독립 검토와 판정 |
| [harness-diagnose](skills/harness-diagnose/SKILL.md) | 원인 불명 결함·반복 수정 실패 조사 |
| [harness-finish](skills/harness-finish/SKILL.md) | 최종 수용·전달·정리 확인 |

## Edit and Update

1. chezmoi 원본에서 필요한 파일을 수정한다. 예를 들어 진입 스킬은 다음 명령으로 편집한다.

```sh
chezmoi edit "$HOME/.agents/plugins/bl4ckbird-harness/skills/using-harness/SKILL.md"
```

2. 차이를 확인해 홈에 적용하고 번들을 검사한다. chezmoi 원본의 `dot_codex-plugin`은 적용 전 이름이므로 번들 검사는 적용본에서 실행한다.

```sh
plugin_dir="$HOME/.agents/plugins/bl4ckbird-harness"
chezmoi diff "$plugin_dir"
chezmoi apply "$plugin_dir"
python3 -B "$plugin_dir/scripts/validate_bundle.py" "$plugin_dir"
```

3. 아래 검증 항목 중 변경에 영향받는 검사를 수행한다. 검사에 실패하면 수정 후 다시 확인하고 다음 설치 단계로 넘어간다.

4. 설치본도 갱신하려면 기본 제공 `plugin-creator` 도구로 버전 표식을 바꾼 뒤 재설치한다. 아래 명령은 앞 단계의 `plugin_dir`를 사용한다. 각 명령이 성공한 것을 확인하며 순서대로 실행한다.

```sh
plugin_tools="$HOME/.codex/skills/.system/plugin-creator/scripts"
python3 -B "$plugin_tools/read_marketplace_name.py"
python3 -B "$plugin_tools/update_plugin_cachebuster.py" "$plugin_dir"
chezmoi add "$plugin_dir/.codex-plugin/plugin.json"
codex plugin add bl4ckbird-harness@personal
codex plugin list
chezmoi diff "$plugin_dir"
```

마켓플레이스 조회 결과는 `personal`이어야 한다. 버전 도구는 기본 버전을 유지하고 `+codex.<timestamp>` 부분을 교체한다. 도구가 홈 매니페스트를 수정하므로 `chezmoi add`로 원본에도 반영한다. 스킬 내용 변경은 새 Codex 작업에서 확인한다.

5. chezmoi Git 저장소에서 변경 범위와 diff를 검토한 뒤 커밋·푸시한다. 로컬 적용과 Codex 재설치는 Git 전달을 대신하지 않는다.

## Validation

다음 명령은 적용된 플러그인 루트에서 실행한다. 로컬 테스트와 평가 목록 조회는 모델을 호출하지 않는다. README만 수정했다면 링크·명령·원본/적용본 일치를 확인하고, 코드 변경 시 해당 테스트를 실행한다.

```sh
cd "$HOME/.agents/plugins/bl4ckbird-harness"
python3 -B scripts/validate_bundle.py
python3 -B -m unittest discover -s tests/records -v
python3 -B -m unittest discover -s tests/bundle -v
PYTHONPATH="$PWD/evaluations" python3 -B -m unittest discover -s evaluations/tests -v
python3 -B evaluations/run.py --list
```

매니페스트나 스킬 메타데이터를 바꾸면 공식 검사기도 실행한다. 이 검사기는 PyYAML이 설치된 Python 환경이 필요하다.

```sh
python3 -B "$HOME/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py" \
  "$HOME/.agents/plugins/bl4ckbird-harness"
```

실제 모델을 사용하는 동작 평가는 [평가 안내](evaluations/README.md)의 명령·격리 조건·판정 한계를 따른다. 기록 명령의 정확한 입력은 [기록 도구 안내](skills/using-harness/references/record-tools.md)와 `python3 -B scripts/records.py --help`에서 확인한다.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| 수정한 스킬이 계속 이전 내용으로 보임 | chezmoi 적용 → 버전 표식 갱신과 원본 반영 → 재설치 → 새 Codex 작업 순서를 확인 |
| 플러그인을 찾지 못함 | 홈 마켓플레이스의 이름·`source.path`, 적용본의 `.codex-plugin/plugin.json`, `codex plugin list` 결과 확인 |
| chezmoi 원본에서 번들 검사가 실패함 | `dot_codex-plugin`이 `.codex-plugin`으로 적용된 홈 경로에서 검사 |
| 공식 검사에서 `No module named 'yaml'` 발생 | PyYAML이 준비된 Python 환경에서 같은 검사 실행 |
| chezmoi 명령에서 폰트·GitHub 조회 오류 발생 | 저장소의 외부 템플릿 평가에 필요한 네트워크 상태 확인 후 재실행 |
| 설치했지만 프로젝트가 자동 활성화되지 않음 | [진입 규칙](skills/using-harness/references/entry.md)의 프로젝트 설정 조건 확인 |

스킬 문서의 작성·분리 기준은 [작성 규칙](skills/using-harness/references/authoring.md)을 따른다. 이 README에는 유지보수 방법을 두고 단계별 실행 규칙은 해당 스킬에서 관리한다.
