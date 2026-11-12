---
name: api
title: API / service
kind: solution
origin: built-in
version: 1.0
owner: BA practice
status: active
---

# Profile: API / service

## 1. Signals
An interface other software calls: REST/GraphQL/gRPC endpoints, partner APIs, internal services, SDKs. No human UI.

## 2. Stage plan
| Stage | Plan |
|-------|------|
| Model | Run — domain model and resource states are central; flows become sequence diagrams |
| Stories | Run — **consumer stories** |
| UX | **Skip** (N/A — no human UI). Developer experience is covered in Spec |
| Spec | Run — + API contract |
| Handoff | Run — + API consumer guide |

## 3. Extra gap questions
- Who are the consumers (internal apps, partners, public)? How many, and what do they do with the data?
- Operations needed per resource (create, read, list, update, delete, custom actions)?
- Authentication & authorisation (API key, OAuth scopes, mTLS)? Per-consumer data visibility?
- Rate limits and quotas per consumer? What happens when exceeded?
- Versioning and deprecation policy? Backward-compatibility promise?
- Idempotency for writes? Retries? Pagination style? Filtering/sorting?
- Error format and codes consumers rely on?
- Expected volume, peak, payload size, latency target?
- Sandbox / test environment for consumers? Documentation format?

## 4. Model
Domain model (resources and relationships), resource state machines, **sequence diagrams** (Mermaid `sequenceDiagram`)
for each main interaction, permissions as consumer/scope × operation.

## 5. Stories
Consumer stories: "As a <consumer system/partner developer>, I want to <operation>, so that <business outcome>."
AC in Gherkin with request/response examples:
`Given a valid token with scope orders:read When GET /orders/123 Then 200 with body {…}`.
Include AC for 400/401/403/404/409/422/429/5xx as relevant.

## 6. UX
N/A. Record "UX: N/A — API only" in `_status.md`.

## 7. Spec sections to add
```markdown
## API contract
| Operation | Method & path | Purpose | Auth / scope | Request (fields → dictionary) | Response | Errors | Idempotent | Rate limit |
|-----------|---------------|---------|--------------|-------------------------------|----------|--------|-----------|-----------|

### Conventions
- Error format:
- Pagination:
- Filtering / sorting:
- Versioning & deprecation:
- Date/time & currency formats:

### Examples
<request/response pairs per operation, using AC example values>
```
Optional: draft `api/openapi.yaml` generated from the contract (mark as *draft for engineering review*).

## 8. NFR focus
Performance (latency p95/p99, throughput), Availability (SLA), Security (authN/Z, input validation, OWASP API Top 10),
Scalability, Observability (request logging, tracing), Rate limiting, Backward compatibility.

## 9. Handoff extras
`api-consumer-guide.md`: purpose, onboarding/auth, operations with examples, errors, limits, versioning, support contact.
Contract tests (per operation and error code) in `qa-pack.md`. No `design-brief.md`.

## 10. Review checks
Every operation has auth, errors, examples; every error code has an AC; versioning policy defined; no field in a
payload missing from the data dictionary.

## 11. Extra stages
None.
