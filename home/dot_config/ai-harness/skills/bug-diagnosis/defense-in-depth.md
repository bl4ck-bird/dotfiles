# Defense-In-Depth Validation

잘못된 데이터로 인한 버그 이후, 한 곳에서만 검증하는 것으로 충분하다고 느끼기 쉽다.
단일 체크는 다른 코드 경로, 리팩터링, 목(mock)에 의해 쉽게 우회된다.

**Core principle**: 데이터가 통과하는 모든 레이어에서 검증한다. 버그를 단순히 "고친" 게
아니라 구조적으로 불가능하게 만든다.

## Why Multiple Layers

- 단일 검증: "버그 수정됨".
- 다중 레이어: "버그 불가능".

각 레이어는 서로 다른 케이스를 잡아낸다. 각각은 저렴하고, 조합하면 견고하다.

## The Four Layers

### Layer 1 — Entry Point Validation

공개 API 경계에서 명백히 잘못된 입력을 거부한다.

```typescript
function createProject(name: string, workingDirectory: string) {
  if (!workingDirectory || workingDirectory.trim() === '') {
    throw new Error('workingDirectory cannot be empty');
  }
  if (!existsSync(workingDirectory)) {
    throw new Error(`workingDirectory does not exist: ${workingDirectory}`);
  }
  if (!statSync(workingDirectory).isDirectory()) {
    throw new Error(`workingDirectory is not a directory: ${workingDirectory}`);
  }
}
```

### Layer 2 — Business Logic Validation

데이터가 *이* 연산에 대해 말이 되는지 확인한다. Layer 1을 우회하는 목과 지름길 호출자를
잡아낸다.

```typescript
function initializeWorkspace(projectDir: string, sessionId: string) {
  if (!projectDir) throw new Error('projectDir required for workspace initialization');
}
```

### Layer 3 — Environment Guards

특정 컨텍스트(테스트, 샌드박스, 프로덕션)에서 위험한 연산을 막는다.

```typescript
async function gitInit(directory: string) {
  if (process.env.NODE_ENV === 'test') {
    const normalized = normalize(resolve(directory));
    const tmpDir = normalize(resolve(tmpdir()));
    if (!normalized.startsWith(tmpDir)) {
      throw new Error(`Refusing git init outside temp dir during tests: ${directory}`);
    }
  }
}
```

### Layer 4 — Debug Instrumentation

다른 레이어가 실패하거나 낯선 조건에서 컨텍스트를 캡처한다.

```typescript
async function gitInit(directory: string) {
  logger.debug('About to git init', { directory, cwd: process.cwd(), stack: new Error().stack });
}
```

비용이 작고 포렌식 가치가 실재할 때만 Layer 4를 유지한다. 그렇지 않으면 수정이 검증된
후 제거한다.

## Applying The Pattern

1. **데이터 흐름을 추적한다**(`root-cause-tracing.md`). 잘못된 값은 어디서 시작되는가?
   어느 레이어들을 통과하는가?
2. **모든 체크포인트를 매핑한다** — 값을 검증할 수 있는 모든 지점.
3. **각 레이어에 검증을 추가한다** — entry → business → environment → debug.
4. **각 레이어를 테스트한다** — Layer 1을 우회해 Layer 2가 잡는지 검증하고, Layer 2를
   우회해 Layer 3이 잡는지 검증한다.

## Example

버그: 빈 `projectDir`이 `process.cwd()`(소스 트리)에서 `git init`을 유발함.

데이터 흐름:

1. 테스트 설정 → 빈 문자열.
2. `Project.create(name, '')`.
3. `WorkspaceManager.createWorkspace('')`.
4. `git init`이 `process.cwd()`에서 실행됨.

추가된 네 레이어:

- Layer 1: `Project.create()`가 비어있지 않음, 존재함, 쓰기 가능함을 검증.
- Layer 2: `WorkspaceManager`가 `projectDir`이 비어있지 않음을 검증.
- Layer 3: `WorktreeManager`가 테스트 중 `tmpdir` 밖에서의 `git init`을 거부.
- Layer 4: `git init` 전 스택 트레이스 로깅.

결과: 스위트의 모든 테스트가 통과했고, 버그가 구조적으로 불가능해졌다.

## Key Insight

네 레이어 모두 필요했다 — 각각이 다른 레이어가 놓친 케이스를 잡았다:

- 서로 다른 코드 경로가 진입점 검증을 우회했다.
- 목이 비즈니스 로직 체크를 우회했다.
- 크로스플랫폼 엣지 케이스가 환경 가드를 필요로 했다.
- 디버그 로깅이 구조적 오용을 식별했다.

**한 검증 지점에서 멈추지 않는다.**

## Anti-Patterns

- **단일 레이어 "수정"**을 throw 지점에만. → 데이터 흐름을 추적하고 Layer 1도 추가한다.
- 호출자가 건너뛸 수 있는 **테스트되지 않은 헬퍼의 검증**. → 공개 경계로 옮긴다.
- **로깅만 하는 "수정"**. → 포렌식일 뿐 교정이 아니다. throw하는 레이어를 최소 하나
  짝짓는다.
- **전역 상태에 의존하는 검증**(뒤집힐 수 있는 플래그). → 레이어별로 하드 체크한다.
- Layer 1-3이 이미 막고 있는데 **Layer 4가 프로덕션에 남음**. → 제거한다; 영원히 리뷰
  주의를 소모한다.

## Hand-Off

네 레이어가 모두 갖춰지고 알려진 어떤 진입점으로도 버그를 재현할 수 없으면,
`bug-diagnosis` SKILL 9-10단계로 복귀한다(검증, 계측 정리, 버그가 규칙을 드러냈다면
durable docs 갱신).
