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

Lead with findings and classify risk:

- blocks implementation
- blocks shipping
- acceptable with documented risk
- follow-up only

For substantial reviews, save the record in `docs/reviews/YYYY-MM-DD-<topic>-security-review.md`.
