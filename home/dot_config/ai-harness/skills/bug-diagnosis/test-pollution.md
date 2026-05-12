# Test Pollution

Load this reference when:

- A test creates files, directories, database rows, or external state that survives
  beyond the test.
- The test suite leaves artifacts in the source tree (`.git`, `tmp/`, leaked
  fixtures).
- Tests pass in isolation but fail when run as a suite (or vice versa).
- You suspect one test corrupts the environment for the next.

If symptoms point elsewhere (deterministic logic bug, missing implementation), use
the main `bug-diagnosis` workflow without this file.

## What This File Owns

The "which test is polluting?" investigation pattern, plus the bisection tool that
finds the polluter automatically.

Defense against re-pollution after the fix lives in `defense-in-depth.md` (Layer 3
environment guards).

## Symptoms

| Symptom | Likely cause |
| --- | --- |
| `.git` appears in `packages/<x>/` after running tests | Test ran `git init` with empty / wrong `cwd` |
| Random files in `tmp/`, `dist/`, project root | Test wrote outside its sandbox |
| Database has unexpected rows after suite | Test seeded data without cleanup |
| Test passes alone, fails in suite | Earlier test changed shared state |
| Test fails alone, passes in suite | Earlier test set up the state this test expects (hidden coupling) |
| CI passes, local fails (or vice versa) | Environment-specific leak |

## The Investigation Process

### 1. Identify The Pollution Signal

Pick a specific, observable artifact:

- A file path (`/tmp/leak.json`, `packages/core/.git`).
- A database row (`SELECT * FROM sessions WHERE user_id = 'test-leak'`).
- A process (`pgrep -f leaked-server`).
- A network port (`lsof -iTCP:8080`).

The signal must be checkable with a single shell command. "The tests are weird" is
not a signal.

### 2. Confirm The Repro Is Deterministic

```text
1. Clean the signal: rm -rf <path> / DROP TABLE / kill <pid>.
2. Run the suite.
3. Check the signal. Does it appear?
4. Repeat 1-3 once more. Same result?

If the signal appears in step 3 but not always, raise the repro rate first:
parallel test workers, slow network, smaller temp directory — the techniques in
bug-diagnosis SKILL.md reproduction-loop step apply.
```

### 3. Bisect To Find The Polluter

Use `find-polluter.sh` in this directory:

```bash
# Default (npm test):
./find-polluter.sh '.git' 'src/**/*.test.ts'

# Other runners:
TEST_CMD="pytest"           ./find-polluter.sh '/tmp/leak.json' 'tests/**/test_*.py'
TEST_CMD="cargo test --"    ./find-polluter.sh 'target/leak'    'tests/*.rs'
TEST_CMD="go test"          ./find-polluter.sh 'tmp/leak'       './...'
```

The script runs each test file individually, checking the signal between runs. It
stops at the first test that creates the signal.

If the script returns "no polluter found":

- The pollution is created by **the combination** of tests (e.g., setup hook + a
  later test). Run the full suite and watch the signal mid-run.
- The pollution is created by a **shared fixture or global hook** (Vitest `setup.ts`,
  Jest `globalSetup`, Pytest `conftest.py`, Rust `mod tests { fn setup() }`). Audit
  those before suspecting individual tests.
- Test runner caches mask the polluter. Disable parallelism / caching once:
  `npm test -- --no-cache --runInBand`, `pytest -p no:cacheprovider`,
  `cargo test -- --test-threads=1`.

### 4. Find The Root Cause

Once `find-polluter.sh` names the test, switch to `root-cause-tracing.md`:

1. Read the test file.
2. Trace the call chain from the test through to the polluting operation.
3. Identify the original trigger (empty parameter, missing teardown, etc.).

### 5. Fix At The Root + Add Defense

After identifying the root cause:

1. Fix at the source (see `root-cause-tracing.md` step "Fix At Source").
2. Add validation layers via `defense-in-depth.md` so the same bug cannot reappear
   through a different code path.
3. Apply `verification-before-completion`: re-run `find-polluter.sh`. The script must
   return "No polluter found".

## Common Polluter Mechanisms

### Empty / Default cwd

```typescript
// ❌ Bug
await execFileAsync('git', ['init'], { cwd: projectDir });  // projectDir = ''
// Empty cwd → process.cwd() → source tree
```

Fix: validate `cwd` at the public API boundary (`defense-in-depth.md` Layer 1).
Environment guard: refuse `git init` outside `tmpdir` during tests
(`defense-in-depth.md` Layer 3).

### Test accessed shared fixture before `beforeEach` / `beforeAll` ran

```typescript
// ❌ Bug
const ctx = setupTest();              // returns { tempDir: '' } before beforeEach
beforeEach(() => { ctx.tempDir = makeTempDir(); });

test('thing', () => {
  somethingThatNeeds(ctx.tempDir);    // first access uses '' → process.cwd()
});
```

Fix: convert the fixture to a getter that throws if accessed before initialization.

### Cleanup runs only on success

```typescript
// ❌ Bug
test('does thing', async () => {
  const session = await createSession();
  await doRiskyThing(session);  // throws → cleanup never runs
  await cleanupSession(session);
});
```

Fix: `afterEach` / `try`-`finally` for cleanup, not inline.

### External process spawned in test, never killed

```typescript
// ❌ Bug
const server = spawn('node', ['server.js']);
// ...test body...
// server still running after the test
```

Fix: track the PID, kill in `afterEach`. Layer 3 guard: in CI, refuse to spawn long-
running processes from tests without an explicit allowlist.

### Database rows seeded but not removed

Fix: transactional tests (begin / rollback), or fixture-scoped cleanup. Layer 3
guard: refuse non-test database connections from test runs.

## When Pollution Is Acceptable

Some pollution is *load-bearing*: build artifacts in `target/` or `dist/`, coverage
reports, log files. The signal is "did *unintended* state leak?" If `.git` showing
up in `packages/core/` is fine for your project, ignore it; if it is not, fix it.

The check for "unintended": is this in `.gitignore`? If yes, fine. If no, the
pollution probably leaked.

## Hand-Off

After find-polluter + root-cause-tracing + defense-in-depth:

1. Apply `verification-before-completion` — re-run `find-polluter.sh`.
2. Return to `bug-diagnosis` SKILL.md workflow step 9-10 (verify, clean up temporary
   instrumentation, update durable docs if the bug exposed a project-wide rule).
