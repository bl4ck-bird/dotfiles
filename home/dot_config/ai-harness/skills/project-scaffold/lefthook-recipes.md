# Lefthook / Pre-Commit Hook Recipes

Load when:

- Project uses `lefthook` (or another git-hook runner), **or**
- User is considering adopting one for dependency-audit/lint/typecheck automation.

Otherwise skip.

## Principle

**Trigger automation by hook; judgment lives in skills.**

- Hook **triggers** language audits, lint, typecheck, focused tests, secret scans on the
  right git event.
- Skill **judgment** (alternatives, license, removal cost, architecture impact) stays in
  `write-plan` Self-Review and `security-review`.

A hook running `npm audit` and failing the commit is a trigger. "Do we accept the vuln,
replace the dep, or proceed with documented risk?" is a `write-plan` / `security-review`
decision.

## Propose, Do Not Install

`project-scaffold` and skill agents **propose** hook config. They do not install or execute
runners without explicit user approval. User owns:

- Choosing the runner (`lefthook`, `husky`, `pre-commit`, `simple-git-hooks`).
- Installing it (`brew install lefthook`, `npm install lefthook`).
- Committing the config.

Agents may write the config file on request but should not invoke the installer.

## Dependency Audit Hooks

Trigger when manifest files change in staged commits. Run language-appropriate audit; fail on
findings the project rejects.

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

When a commit touches a manifest, require the message body to mention dependency rationale.

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

The script is a **trigger**: forces the human to write rationale. Content (alternatives,
license, removal cost, fit) belongs in plan or decision record.

## Other Hook Targets

| Stage | Recommended targets |
| --- | --- |
| Pre-commit | Lint, typecheck, focused/fast tests, secret scan (gitleaks, ggshield, trufflehog), formatter |
| Commit-msg | Conventional commit format, dependency rationale |
| Pre-push | Full test suite (if fast enough), build verification, license check |
| Post-merge | Re-run dependency audit on merged manifest changes |

### Pre-commit secret scan

| Tool | Setup | Trade-off |
| --- | --- | --- |
| `gitleaks` | `brew install gitleaks` + config | Fast, mature, FP-prone without tuning |
| `trufflehog` | Container or binary | More signals, slower |
| Plain regex grep | None | Brittle, fine for minimal "no AWS keys" protection |

### Pre-push full suite

Right stage when the suite > ~30 s. Pre-commit should stay fast (< 10 s for staged-file
checks) so devs do not bypass with `--no-verify`.

## What Lefthook Cannot Enforce

These belong in skills, not hooks:

- Architecture (DDD / SOLID / file-size) — `code-quality-review`.
- Acceptance compliance — `spec-compliance-review`.
- Security judgment beyond audit output — `security-review`.
- Independent double-check — `second-review`.
- Plan/spec hygiene — `write-plan` / `write-spec` Self-Review.

A hook running `npm audit` does not know if the project accepts a `moderate` vuln. That is a
`security-review` decision recorded in the plan.

## Avoid

- Hooks mutating files (auto-format, auto-fix lint) without explicit opt-in. Surprise
  mutations cause merge conflicts and break "what I staged is what I committed".
- Hooks that bypass `verification-before-completion` semantics — a hook claiming "tests pass"
  must run the command and read output.
- Skipping hooks with `--no-verify` to finish faster. Fix the underlying issue or report the
  blocker.

## Implementation File

Hook specifics belong in `lefthook.yml` (or project equivalent), not in this companion. This
file is the catalog of *what* and *why*; *how* lives in the project's hook config.
