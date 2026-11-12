---
name: batch
title: Batch / scheduled process
kind: solution
origin: built-in
version: 1.0
owner: BA practice
status: active
---

# Profile: Batch / scheduled process

## 1. Signals
Unattended processing: nightly jobs, end-of-day/month runs, bulk file processing, scheduled notifications, clean-up/archiving.

## 2. Stage plan
| Stage | Plan |
|-------|------|
| Model | Run — job flow (steps, checkpoints) and record-level states |
| Stories | Run — **job stories** + operator stories |
| UX | Skip unless operators need a job console/report screen (then partial) |
| Spec | Run — + job specification |
| Handoff | Run — + ops runbook |

## 3. Extra gap questions
- Schedule (cron-style, calendar, business days, time zone)? Or event-triggered?
- Inputs: source, format, expected volume, arrival time? What if input is late, empty or malformed?
- Selection criteria — exactly which records are processed?
- Processing window and dependency on other jobs (must run after/before)?
- Record-level failure: skip and continue, or stop the whole run? Threshold for aborting?
- Restartability: resume from checkpoint or rerun from start? Is a rerun safe (idempotent)?
- Outputs: files, records, notifications — to whom, where, format?
- Manual triggering / re-run by whom? Back-dated runs?
- Run report: what totals, who receives it?

## 4. Model
Job flow (Mermaid `flowchart`: read → validate → process → write → report), record states
(pending, processed, failed, skipped), job states (scheduled, running, succeeded, failed, partially succeeded).

## 5. Stories
Job stories: "When <trigger/schedule>, the system must <process> for <selection>, so that <outcome>."
AC cover: normal run, empty input, malformed records, partial failure, rerun, late input, overlapping runs.

## 6. UX
Usually N/A. Partial `/ba-ux` only for operator console or run report layouts.

## 7. Spec sections to add
```markdown
## Job specification — <Job name>
| Topic | Requirement |
|-------|-------------|
| Trigger / schedule / time zone | |
| Dependencies (before/after) | |
| Input source, format, volume | |
| Selection criteria | |
| Processing steps (→ BR-) | |
| Record-level error handling | |
| Abort threshold | |
| Checkpoint / restart / rerun safety | |
| Outputs & recipients | |
| Run report contents | |
| Max duration / processing window | |
| Manual trigger permissions | |
```

## 8. NFR focus
Throughput and processing window, Reliability (restartability, idempotency), Observability (run logs, alerts), Audit, Data retention.

## 9. Handoff extras
`ops-runbook.md`: schedule, dependencies, monitoring, alert meanings, restart/rerun procedure, escalation contacts.
Volume, rerun and failure scenarios in `qa-pack.md`.

## 10. Review checks
Rerun safety stated; every failure mode has behaviour + alert; schedule includes time zone; volumes and window quantified.

## 11. Extra stages
None.
