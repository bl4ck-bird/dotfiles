# 기록 도구

Python 3.9 이상 표준 라이브러리만 사용한다. 명령은 플러그인 루트에서 실행하거나 스크립트의 절대 경로를 사용한다.

## 명시적 프로젝트 적용

```sh
python3 scripts/harness.py init --root /path/to/project
```

사용자가 해당 프로젝트의 적용·활성화를 요청했을 때 실행한다. `.harness/config.json`, 시작용 CURRENT, 루트 `.gitignore`의 `/.harness/` 규칙을 준비한다. 기존 기록·다른 하네스 설정·추적 파일·비활성 설정을 자동 덮어쓰지 않는다. Git 초기화·설치·커밋을 수행하지 않는다. 이미 같은 설정으로 활성화된 프로젝트에는 안전하게 재실행할 수 있다.

## 구조 확인

```sh
python3 scripts/harness.py check --root /path/to/project
```

설정·제외·추적 여부와 내부 Markdown 링크를 확인한다. `changes/<변경명>/status.md`는 [상태 기준](state.md)의 적용 범위에 따라 필수 항목·작업 표·완료 모순·남은 실행과 차단 사항을 확인한다. 검사 대상의 완료되지 않은 변경은 CURRENT에서 해당 status로 직접 연결해야 한다. CURRENT에 연결되지 않은 이전 자유형식 상태는 미검사 개수를 알리며 자동 변환하지 않는다. status가 없는 단순 작업에는 새 상태 파일을 요구하지 않으며 과거 snapshots 안의 상태는 재검사하지 않는다.

Git 저장소에서는 실제 제외 결과도 확인하며, Git이 없거나 아직 저장소가 아니면 제외 규칙의 구조만 확인한다. 나중에 Git을 도입하면 다시 검사한다. 명령은 읽기 전용이며 상태를 수정하거나 작업을 재실행하지 않는다. 실제 테스트 수행·승인 의미·코드 최신성은 판정하지 않으므로 검사 통과를 작업 완료로 보고하지 않는다.

## 승인·리뷰 대상 보존

```sh
python3 scripts/harness.py snapshot --root /path/to/project --change folder-import --files changes/folder-import/spec.md changes/folder-import/plan.md
```

`--files`는 `.harness/` 기준의 기존 Markdown 파일이다. 활성 설정과 기록의 Git 제외 경계를 확인한 뒤 새 스냅샷 폴더에 상대 경로를 보존해 복사하고 해시를 기록한다. 보고된 경로를 승인·리뷰 보고에서 참조한다. 허용 범위를 벗어난 경로·심볼릭 링크는 거부한다. 스냅샷 생성은 승인이 아니며 사용자 발언과 검토 결과는 별도로 연결한다.

문서 참조 검사는 아래 인라인 링크를 대상으로 한다. CURRENT의 활성 status도 이 형식으로 연결한다. 참조형 링크는 지원하지 않으며 코드 블록 안의 예시 링크는 검사하지 않는다.

```markdown
[설명](상대/경로.md)
```
