# Root Cause Tracing

Bugs often surface deep in the call stack — `git init` in the wrong directory, a file
written to the wrong path, a query opened against the wrong database. The instinct is to
fix where the error appears. That is treating a symptom.

**Core principle**: trace backward through the call chain until you find the original
trigger, then fix at the source. Add validation at each layer afterward (see
`defense-in-depth.md`).

## When To Use

- The error happens deep in execution, not at an entry point.
- The stack trace shows a long call chain.
- It is unclear where the invalid data originated.
- You need to identify which test or code path triggers the problem.

## The Tracing Process

### 1. Observe the symptom

Concrete and specific. "`git init` failed in `~/project/packages/core`" — not "git
broke".

### 2. Find the immediate cause

What code directly produces this?

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

- `projectDir = ''` (empty string)
- Empty string as `cwd` resolves to `process.cwd()`
- That is the source-code directory — there is the symptom.

### 5. Find the original trigger

Where did the empty string come from?

```typescript
const context = setupCoreTest();              // returns { tempDir: '' }
Project.create('name', context.tempDir);      // accessed before beforeEach ran
```

The trigger is "top-level variable initialization accessing pre-`beforeEach` state".
The fix is to make `tempDir` a getter that throws if accessed before `beforeEach`.

## Adding Stack Traces When Manual Trace Fails

When you cannot reason backward from code alone, instrument:

```typescript
async function gitInit(directory: string) {
  const stack = new Error().stack;
  console.error('DEBUG git init:', {
    directory,
    cwd: process.cwd(),
    nodeEnv: process.env.NODE_ENV,
    stack,
  });
  await execFileAsync('git', ['init'], { cwd: directory });
}
```

Notes:

- In test runs, prefer `console.error` over the project logger — loggers may be
  suppressed.
- Log *before* the dangerous operation, not after it fails.
- Include directory, cwd, env vars, timestamps.
- `new Error().stack` captures the complete call chain.

Run and capture:

```bash
npm test 2>&1 | grep 'DEBUG git init'
```

Analyze:

- File names in the stack frames.
- Line numbers triggering the call.
- The pattern (same test? same parameter?).

Remove the instrumentation when the trace is complete (`bug-diagnosis` cleanup step).

## Finding Which Test Causes Pollution

If something appears during tests but you do not know which test, run a bisection
harness:

- Run the suite in chunks; binary-search which chunk produces the side effect.
- Or run tests one at a time with the polluting condition as a stop signal.
- Tools like `vitest --bail=1` plus a pre-test check that looks for the polluting state
  can stop at the first offender.

## Key Principle

```text
Found immediate cause
  → can trace one level up? → yes → trace backward
                            → no  → instrument with stack trace
  → is this the source?    → no  → keep tracing
                            → yes → fix at source
  → then add validation at each layer (defense-in-depth)
```

**Never fix only where the error appears.** Trace back to the original trigger.

## Common Failures

- **Fixing the symptom** because the trace seems hard. → Instrument, then trace.
- **Stopping at the first plausible cause** without verifying it is the trigger. → Ask
  what called *that*.
- **Trusting the logger** in tests. → Use `console.error`.
- **Logging after the failure** when the state has already mutated. → Log before the
  dangerous operation.

## Hand-Off

When the root cause is identified, return to `bug-diagnosis` SKILL workflow step 7-8
(regression test before fix, fix the root cause). Apply `defense-in-depth.md` after the
fix if the value flowed through multiple layers.
