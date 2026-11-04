# Public Security Guide

Author: Prosenjit Banerjee <prosenjit.banerjee@gmail.com>

## Runtime guardrails

### Input guard

`security/input_guard.py` rejects empty input and known instruction-injection
patterns before orchestration.

### Output guard

`security/output_guard.py` blocks restricted keys such as passwords and API
keys from crossing the response boundary.

### Evidence policy

The Evidence Validator reports uncertainty and requests human review when a
requested entity, action, exclusion, or right is not supported by available
annotations. This public implementation does not constitute a legal rights
clearance system.

## Traceability

Every HTTP response receives an `X-Trace-ID`. Structured logging and
Prometheus metrics support local diagnosis without publishing media.

## Repository security

`scripts/check_publish_safety.py` inspects the Git index and fails when it
finds:

- datasets, media, archives, embeddings, or model artifacts;
- files larger than 10 MiB;
- `CLAUDE.md` or any path declared local-only;
- private research, ingestion, evaluation, or operational modules.

The same check runs from the versioned pre-push hook. Ignored local files remain
on the author's machine but are absent from clones and GitHub downloads.

## Deployment boundary

The API currently runs on localhost and will be externally exposed soon.
External exposure requires authentication, TLS, rate limiting, access policy,
durable audit events, secret management, and deployment-specific threat
modelling. These controls are not represented as complete in the public build.

