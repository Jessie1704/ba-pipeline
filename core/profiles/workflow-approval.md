---
name: workflow-approval
title: Workflow, approvals & case management
kind: solution
origin: catalogue
version: 1.1
owner: BA practice
status: active
---

# Profile: Workflow, approvals & case management

## 1. Signals
Requests that move between people: submit, review, approve, reject, return for changes, escalate, assign,
reassign, delegate, queue, inbox, SLA, deadline, case, ticket, claim, application, onboarding request.

**Not this profile when:** the flow is fully automated with no human decisions (→ `batch` or `integration`),
or it's a single-step form with no review (→ `web-app` / `mobile-app` alone).

## 2. Stage plan
| Stage | Plan | Notes |
|-------|------|-------|
| Model | Run | **State machine is the centrepiece**; swimlane flow per request type; SLA clock events |
| Stories | Run | Stories per role and per transition; supervisor/admin stories mandatory |
| UX | Run | Inbox/work queue, request detail with history, action dialogs (approve/reject with reason) |
| Spec | Run | + routing, approval matrix, SLA & escalation, delegation, queues |
| Review | Run | |
| Handoff | Run | + supervisor guide |

## 3. Extra gap questions
- **Business calendar for every SLA and deadline:** which days count (Mon–Fri?), whose public holidays
  (country/region), which time zone, and is the clock counted in business hours or business days?
  (Never assume — a single holiday shifts every date in the acceptance criteria.)
- Is the threshold measured on the amount **claimed/requested** or the amount **after caps/adjustments**?
- Who approves when the normal approver is **missing** (no manager on record, vacant role, approver's own request)?
- After **escalation**, may the escalation target decide, or only chase? Does the original approver keep rights?
- Request types — one workflow or several? What differs between them?
- Approval levels: who approves what, based on which attributes (amount, category, region, risk)?
- Sequential or parallel approvals? All must approve, or any one? What if approvers disagree?
- Can a requester approve their own request? Segregation of duties rules?
- Delegation and out-of-office: who acts when an approver is away? Is delegation automatic or manual?
- Return for changes: does the request restart from the first step, or resume where it stopped?
- SLA per step: when does the clock **start, pause, resume, stop**? Business hours, time zones, holidays?
- Escalation: after how long, to whom, how many levels? Is the original approver still able to act?
- Assignment: to a person, a team queue, round-robin, by skill, by workload? Can items be claimed/unclaimed?
- Can a request be withdrawn, cancelled, reopened? By whom, in which states?
- What is shown in the history/audit trail, and who can see comments?
- Bulk actions for approvers? Mobile approval? Approval by e-mail reply?
- Volume: requests per day, peak periods, typical queue size per approver?

## 4. Model
- **State machine** per request type (Mermaid `stateDiagram-v2`) incl. Draft, Submitted, In review (per level),
  Returned, Approved, Rejected, Withdrawn, Cancelled, Escalated, Closed, Reopened — keep only what applies.
- Transition table: from → to, trigger, actor, guard rule (`BR-`), SLA effect (start/pause/stop), notification.
- Swimlane flowchart per request type (requester, approvers by level, system, supervisor).
- Permissions matrix: role × action × state (e.g. "Approver L2 — Approve — only in *In review L2*").

## 5. Stories
Standard user stories, derived from **every transition** in the transition table plus:
supervisor (monitor queues, reassign, override), admin (configure thresholds, approvers, SLAs),
requester (track status, withdraw), and system (escalate, remind, auto-close).
AC include time-based scenarios: `Given a request submitted on Friday 17:00 And SLA is 2 business days When … Then escalates on Tuesday 17:00`.

## 6. UX
Run — focus: inbox/work queue (columns, filters, sort, SLA indicators), request detail with timeline/history,
action dialogs (mandatory reason on reject/return), bulk actions, delegation settings, supervisor dashboard.

## 7. Spec sections to add
```markdown
## Request types
| Type | Description | Workflow variant | Volume / day | Owner |
|------|-------------|------------------|--------------|-------|

## Approval matrix
| Request type | Condition (amount / category / region…) | Level 1 | Level 2 | Level 3 | Mode (sequential / parallel / any-one) |
|--------------|------------------------------------------|---------|---------|---------|---------------------------------------|

## Routing & assignment rules
| Rule ID | When | Assign to (person / queue / role) | Method (direct / round-robin / skill / workload) | Fallback |
|---------|------|-----------------------------------|-----------------------------------------------|----------|

## SLA & escalation
| Step / state | SLA | Calendar (business hours, TZ, holidays) | Clock starts | Pauses on | Stops on | Reminder at | Escalate at → to whom |
|--------------|-----|------------------------------------------|--------------|-----------|----------|-------------|-----------------------|

## Delegation & absence
| Topic | Rule |
|-------|------|
| Who can delegate, to whom | |
| Manual / automatic (out-of-office) | |
| Scope (all / per request type / amount limit) | |
| Audit of delegated actions | |

## Segregation of duties
| Rule | Enforcement | Exception process |
|------|-------------|-------------------|

## Work queues
| Queue | Contains | Visible to | Default sort | Columns | Bulk actions |
|-------|----------|------------|--------------|---------|--------------|

## Audit trail
| Event | Data captured (who, when, from/to state, comment, delegated-by) | Visible to | Retention |
|-------|------------------------------------------------------------------|------------|-----------|
```

## 8. NFR focus
Audit (mandatory, tamper-evident), Security (authorisation per state, segregation of duties), Usability
(approver throughput), Performance (inbox load with large queues), Availability, Notifications reliability.

## 9. Handoff extras
- `supervisor-guide.md` — for team leads/operations: queues and what they mean, SLA indicators, how to
  reassign/escalate/override, delegation setup, common situations and how to resolve them, reports available.
- `agent-brief.md` — add the transition table, approval matrix, SLA rules and calendar logic as testable rules.
- `qa-pack.md` — add a **state-transition test matrix** (every valid and invalid transition per role) and
  **time-travel scenarios** for SLAs, reminders and escalations (incl. weekends, holidays, time zones).

## 10. Review checks
- Every state has at least one exit (except terminal states); no unreachable states.
- Every transition has an actor, guard, SLA effect and notification decision.
- Every SLA defines start, pause, stop and calendar.
- Every approval path has a fallback approver (absence, vacancy, conflict of interest).
- Segregation of duties stated (self-approval allowed or not).
- Invalid transitions have AC (e.g. approving an already-withdrawn request).

## 11. Extra stages
None.

---
Changelog: 1.0 — installed from catalogue.
1.1 — pilot (expense-claims): added business-calendar, threshold-basis, missing-approver and escalation-powers questions.
