# Test Pollution

다음일 때 로드:

- 테스트가 파일, 디렉터리, DB 행, 또는 외부 상태를 만들고 그것이 테스트 이후에도 남는다.
- 스위트가 소스 트리에 산출물을 남긴다(`.git`, `tmp/`, 유출된 픽스처).
- 테스트가 단독으로는 통과하지만 스위트에서는 실패한다(또는 그 반대).
- 한 테스트가 다음 테스트를 위한 환경을 오염시킨다.

증상이 다른 곳을 가리킨다면(결정적 로직 버그, 구현 누락) 이 파일 없이 메인
`bug-diagnosis`를 사용한다.

## What This File Owns

"어떤 테스트가 오염시키는가?"라는 조사 작업과 이분 탐색 도구. 재오염 방어는
`defense-in-depth.md`(Layer 3 환경 가드)에 있다.

## Symptoms

| Symptom | Likely cause |
| --- | --- |
| 테스트 후 `packages/<x>/`에 `.git`이 나타남 | 테스트가 비어있거나 잘못된 `cwd`로 `git init`을 실행함 |
| `tmp/`, `dist/`, 프로젝트 루트에 무작위 파일 | 테스트가 샌드박스 밖에 파일을 씀 |
| 스위트 후 예상치 못한 DB 행 | 테스트가 정리 없이 시딩함 |
| 단독으로는 통과, 스위트에서는 실패 | 이전 테스트가 공유 상태를 변경함 |
| 단독으로는 실패, 스위트에서는 통과 | 이전 테스트가 이 테스트가 기대하는 상태를 준비함(숨은 결합) |
| CI는 통과, 로컬은 실패(또는 반대) | 환경 특이적 누수 |

## Investigation Process

### 1. Identify The Pollution Signal

단일 셸 명령으로 확인 가능한, 구체적이고 관찰 가능한 산출물을 고른다:

- 파일 경로(`/tmp/leak.json`, `packages/core/.git`).
- DB 행(`SELECT * FROM sessions WHERE user_id = 'test-leak'`).
- 프로세스(`pgrep -f leaked-server`).
- 포트(`lsof -iTCP:8080`).

"테스트가 이상하다"는 신호가 아니다.

### 2. Confirm Deterministic Repro

```text
1. Clean the signal: rm -rf <path> / DROP TABLE / kill <pid>.
2. Run the suite.
3. Check the signal. Does it appear?
4. Repeat once more. Same result?
```

비결정적이라면 재현율을 먼저 끌어올린다(병렬 워커, 느린 네트워크, 더 작은 임시
디렉터리 — `bug-diagnosis` 재현 루프 기법).

### 3. Bisect To Find The Polluter

`find-polluter.sh`를 사용한다:

```bash
# Run from the project root. Default runner: npm test.
~/.config/ai-harness/skills/bug-diagnosis/find-polluter.sh '.git' 'src/**/*.test.ts'

# Other runners (TEST_CMD must accept a test file path as its argument):
TEST_CMD="pytest" ~/.config/ai-harness/skills/bug-diagnosis/find-polluter.sh '/tmp/leak.json' 'tests/**/test_*.py'
```

`go test`와 `cargo test`는 파일 경로가 아니라 패키지/테스트 타깃(`--test <name>`)을
대상으로 하므로 스크립트로 구동할 수 없다 — 수동으로 이분 탐색한다: 각 패키지/테스트
타깃을 개별 실행하며 실행 사이에 오염 신호를 확인한다.

각 테스트 파일을 개별 실행하고 실행 사이에 신호를 확인해 최초 오염원에서 멈춘다.

"오염원 없음"이라면:

- 오염이 **조합**(설정 훅 + 이후 테스트)에서 발생함. 전체 스위트를 실행하며 실행 도중
  신호를 관찰한다.
- 오염이 **공유 픽스처/전역 훅**(Vitest `setup.ts`, Jest `globalSetup`, Pytest
  `conftest.py`, Rust `mod tests { fn setup() }`)에서 발생함. 이것들을 먼저 감사한다.
- 러너 캐시가 오염원을 가림. 병렬성/캐싱을 한 번 비활성화한다:
  `npm test -- --no-cache --runInBand`, `pytest -p no:cacheprovider`,
  `cargo test -- --test-threads=1`.

### 4. Find The Root Cause

`root-cause-tracing.md`로 전환한다: 테스트 파일을 읽고, 오염 연산까지 콜 체인을
추적하고, 원래 트리거(빈 파라미터, 누락된 teardown 등)를 식별한다.

### 5. Fix At Root + Add Defense

1. 소스에서 수정한다(`root-cause-tracing.md` "Fix At Source").
2. `defense-in-depth.md`를 통해 검증 레이어를 추가해 다른 경로로도 버그가 재발할 수
   없게 한다.
3. 최신 출력으로 검증한다: `find-polluter.sh`를 재실행 → "오염원 없음(No polluter
   found)".

## Common Polluter Mechanisms

### Empty / Default cwd

```typescript
// ❌ Bug
await execFileAsync('git', ['init'], { cwd: projectDir });  // projectDir = ''
// Empty cwd → process.cwd() → source tree
```

수정: 공개 API 경계에서 `cwd`를 검증한다(Layer 1). 환경 가드: 테스트 중 `tmpdir` 밖에서의
`git init`을 거부한다(Layer 3).

### Fixture Accessed Before `beforeEach`

```typescript
// ❌ Bug
const ctx = setupTest();              // returns { tempDir: '' } before beforeEach
beforeEach(() => { ctx.tempDir = makeTempDir(); });

test('thing', () => {
  somethingThatNeeds(ctx.tempDir);    // first access uses '' → process.cwd()
});
```

수정: 픽스처를 초기화 전 접근 시 예외를 던지는 getter로 변환한다.

### Cleanup Only On Success

```typescript
// ❌ Bug
test('does thing', async () => {
  const session = await createSession();
  await doRiskyThing(session);  // throws → cleanup never runs
  await cleanupSession(session);
});
```

수정: 인라인이 아니라 `afterEach`/`try`-`finally`를 사용한다.

### External Process Spawned, Never Killed

```typescript
// ❌ Bug
const server = spawn('node', ['server.js']);
// ...test body...
// server still running after the test
```

수정: PID를 추적하고 `afterEach`에서 죽인다. Layer 3 가드: CI에서는 명시적 허용 목록
없이 테스트가 장시간 실행 프로세스를 스폰하는 것을 거부한다.

### DB Rows Seeded But Not Removed

수정: 트랜잭션 테스트(begin/rollback) 또는 픽스처 범위 정리. Layer 3 가드: 테스트
실행에서 비테스트 DB 연결을 거부한다.

## When Pollution Is Acceptable

일부 오염은 필요하다: `target/`/`dist/`의 빌드 산출물, 커버리지, 로그. 신호는
"*의도하지 않은* 상태가 유출됐는가?"다. 확인: `.gitignore`에 있는가? 예 → 문제없음.
아니오 → 유출됨.

## Hand-Off

find-polluter + root-cause-tracing + defense-in-depth 이후:

1. `find-polluter.sh`를 재실행하고 출력을 읽는다.
2. `bug-diagnosis` SKILL.md 9-10단계로 복귀한다(검증, 계측 정리, 버그가 프로젝트 전역
   규칙을 드러냈다면 durable docs 갱신).
