# Lefthook / Pre-Commit Hook Recipes

로드 시점:

- 프로젝트가 `lefthook`(또는 다른 git-hook 러너)을 사용하는 경우, **또는**
- 사용자가 dependency-audit/lint/typecheck 자동화를 위해 하나를 도입할지 고려 중인 경우.

그 외에는 건너뛴다.

## Principle

**자동화는 hook으로 트리거하고, 판단은 스킬에 있다.**

- Hook은 올바른 git 이벤트에서 언어 감사, lint, typecheck, focused test, secret scan을
  **트리거**한다.
- 스킬의 **판단**(대안, 라이선스, 제거 비용, 아키텍처 영향)은 `write-plan` Self-Review와
  `security-review`에 남는다.

`npm audit`을 실행해 커밋을 실패시키는 hook은 트리거다. "이 취약점을 수용할지, 의존성을 교체할지,
문서화된 위험을 안고 진행할지"는 `write-plan` / `security-review`의 결정이다.

## Propose, Do Not Install

`project-scaffold`와 스킬 agent들은 hook 설정을 **제안**한다. 명시적 사용자 승인 없이 러너를
설치하거나 실행하지 않는다. 사용자가 소유하는 것:

- 러너 선택(`lefthook`, `husky`, `pre-commit`, `simple-git-hooks`).
- 설치(`brew install lefthook`, `npm install lefthook`).
- 설정 커밋.

Agent는 요청 시 설정 파일을 작성할 수 있지만 installer를 호출해서는 안 된다.

## Dependency Audit Hooks

staged commit에서 manifest 파일이 변경될 때 트리거한다. 언어에 맞는 감사를 실행하고, 프로젝트가
거부하는 발견사항에서 실패시킨다.

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

커밋이 manifest를 건드릴 때, 메시지 본문에 의존성 근거를 명시하도록 요구한다.

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

이 스크립트는 **트리거**다: 사람이 근거를 작성하도록 강제한다. 내용(대안, 라이선스, 제거 비용,
적합성)은 plan이나 decision record에 속한다.

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
| `gitleaks` | `brew install gitleaks` + config | 빠르고 성숙하지만 튜닝 없이는 오탐(FP)이 잦음 |
| `trufflehog` | Container or binary | 더 많은 시그널, 더 느림 |
| Plain regex grep | None | 취약하지만 최소한의 "no AWS keys" 보호에는 충분 |

### Pre-push full suite

suite가 ~30초를 넘을 때 적합한 단계다. pre-commit은 빠르게 유지해야 하며(staged-file 체크 기준
10초 미만) 개발자가 `--no-verify`로 우회하지 않도록 한다.

## What Lefthook Cannot Enforce

다음은 hook이 아니라 스킬에 속한다:

- 아키텍처(DDD / SOLID / file-size)와 acceptance compliance — `implementation-review`.
- 감사 출력 이상의 보안 판단 — `security-review`.
- 독립적인 double-check — `second-review`.
- Plan/spec 위생 — `write-plan` / `write-spec` Self-Review.

`npm audit`을 실행하는 hook은 프로젝트가 `moderate` 취약점을 수용하는지 알지 못한다. 그것은 plan에
기록되는 `security-review` 결정이다.

## Avoid

- 명시적 opt-in 없이 파일을 변형하는 hook(auto-format, auto-fix lint). 예상치 못한 변형은 merge
  conflict를 일으키고 "내가 stage한 것 = 내가 commit한 것" 원칙을 깬다.
- fresh-verification 시맨틱을 우회하는 hook — "tests pass"라고 주장하는 hook은 명령을 실행하고
  출력을 읽어야 한다.
- 더 빨리 끝내려고 `--no-verify`로 hook을 건너뛰는 것. 근본 원인을 고치거나 블로커를 보고한다.

## Implementation File

Hook 세부사항은 이 컴패니언 문서가 아니라 `lefthook.yml`(또는 프로젝트 동등물)에 속한다. 이 파일은
*무엇을·왜*의 카탈로그이며; *어떻게*는 프로젝트의 hook 설정에 있다.
