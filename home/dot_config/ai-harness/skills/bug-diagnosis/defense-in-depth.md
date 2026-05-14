# Defense-In-Depth Validation

After a bug caused by invalid data, validating at one place feels sufficient. A single check
is easily bypassed by different code paths, refactoring, or mocks.

**Core principle**: validate at every layer the data passes through. Make the bug
structurally impossible, not just "fixed".

## Why Multiple Layers

- Single validation: "bug fixed".
- Multiple layers: "bug impossible".

Each layer catches different cases. Each is cheap; the combination is robust.

## The Four Layers

### Layer 1 — Entry Point Validation

Reject obviously invalid input at the public API boundary.

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

Ensure data makes sense for *this* operation. Catches mocks and shortcut callers that bypass
Layer 1.

```typescript
function initializeWorkspace(projectDir: string, sessionId: string) {
  if (!projectDir) throw new Error('projectDir required for workspace initialization');
}
```

### Layer 3 — Environment Guards

Prevent dangerous operations in specific contexts (tests, sandbox, production).

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

Capture context when other layers fail or in unfamiliar conditions.

```typescript
async function gitInit(directory: string) {
  logger.debug('About to git init', { directory, cwd: process.cwd(), stack: new Error().stack });
}
```

Keep Layer 4 only when cost is small and forensic value is real. Otherwise remove after fix
is verified.

## Applying The Pattern

1. **Trace the data flow** (`root-cause-tracing.md`). Where does the bad value originate?
   Which layers does it pass through?
2. **Map all checkpoints** — every point where the value could be validated.
3. **Add validation at each layer** — entry → business → environment → debug.
4. **Test each layer** — bypass Layer 1, verify Layer 2 catches; bypass Layer 2, verify
   Layer 3 catches.

## Example

Bug: empty `projectDir` caused `git init` in `process.cwd()` (source tree).

Data flow:

1. Test setup → empty string.
2. `Project.create(name, '')`.
3. `WorkspaceManager.createWorkspace('')`.
4. `git init` ran in `process.cwd()`.

Four layers added:

- Layer 1: `Project.create()` validates non-empty, exists, writable.
- Layer 2: `WorkspaceManager` validates `projectDir` non-empty.
- Layer 3: `WorktreeManager` refuses `git init` outside `tmpdir` during tests.
- Layer 4: stack-trace logging before `git init`.

Result: all suite tests passed; bug became structurally impossible.

## Key Insight

All four layers were necessary — each caught a case the others missed:

- Different code paths bypassed entry validation.
- Mocks bypassed business-logic checks.
- Cross-platform edge cases needed environment guards.
- Debug logging identified structural misuse.

**Do not stop at one validation point.**

## Anti-Patterns

- **Single-layer "fix"** at the throw site. → Trace data flow; add Layer 1 too.
- **Validation in untested helper** callers can skip. → Move onto the public boundary.
- **Logging-only "fix"**. → Forensic, not corrective. Pair with at least one throwing layer.
- **Validation depends on global state** (flag that can flip). → Hard checks at the layer.
- **Layer 4 left in production** when Layer 1-3 already block. → Remove it; costs review
  attention forever.

## Hand-Off

When all four layers are in place and the bug cannot be reproduced from any known entry
point, return to `bug-diagnosis` SKILL step 9-10 (verify, clean instrumentation, update
durable docs if the bug exposed a rule).
