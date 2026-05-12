# Lefthook / Pre-Commit Hook Recipes

Load this reference when:

- The project uses `lefthook` (or another git-hook runner), **or**
- The user is considering adopting one for dependency-audit / lint / typecheck
  automation.

If the project does not use a hook runner and is not adopting one, skip this file.

## Principle

The harness rule is **trigger automation by hook; judgment lives in skills.**

- Hook **triggers** language audits, lint, typecheck, focused tests, secret scans on
  the right git event.
- Skill **judgment** (alternatives, license, removal cost, architecture impact)
  remains in `write-plan` Self-Review (for dependency adds) and `security-review`
  (for high-risk deps).

A hook that runs `npm audit` and fails the commit is a trigger. The decision "do we
accept the vulnerability, replace the dependency, or proceed with documented risk" is
a `write-plan` / `security-review` decision.

## Propose, Do Not Install

`project-scaffold` and skill agents may **propose** hook configuration. They do not
install or execute hook runners without explicit user approval. The user owns:

- Choosing the hook runner (`lefthook`, `husky`, `pre-commit`, `simple-git-hooks`).
- Installing it (`brew install lefthook`, `npm install lefthook`, etc.).
- Committing the configuration file.

Agents may write the configuration file if the user asks, but should not invoke the
installer.

## Dependency Audit Hooks

Trigger when manifest files change in staged commits. Run language-appropriate audit
tools and fail the commit on findings the project rejects.

| Manifest changed | Recommended audit command |
| --- | --- |
| `package.json`, `package-lock.json`, `pnpm-lock.yaml`, `yarn.lock` | `npm audit --omit=dev` / `pnpm audit --prod` / `yarn npm audit --severity high` |
| `requirements.txt`, `pyproject.toml`, `poetry.lock`, `uv.lock` | `pip-audit` / `safety check` |
| `Cargo.toml`, `Cargo.lock` | `cargo audit` |
| `go.mod`, `go.sum` | `govulncheck ./...` |
| `Gemfile`, `Gemfile.lock` | `bundler-audit` |

### Example: lefthook configuration for npm projects

```yaml
# lefthook.yml
pre-commit:
  parallel: true
  commands:
    audit:
      glob: "{package.json,package-lock.json,pnpm-lock.yaml,yarn.lock}"
      run: npm audit --omit=dev --audit-level=high
    lint:
      glob: "*.{ts,tsx,js,jsx}"
      run: npx eslint {staged_files}
    typecheck:
      run: npx tsc --noEmit
    secret-scan:
      run: gitleaks protect --staged --no-banner
```

### Commit-msg rationale enforcement

When a commit touches a manifest file, require the message body to mention dependency
rationale (added / replaced / upgraded reason, alternatives considered when relevant).
Lefthook can enforce this with a small commit-msg script.

```yaml
commit-msg:
  commands:
    dep-rationale:
      run: |
        if git diff --cached --name-only | grep -qE '(package.json|requirements.txt|Cargo.toml|go.mod|Gemfile)$'; then
          grep -qE '(added|replaced|upgraded|removed) (dep|dependency)' "{1}" || {
            echo "Dependency change requires rationale in commit body."
            echo "Mention: added/replaced/upgraded <dep> for <reason>."
            exit 1
          }
        fi
```

The script's contract is a **trigger**: it forces the human to write the rationale.
The rationale's **content** (alternatives evaluated, license compatibility, removal
cost, project fit) belongs in the plan or a decision record.

## Other Hook Targets

| Stage | Recommended targets |
| --- | --- |
| Pre-commit | Lint, typecheck, focused / fast tests, secret scan (gitleaks, ggshield, trufflehog), formatter |
| Commit-msg | Conventional commit format (when the project uses it), dependency rationale |
| Pre-push | Full test suite (when fast enough), build verification, license check |
| Post-merge | Re-run dependency audit on merged manifest changes |

### Pre-commit secret scan

Three options. Pick one based on tolerance for setup:

| Tool | Setup | Trade-off |
| --- | --- | --- |
| `gitleaks` | `brew install gitleaks` + config file | Fast, mature, false-positive prone without tuning |
| `trufflehog` | Container or binary | More signals, slower |
| Plain regex grep | None | Brittle, fine for "no AWS keys" minimal protection |

### Pre-push full suite

Pre-push is the right stage for the full test suite when it takes more than ~30
seconds. Pre-commit should stay fast (< 10 seconds for staged-file-only checks) so
developers do not bypass it with `--no-verify`.

## What Lefthook Cannot Enforce

These belong in skills, not hooks:

- Architecture decisions (DDD / SOLID / file-size) — `code-quality-review`.
- Acceptance compliance — `spec-compliance-review`.
- Security judgment beyond audit output — `security-review`.
- Independent double-check — `second-review`.
- Plan / spec hygiene — `write-plan` / `write-spec` Self-Review.

A hook that runs `npm audit` does not know whether the project accepts a `moderate`
vulnerability. That judgment is a `security-review` decision recorded in the plan.

## Avoid

- Hooks that mutate files (auto-format, auto-fix lint) without explicit user opt-in.
  Surprise mutations cause merge conflicts and break "what I staged is what I
  committed".
- Hooks that bypass `verification-before-completion` semantics — a hook claiming
  "tests pass" must run the test command and read the output, same as any skill.
- Skipping hooks with `--no-verify` to finish faster. The harness rule is to fix the
  underlying issue or report the blocker, not to bypass the gate.

## Implementation File

Hook implementation specifics belong in `lefthook.yml` (or the project's
equivalent), not in this companion. This file is the catalog of *what* to hook and
*why*. The *how* lives in the project's hook config.
