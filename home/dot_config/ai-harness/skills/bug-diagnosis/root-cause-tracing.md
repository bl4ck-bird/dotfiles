# Root Cause Tracing

버그는 콜스택 깊숙한 곳에서 드러난다 — 잘못된 디렉터리에서의 `git init`, 잘못된 경로의
파일, 잘못된 DB를 대상으로 한 쿼리. 본능적으로는 에러가 나타난 곳을 고치려 한다. 그것은
증상을 치료하는 것이다.

**Core principle**: 콜 체인을 역방향으로 추적해 원래 트리거까지 올라가고, 소스에서
고친다. 그 후 각 레이어에 검증을 추가한다(`defense-in-depth.md`).

## When To Use

- 에러가 진입점이 아니라 실행 깊숙한 곳에서 발생한다.
- 스택 트레이스가 긴 콜 체인을 보여준다.
- 잘못된 데이터가 어디서 시작됐는지 불분명하다.
- 어떤 테스트/코드 경로가 문제를 유발하는지 식별해야 한다.

## The Tracing Process

### 1. Observe the symptom

구체적이고 명확하게. "`~/project/packages/core`에서 `git init`이 실패했다" — "git이
망가졌다"가 아니라.

### 2. Find the immediate cause

```typescript
await execFileAsync('git', ['init'], { cwd: projectDir });
```

### 3. Ask: what called this?

```text
WorktreeManager.createSessionWorktree(projectDir, sessionId)
  → Session.initializeWorkspace()
  → Session.create()
  → test at Project.create()
```

### 4. Keep tracing up

어떤 값이 전달됐는가?

- `projectDir = ''`(빈 문자열).
- 빈 `cwd`는 `process.cwd()`로 해석된다.
- 그것이 바로 소스 코드 디렉터리다 — 증상이 여기 있다.

### 5. Find the original trigger

```typescript
const context = setupCoreTest();              // returns { tempDir: '' }
Project.create('name', context.tempDir);      // accessed before beforeEach ran
```

트리거: 최상위 변수 초기화가 `beforeEach` 이전 상태에 접근함. 수정: `tempDir`을
`beforeEach` 이전에 접근되면 예외를 던지는 getter로 만든다.

## Adding Stack Traces When Manual Trace Fails

```typescript
async function gitInit(directory: string) {
  console.error('DEBUG git init:', {
    directory,
    cwd: process.cwd(),
    nodeEnv: process.env.NODE_ENV,
    stack: new Error().stack,
  });
  await execFileAsync('git', ['init'], { cwd: directory });
}
```

- 테스트에서는 프로젝트 로거보다 `console.error`를 우선한다(로거는 억제될 수 있음).
- 위험한 연산이 실패한 *후*가 아니라 *직전*에 로깅한다.
- 디렉터리, cwd, 환경 변수, 타임스탬프를 포함한다.
- `new Error().stack`은 전체 체인을 캡처한다.

```bash
npm test 2>&1 | grep 'DEBUG git init'
```

분석: 프레임 안의 파일명, 호출을 유발한 줄 번호, 패턴(같은 테스트인가? 같은
파라미터인가?).

추적이 끝나면 계측을 제거한다(`bug-diagnosis` 정리 단계).

## Finding Which Test Causes Pollution

테스트 도중 무언가가 나타나는데 어떤 테스트인지 모른다면 이분(bisection) 하네스를
실행한다:

- 스위트를 청크 단위로 실행하고, 어느 청크가 부작용을 일으키는지 이진 탐색한다.
- 또는 오염 조건을 정지 신호로 삼아 테스트를 하나씩 실행한다.
- `vitest --bail=1`과 오염 상태를 찾는 사전 테스트 점검을 결합하면 최초 유발자에서
  멈춘다.

## Key Principle

```text
즉시 원인을 찾음
  → 한 단계 위로 추적 가능한가? → 예 → 역방향으로 추적
                              → 아니오 → 스택 트레이스로 계측
  → 이것이 소스인가?           → 아니오 → 계속 추적
                              → 예 → 소스에서 수정
  → 그 후 각 레이어에 검증 추가(defense-in-depth)
```

**에러가 나타난 곳만 고치지 않는다.** 원래 트리거까지 역추적한다.

## Common Failures

- **증상만 고치기** — 추적이 어려워 보인다는 이유로. → 계측 후 추적한다.
- **처음 그럴듯한 원인에서 멈추기** — 그것이 트리거인지 검증하지 않고. → *그것*을 무엇이
  호출했는지 묻는다.
- 테스트에서 **로거를 신뢰하기**. → `console.error`를 사용한다.
- 상태가 이미 변이된 뒤 **실패 후 로깅하기**. → 위험한 연산 전에 로깅한다.

## Hand-Off

근본 원인 식별 → `bug-diagnosis` SKILL 7-8단계로 복귀(수정 전 회귀 테스트, 근본 원인
수정). 값이 여러 레이어를 거쳤다면 수정 후 `defense-in-depth.md`를 적용한다.
