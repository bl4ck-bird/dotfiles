# Root Cause Tracing

Bugs surface deep in the call stack — `git init` in the wrong directory, a file at the wrong
path, a query against the wrong DB. The instinct is to fix where the error appears. That is
treating a symptom.

**Core principle**: trace backward through the call chain to the original trigger, fix at the
source. Add validation at each layer afterward (`defense-in-depth.md`).

## When To Use

- Error happens deep in execution, not at an entry point.
- Stack trace shows a long call chain.
- Unclear where invalid data originated.
- Need to identify which test/code path triggers the problem.

## The Tracing Process

### 1. Observe the symptom

Concrete and specific. "`git init` failed in `~/project/packages/core`" — not "git broke".

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

What value was passed?

- `projectDir = ''` (empty string).
- Empty `cwd` resolves to `process.cwd()`.
- That is the source-code directory — there is the symptom.

### 5. Find the original trigger

```typescript
const context = setupCoreTest();              // returns { tempDir: '' }
Project.create('name', context.tempDir);      // accessed before beforeEach ran
```

Trigger: top-level variable initialization accessing pre-`beforeEach` state. Fix: make
`tempDir` a getter that throws if accessed before `beforeEach`.

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

- In tests, prefer `console.error` over project logger (loggers may be suppressed).
- Log *before* the dangerous op, not after it fails.
- Include directory, cwd, env vars, timestamps.
- `new Error().stack` captures the full chain.

```bash
npm test 2>&1 | grep 'DEBUG git init'
```

Analyze: file names in frames, line numbers triggering the call, the pattern (same test? same
parameter?).

Remove instrumentation when trace is complete (`bug-diagnosis` cleanup step).

## Finding Which Test Causes Pollution

If something appears during tests but you do not know which test, run a bisection harness:

- Run the suite in chunks; binary-search which chunk produces the side effect.
- Or run tests one at a time with the polluting condition as a stop signal.
- `vitest --bail=1` plus a pre-test check looking for the polluting state stops at first
  offender.

## Key Principle

```text
Found immediate cause
  → can trace one level up? → yes → trace backward
                            → no  → instrument with stack trace
  → is this the source?     → no  → keep tracing
                            → yes → fix at source
  → then add validation at each layer (defense-in-depth)
```

**Never fix only where the error appears.** Trace back to the original trigger.

## Common Failures

- **Fixing the symptom** because the trace seems hard. → Instrument, then trace.
- **Stopping at the first plausible cause** without verifying it is the trigger. → Ask what
  called *that*.
- **Trusting the logger** in tests. → Use `console.error`.
- **Logging after the failure** when state has already mutated. → Log before the dangerous op.

## Hand-Off

Root cause identified → return to `bug-diagnosis` SKILL step 7-8 (regression test before fix,
fix root cause). Apply `defense-in-depth.md` after the fix if the value flowed through
multiple layers.
