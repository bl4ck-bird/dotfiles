---
name: security-review
description: Use when reviewing auth, permissions, secrets, crypto, deletion, destructive operations, sensitive data, external integrations, or data-loss risk.
---

# Security Review

Review security-sensitive work with evidence from code, config, docs, and verification. Do not rely
on intent alone.

## Triggers

Use this skill when work touches:

- authentication, authorization, sessions, tokens, or credentials
- secrets, `.env`, private keys, logging, or telemetry
- crypto, hashing, signing, or key management
- deletion, destructive commands, backups, restore, import, export, or data retention
- external integrations, webhooks, sync, concurrency, permissions, or sensitive data exposure
- untrusted input, validation, injection, path traversal, command construction,
  parser/deserialization, SSRF, open redirects, or file uploads
- new or replaced dependencies in auth/payment/crypto/network-protocol/native-code paths (audit
  output, supply-chain reputation, post-install scripts)

## Checks

- Trust boundaries and validation points are explicit.
- Sensitive data is not printed, logged, committed, or exposed in errors.
- Authorization checks happen at the correct boundary.
- Destructive operations require explicit user or product-level approval.
- Crypto and secret handling follow project docs or primary-source guidance.
- Tests or manual checks cover denial, invalid input, and failure behavior when practical.
- `docs/SECURITY_MODEL.md` is updated when durable security behavior changes.

## Output

Lead with findings, ordered by severity.

### Severity

- **Critical (Must Fix)**: exploitable vulnerability, secret leakage, auth bypass, data
  loss risk, destructive operation without approval, crypto / key handling defect.
- **Important (Should Fix)**: weak validation, missing authorization at the right
  boundary, sensitive data in logs / errors / telemetry, missing denial / failure test for
  a security-relevant path.
- **Minor (Nice To Have)**: defense-in-depth opportunity, hardening suggestion, naming
  clarity for a security-relevant identifier.

### Result

- **Ready to merge: Yes** — no Critical or Important findings remain.
- **Ready to merge: With fixes** — Critical / Important findings the implementer can fix;
  reviewer re-runs after fixes.
- **Ready to merge: No** — fundamental security flaw requires the plan or acceptance to be
  revised.

### Iteration Rule

If the result is **With fixes**, the implementer applies the Critical / Important findings
and the same review re-runs on the changed diff. Stop after **two cycles** — escalate to
the user. See `using-bb-harness` Review Iteration Pattern.

### Trigger Source

This review is normally dispatched as a follow-on from `code-quality-review` when a
security-sensitive surface is touched. It can also be called directly when a planned slice
is known to be security-heavy from the outset.

For substantial reviews, save the record in
`docs/reviews/YYYY-MM-DD-<topic>-security-review.md`.
