# Test Pollution

Load when:

- A test creates files, directories, DB rows, or external state that survives the test.
- Suite leaves artifacts in the source tree (`.git`, `tmp/`, leaked fixtures).
- Tests pass in isolation but fail in suite (or vice versa).
- One test corrupts the environment for the next.

If symptoms point elsewhere (deterministic logic bug, missing impl), use main `bug-diagnosis`
without this file.

## What This File Owns

The "which test is polluting?" investigation + the bisection tool. Defense against
re-pollution lives in `defense-in-depth.md` (Layer 3 environment guards).

## Symptoms

| Symptom | Likely cause |
| --- | --- |
| `.git` appears in `packages/<x>/` after tests | Test ran `git init` with empty/wrong `cwd` |
| Random files in `tmp/`, `dist/`, project root | Test wrote outside its sandbox |
| Unexpected DB rows after suite | Test seeded without cleanup |
| Passes alone, fails in suite | Earlier test changed shared state |
| Fails alone, passes in suite | Earlier test sets up state this test expects (hidden coupling) |
| CI passes, local fails (or vice versa) | Environment-specific leak |

## Investigation Process

### 1. Identify The Pollution Signal

Pick a specific, observable artifact checkable with a single shell command:

- File path (`/tmp/leak.json`, `packages/core/.git`).
- DB row (`SELECT * FROM sessions WHERE user_id = 'test-leak'`).
- Process (`pgrep -f leaked-server`).
- Port (`lsof -iTCP:8080`).

"The tests are weird" is not a signal.

### 2. Confirm Deterministic Repro

```text
1. Clean the signal: rm -rf <path> / DROP TABLE / kill <pid>.
2. Run the suite.
3. Check the signal. Does it appear?
4. Repeat once more. Same result?
```

If non-deterministic, raise the repro rate first (parallel workers, slow network, smaller
temp dir — `bug-diagnosis` reproduction-loop techniques).

### 3. Bisect To Find The Polluter

Use `find-polluter.sh`:

```bash
# Default (npm test):
./find-polluter.sh '.git' 'src/**/*.test.ts'

# Other runners:
TEST_CMD="pytest"           ./find-polluter.sh '/tmp/leak.json' 'tests/**/test_*.py'
TEST_CMD="cargo test --"    ./find-polluter.sh 'target/leak'    'tests/*.rs'
TEST_CMD="go test"          ./find-polluter.sh 'tmp/leak'       './...'
```

Runs each test file individually, checks the signal between runs, stops at the first
polluter.

If "no polluter found":

- Pollution is from a **combination** (setup hook + later test). Run full suite, watch signal
  mid-run.
- Pollution is from a **shared fixture / global hook** (Vitest `setup.ts`, Jest `globalSetup`,
  Pytest `conftest.py`, Rust `mod tests { fn setup() }`). Audit those first.
- Runner caches mask the polluter. Disable parallelism/caching once:
  `npm test -- --no-cache --runInBand`, `pytest -p no:cacheprovider`,
  `cargo test -- --test-threads=1`.

### 4. Find The Root Cause

Switch to `root-cause-tracing.md`: read the test file, trace the call chain to the polluting
operation, identify the original trigger (empty parameter, missing teardown, etc.).

### 5. Fix At Root + Add Defense

1. Fix at source (`root-cause-tracing.md` "Fix At Source").
2. Add validation layers via `defense-in-depth.md` so the bug cannot reappear via another
   path.
3. Apply `verification-before-completion`: re-run `find-polluter.sh` → "No polluter found".

## Common Polluter Mechanisms

### Empty / Default cwd

```typescript
// ❌ Bug — empty cwd → process.cwd() → source tree
await execFileAsync('git', ['init'], { cwd: projectDir });  // projectDir = ''
```

Fix: validate `cwd` at the public API boundary (Layer 1). Environment guard: refuse `git
init` outside `tmpdir` during tests (Layer 3).

### Fixture Accessed Before `beforeEach`

```typescript
// ❌ Bug
const ctx = setupTest();              // returns { tempDir: '' }
beforeEach(() => { ctx.tempDir = makeTempDir(); });
test('thing', () => { somethingThatNeeds(ctx.tempDir); });  // first access uses ''
```

Fix: convert fixture to a getter that throws if accessed before initialization.

### Cleanup Only On Success

```typescript
// ❌ Bug — throw bypasses cleanup
test('does thing', async () => {
  const session = await createSession();
  await doRiskyThing(session);
  await cleanupSession(session);
});
```

Fix: `afterEach` / `try`-`finally`, not inline.

### External Process Spawned, Never Killed

```typescript
// ❌ Bug — server still running after test
const server = spawn('node', ['server.js']);
```

Fix: track PID, kill in `afterEach`. Layer 3 guard: in CI, refuse to spawn long-running
processes from tests without explicit allowlist.

### DB Rows Seeded But Not Removed

Fix: transactional tests (begin/rollback) or fixture-scoped cleanup. Layer 3 guard: refuse
non-test DB connections from test runs.

## When Pollution Is Acceptable

Some pollution is load-bearing: build artifacts in `target/`/`dist/`, coverage, logs. Signal
is "did *unintended* state leak?" Check: is it in `.gitignore`? Yes → fine. No → leaked.

## Hand-Off

After find-polluter + root-cause-tracing + defense-in-depth:

1. Apply `verification-before-completion` — re-run `find-polluter.sh`.
2. Return to `bug-diagnosis` SKILL.md step 9-10 (verify, clean instrumentation, update
   durable docs if the bug exposed a project-wide rule).
