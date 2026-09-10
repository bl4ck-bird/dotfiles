# Harness Evaluations

작은 격리 프로젝트에서 실제 `codex exec`를 실행해 하네스 지침 적용 전후를 비교한다. Python 3.9 이상과 지원 옵션이 있는 Codex CLI가 필요하다. 추가 패키지는 설치하지 않는다.

## Commands

이 디렉터리에서 실행한다. 목록과 판정기 테스트는 모델을 호출하지 않는다.

```sh
python3 run.py --list
python3 -m unittest discover -s tests -v
```

실제 평가는 기존 Codex 인증을 사용한다. 모델·추론 수준·호출별 평가 제한 시간을 명시한다. 다음 모델은 초기 후보이며 실제 사용 가능 여부는 호출 결과로 확인한다.

```sh
python3 run.py --output /path/to/project/.harness/evaluations \
  --model gpt-5.6-terra --effort medium \
  --judge-model gpt-5.6-terra --judge-effort high \
  --timeout 180 --repeat 2 --mode paired
```

`--scenario mechanical-edit`처럼 하나만 선택할 수 있다. `paired`는 같은 요청·초기 파일·모델 설정으로 baseline과 하네스 적용을 비교하며 반복마다 새 작업 공간을 만든다. 호출별 제한 시간은 평가 실행 설정이며 하네스 자체의 기본 한도가 아니다.

## Scenarios

| Scenario | Observable Outcome |
| --- | --- |
| `mechanical-edit` | 정확한 오탈자 수정·무관한 변경 없음·불필요한 재질문 없음 |
| `unresolved-requirement` | 구체적 정책 질문·관련 구현 보류·요청 없는 프로젝트 활성화 없음 |
| `spec-review` | 읽기 전용 명세 검토·실제 요구 충돌 탐지·현재 시점 지침 적용 |
| `valid-review-finding` | 실제 요구와 명세의 모순을 근거 있는 finding으로 보고 |
| `false-positive-review` | 요구·코드·테스트의 반증으로 오탐 수정 제안을 거절 |
| `weak-test-review` | 타입 확인만 하는 테스트가 계약 동작을 입증하지 못함을 탐지 |
| `integration-omission-review` | 단위 통과와 실제 HTTP 사용자 흐름의 누락을 구분 |
| `internal-id-leakage` | 공개 README의 내부 ID·기록 경로 제거와 사용자 안내 보존 |
| `required-reviewer-unavailable` | 비적격 후보만 주어진 상태에서 필수 review gate와 근거 공백 유지 |
| `uncertain-prior-execution` | unknown/running 관측에서 충돌 작업 보류·종료 근거 요구·시도 회계 보존 |

## Evidence and Verdicts

- `configuration.json`, 소스 manifest: 요청 모델/추론 수준·설정·대상 버전·비교 한계.
- 실행별 `before.json`, `after.json`, `agent/`: 실제 파일 내용·원시 JSONL·응답·명령 종료 상태.
- 실행별 `judge/`: 독립 판정 요청·관찰·실행·근거가 연결된 결과. 평가 대상 자기 보고가 판정을 대신하지 않는다.
- `summary.json`, `summary.md`: 개별 `satisfied` / `failed` / `unverified`와 모델이 인용해 열거한 `annotated_question_count`. 이 수는 실제 모든 질문의 탐지를 보장하지 않으며, 개별 실행·judge 결과·파생 질문 check에도 같은 한계가 남는다. 중요한 실패를 평균 점수로 숨기지 않는다.

종료 코드는 전체 충족 `0`, 실패 포함 `1`, 미검증 `2`다. 파일 범위/내용의 결정적 실패를 모델 판정이 뒤집을 수 없다. 호출 원시 이벤트는 검증 근거로 보존하며 사용량·비용은 별도로 수집·집계하지 않는다.

## Isolation and Limits

평가 대상의 쓰기 범위는 새 작업 공간이며 기대값·원본·판정 자료는 밖에 둔다. 실행 전 실제 샌드박스 탐침으로 쓰기 경계를 확인하고 실패하면 모델을 호출하지 않는다. 판정 에이전트는 읽기 전용이며 평가 코드나 대상이 제시한 명령을 호스트 판정 프로세스에서 실행하지 않는다.

사용자 설정·execpolicy·프로젝트 지침의 자동 로딩은 지원 CLI 옵션으로 제외한다. 인증 값은 복사하거나 출력하지 않는다. 기본 모델·공통 도구·전역 스킬 카탈로그 등의 환경 영향까지 완전히 제거했다는 주장은 하지 않는다.

CLI 종료와 모든 별도 프로세스의 종료는 다르다. 시간 초과·미완료 사건·남은 실행은 미검증으로 보존한다. 불확실한 공간은 재사용·자동 정리하지 않는다. 관측 파일 크기 제한에 걸리면 결과를 잘라 통과시키지 않는다.

이 실행기는 파일로 전달한 실제 스킬 지침을 평가한다. 설치 탐색·서브에이전트 실행 루프·세션 간 복구는 별도 검증 대상이다. 공용 기록 도구가 필요한 기능을 가짜 상태로 우회하지 않는다. 의미 판정에는 모델 판단의 한계가 있어 개별 원시 근거를 함께 확인해야 한다. 특히 `annotated_question_count=0`은 실제 질문이 없다는 증명이 아니라 판정 모델이 질문을 인용해 열거하지 않았다는 뜻이다.

`required-reviewer-unavailable`와 `uncertain-prior-execution`의 JSON은 synthetic observation이다. 이 두 사례의 통과는 주어진 사실에서의 판단을 뜻하며 실제 reviewer 가용성·host 조회·이전 세션 종료 또는 재개를 증명하지 않는다. 그 결과는 `result.json`의 `synthetic_observation=true`와 suite configuration의 한계에도 남는다.

`--global-instructions <path>`는 선택 사항이다. 지정하면 일반 파일만 suite의 `harness-source/`에 동결해 harness 모드의 명시 지침으로만 전달한다. baseline에는 전달하지 않아 기본 비교 격리를 유지한다. 이 옵션은 설치된 전역 지침의 자동 탐색을 평가하지 않는다.

## References

- [Non-interactive mode](https://learn.chatgpt.com/docs/non-interactive-mode)
- [Configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference)
