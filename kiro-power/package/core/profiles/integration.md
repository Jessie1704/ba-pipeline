---
name: integration
title: Integration
kind: solution
origin: built-in
version: 1.0
owner: BA practice
status: active
---

# Profile: Integration

## 1. Signals
Connecting existing systems or vendors: sync data, send events, exchange files, call third-party APIs, middleware/iPaaS.

## 2. Stage plan
| Stage | Plan |
|-------|------|
| Model | Run — context diagram + sequence diagrams + data flow are central |
| Stories | Run — **system/event stories** plus operator stories for failure handling |
| UX | Skip unless there's a monitoring/reconciliation screen (then partial) |
| Spec | Run — + interface specification and field mapping |
| Handoff | Run — + ops runbook |

## 3. Extra gap questions
- Systems involved, owners, and which is the **source of truth** for each data item?
- Direction, trigger (event, schedule, on demand) and frequency? Real-time or eventual?
- Transport (API, message queue, file/SFTP, database link)? Formats?
- Field-by-field mapping — transformations, lookups, defaults, unmapped fields?
- Duplicates and ordering — how are they detected and handled? Idempotency key?
- Failure: timeout, retry count/backoff, dead-letter, who is alerted, how is it fixed and replayed?
- Partial success — what if 3 of 100 records fail?
- Reconciliation — how do we prove both sides match?
- Vendor constraints: rate limits, maintenance windows, test environment, contract/SLA?
- Initial load / backfill of historical data?

## 4. Model
**Context diagram** (systems and data flows), sequence diagrams per interaction, data ownership table.

## 5. Stories
"As <operations / receiving process>, I need <data/event> from <system> within <time>, so that <outcome>."
Add stories for: initial load, reconciliation, error queue handling, replay.

## 6. UX
Usually N/A. If ops need an error queue or reconciliation screen → partial `/ba-ux` for those screens only.

## 7. Spec sections to add
```markdown
## Interface specification
| Interface ID | Source → Target | Trigger / frequency | Transport & format | Volume | Ordering & idempotency | Owner |
|--------------|-----------------|---------------------|--------------------|--------|------------------------|-------|

### Field mapping — <Interface ID>
| Source field | Target field | Transformation / lookup | Default | Required | Rule |
|--------------|-------------|-------------------------|---------|----------|------|

### Error handling
| Failure | Detection | Retry policy | After retries exhausted | Alert (who, how) | Recovery / replay |
|---------|-----------|--------------|-------------------------|------------------|-------------------|

### Reconciliation
| Check | Frequency | Method | Tolerance | Action on mismatch |
|-------|-----------|--------|-----------|--------------------|
```

## 8. NFR focus
Latency/freshness, Throughput, Availability & dependency SLAs, Reliability (no data loss), Security (credentials, encryption in transit), Observability & alerting, Audit.

## 9. Handoff extras
`ops-runbook.md`: what runs, how to monitor, alerts and their meaning, common failures and fixes, replay steps, contacts per system.
Mapping and failure-injection tests in `qa-pack.md`.

## 10. Review checks
Every mapped field exists in both systems' dictionaries; every failure has detection + recovery; source of truth defined for every shared entity.

## 11. Extra stages
None.
