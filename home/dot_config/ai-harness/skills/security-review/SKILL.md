---
name: security-review
description: Use when reviewing auth, permissions, secrets, crypto, deletion, destructive operations, sensitive data, external integrations, or data-loss risk.
---

# Security Review

Review security-sensitive work with evidence from code, config, docs, verification. Do not
rely on intent alone.

## Triggers

Work touches:

- authentication, authorization, sessions, tokens, credentials
- secrets, `.env`, private keys, logging, telemetry
- crypto, hashing, signing, key management
- deletion, destructive commands, backups, restore, import, export, data retention
- external integrations, webhooks, sync, concurrency, permissions, sensitive data exposure
- untrusted input, validation, injection, path traversal, command construction,
  parser/deserialization, SSRF, open redirects, file uploads
- new or replaced dependencies in auth/payment/crypto/network-protocol/native-code paths
  (audit output, supply-chain reputation, post-install scripts)

## Checks

- Trust boundaries and validation points are explicit.
- Sensitive data not printed, logged, committed, or exposed in errors.
- Authorization checks happen at the correct boundary.
- Destructive operations require explicit user or product-level approval.
- Crypto and secret handling follow project docs or primary-source guidance.
- Tests or manual checks cover denial, invalid input, failure behavior when practical.
- `docs/SECURITY_MODEL.md` updated when durable security behavior changes.

## Output

Lead with findings, ordered by severity.

### Severity

- **Critical (Must Fix)**: exploitable vulnerability, secret leakage, auth bypass, data loss
  risk, destructive operation without approval, crypto / key handling defect.
- **Important (Should Fix)**: weak validation, missing authorization at right boundary,
  sensitive data in logs / errors / telemetry, missing denial/failure test for a
  security-relevant path.
- **Minor (Nice To Have)**: defense-in-depth opportunity, hardening suggestion, naming
  clarity for a security-relevant identifier.

### Result

- **Ready to merge: Yes** — no Critical or Important findings remain.
- **Ready to merge: With fixes** — Critical/Important findings the implementer can fix;
  reviewer re-runs after fixes.
- **Ready to merge: No** — fundamental security flaw requires plan or acceptance revision.

### Iteration Rule

**With fixes** → implementer applies Critical/Important findings, same review re-runs on
changed diff. Stop after **two cycles** — escalate to user. See `using-bb-harness` Review
Iteration Pattern.

### Trigger Source

Normally a follow-on from `code-quality-review` when a security-sensitive surface is touched.
May be called directly when a planned slice is security-heavy from the outset.

Save substantial records in `docs/reviews/YYYY-MM-DD-<topic>-security-review.md`.
